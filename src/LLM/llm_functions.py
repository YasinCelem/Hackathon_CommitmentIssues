import PyPDF2
import openai
import os
import re
import unicodedata
from dotenv import load_dotenv
from textwrap import dedent
import fitz
import json

_ = load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1"
)


# functions
def clean_text(text: str) -> str:
    """Remove control characters and normalize spacing so the gateway doesn't error."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)  # remove control chars
    text = re.sub(r"[ \t\u00A0]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")
    return text.strip()


# takes as input a file (either pdf or text file?)
# returns (text)
# * key fields
# * deadlines & obligations
# * EFFECT: save key fields and deadlines & obligations to the database
def document_analyzer(file_to_analyze):
    text = read_text(file_to_analyze)  # ← this converts the PDF to UTF-8 text

    prompt = prompt = f"""\
    You are a disciplined back-office assistant. Follow the output format EXACTLY. Be literal; do not guess. If a value is missing in the document, return null. Dates must be YYYY-MM-DD (assume Europe/Amsterdam naming if month names appear).

    TASK
    Classify the document into EXACTLY ONE category from the allowed list, generate a storage name, extract the document creation date (date_received), and list all explicit deadlines.

    ALLOWED CATEGORIES (choose ONE, exactly as written)
    - KvK > UBO Register
    - KvK > UBO Extract
    - KvK > Annual Report Filing (SBR)
    - KvK > Self-File Annual Report
    - Contracts > Repository
    - Contracts > Drafts
    - Contracts > Negotiations
    - Contracts > Approvals
    - Contracts > Signatures
    - Contracts > Obligations & Renewals
    - Taxes > VAT Return & Payment
    - Taxes > VAT ICP Report
    - Taxes > VAT OSS (One-Stop Shop)
    - Taxes > VAT KOR
    - Taxes > VAT Article 23 (Import)
    - Taxes > VAT Rates & Exemptions
    - Taxes > VAT / OB Numbers
    - Taxes > VAT Supplement
    - Taxes > Payroll Tax
    - Taxes > Income Tax (IB)
    - Taxes > Corporate Tax (VPB)

    NAMING RULE
    - Produce a concise storage name: "YYYY-MM-DD - <CategoryLeaf> - <IssuerOrParty> - <ShortTitle>"
    - CategoryLeaf = the part after the last ">" (e.g., "Signatures", "VAT Return & Payment").
    - If Issuer/Party not found, use "Unknown".
    - ShortTitle: 2-6 words from the doc (no commas).

    DATE RULES
    - date_received = the document's own issue/creation date, if clearly present. Otherwise null.

    DEADLINES
    - Return a list of triples: [ "<YYYY-MM-DD>", "<what/why>", "<recurrence>" ].
    - <YYYY-MM-DD>: an exact calendar date only (ISO format).
    - <what/why>: brief description of the obligation (e.g., "Monthly rent due", "BTW payment due Q1 2026").
    - <recurrence>: 
    - Use short text like "every month", "every 2 weeks", "every quarter", "every year" when the document clearly states a cadence.
    - Otherwise use null.
    - If the document describes a recurring obligation, include the nearest explicit date for the first element and put the cadence in <recurrence>.
    - Do not use RRULEs or relative expressions (no "REL:+14d", no "day 1 each month" in the date field).
    - If no explicit calendar dates exist, return [].

    OUTPUT
    - Return exactly one fenced code block containing valid JSON and nothing else.

    JSON structure:
    {{
        "category": "<one of the allowed categories>",
        "name": "<YYYY-MM-DD - CategoryLeaf - IssuerOrParty - ShortTitle>",
        "date_received": "YYYY-MM-DD or null",
        "deadlines": [
            ["<YYYY-MM-DD>", "<brief description>", "<recurrence or null>"]
        ]
    }}

    This is the document:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system",
             "content": "You are a disciplined back-office assistant. Follow the output format EXACTLY. Be literal; do not guess. If a value is missing in the document, return null. Dates must be YYYY-MM-DD (assume Europe/Amsterdam naming if month names appear)."},
            {"role": "user", "content": prompt}
        ],
        temperature=1
    )

    return response.choices[0].message.content


def read_text(path: str):
    if path.lower().endswith(".pdf"):
        try:
            pages = []
            with open(path, "rb") as f:
                r = PyPDF2.PdfReader(f)
                for p in r.pages:
                    pages.append(p.extract_text() or "")
            return clean_text("\n".join(pages))  # i need this to be utf-8
        except Exception:
            raise RuntimeError("PDF read failed. ")
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


# form filler (existing)
def fill_in_form(file_to_fill_in):
    text = read_text(file_to_fill_in)
    
    fields_in_the_database = getFieldsFromTheDatabase()
    prompt_to_identify_missing = f'''You are given a document. In this document, some spots are not filled, for example it might have something like: Name: .... or Name: and then nothing. You should identify these, and output a list of them. The answer should be in this format: [field1, field2, field3, ...].
    I am also providing a list of suggested fields: {fields_in_the_database}. If there is a similar thing, you should instead output a suggested field: for example, instead of asking for a "Full Name" ask for "name" if that is a suggested field.
    The document is: {text}'''    
    response_fields_to_fill = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a rigorous and precise assistant."},
            {"role": "user", "content": prompt_to_identify_missing}
        ],
        temperature=1
    )
    fields_to_fill = response_fields_to_fill.choices[0].message.content
    print("LLM1 output: ", fields_to_fill)
    
    s = fields_to_fill.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    fields_textprocessed = [
        f.strip().strip('"').strip("'")
        for f in s.split(",")
        if f.strip()
    ]
    with_database_results = {}
    for field in fields_textprocessed:
        with_database_results[field] = getFromDatabase(field)
    print("after we get the values from database: ", with_database_results)
    
    prompt_to_impute = f'''You are given a document, and a small database (as a json). In this document, some spots are not filled, for example it might have something like: Name: .... or Name: and then nothing. You should identify these, and impute the relevant field from the database.
    I want you to be understanding: if there is a similar thing in the database you should use that. For example if name: xyz is missing in the database, and the document has Full Name: ...., you should still fill in Full Name: xyz.
    However, if any fields have not even a similar field in the database, you should add that in the end, with "FURTHER INFO NEEDED: field1". If there is no such field, just say null.
    The database is {with_database_results}. The document is: {text}.'''    
    response_fields_to_fill = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a rigorous and precise assistant."},
            {"role": "user", "content": prompt_to_impute}
        ],
        temperature=1
    )
    imputed_form = response_fields_to_fill.choices[0].message.content
    print("imputed form: ", imputed_form)
    

def getFromDatabase(field: str):
    fake_db = {
        "student-number": "1234456",
        "status": "unmarried",
        "firstname": "Avery",
        "lastname": "Doe",
        "name_of_account_holder": "Avery Doe",
        "IBAN": "NL1234456787",
        "BIC": "1234AB",
        "date_of_birth": "1990-03-14",
        "address": "123 Maple Street, Utrecht",
        "city_bank": "Utrecht",
        "country_bank": "Netherlands",
        "name_bank": "Revolut",
    }
    return fake_db.get(field)


def getFieldsFromTheDatabase():
    fake_db = {
        "student-number": "1234456",
        "status": "unmarried",
        "firstname": "Avery",
        "lastname": "Doe",
        "name_of_account_holder": "Avery Doe",
        "IBAN": "NL1234456787",
        "BIC": "1234AB",
        "date_of_birth": "1990-03-14",
        "address": "123 Maple Street, Utrecht",
        "city_bank": "Utrecht",
        "country_bank": "Netherlands",
        "name_bank": "Revolut",
    }
    return fake_db


def find_difference(file1, file2):
    text1 = read_text(file1)
    text2 = read_text(file2)

    prompt = f"""\
    You are a contract comparer. Compare FILE_OLD (previous year) vs FILE_NEW (this year).
    Return a SHORT, human-friendly overview of the most important differences.
    {text1}

    NEW:
    {text2}
    """

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a contract comparer."},
            {"role": "user", "content": prompt}
        ],
        temperature=1
    )

    return response.choices[0].message.content


def create_reminder():
    pass


def send_reminder():
    pass

def get_fields_to_fill_pdf(text, db):
    """Use GPT-5 to detect blanks and map them to database fields."""
    prompt = f"""
    You are a smart PDF form filler assistant.
    The document text includes blanks such as 'Name: ____' or 'Email: ____'.
    Detect those blanks and match them with the most relevant database fields.

    Return valid JSON ONLY with key–value pairs for filling.
    Example:
    {{"name": "Avery Doe", "address": "123 Maple Street"}}

    Document text:
    {text}

    Database fields:
    {json.dumps(db, ensure_ascii=False, indent=2)}
    """

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "system", "content": "Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=1
    )

    try:
        return json.loads(response.choices[0].message.content)
    except Exception:
        print("⚠️ GPT JSON parse failed.")
        return {}


def get_pdf_form_fields(pdf_path):
    """Return AcroForm fields if present using PyMuPDF with enhanced detection."""
    try:
        doc = fitz.open(pdf_path)
        fields = {}

        for page_num in range(len(doc)):
            page = doc[page_num]
            widgets = page.widgets()

            if widgets:
                for widget in widgets:
                    # Try multiple ways to get the field name
                    field_name = widget.field_name

                    # Fallback: use field_label if field_name is empty
                    if not field_name:
                        field_name = widget.field_label

                    # Fallback: generate name from position
                    if not field_name:
                        field_name = f"field_{page_num}_{widget.rect.x0}_{widget.rect.y0}"

                    if field_name:
                        fields[field_name] = {
                            'type': widget.field_type,
                            'rect': widget.rect,
                            'page': page_num,
                            'value': widget.field_value
                        }
                        print(f"✅ Found field: {field_name} (type: {widget.field_type})")

        doc.close()

        if not fields:
            print("⚠️ No form fields detected. This may be a static PDF or use a different form technology.")
        else:
            print(f"📋 Total fields found: {len(fields)}")

        return fields
    except Exception as e:
        print(f"⚠️ Field detection error: {e}")
        return {}


def diagnose_pdf_structure(pdf_path):
    """Debug function to inspect PDF structure with enhanced detection."""
    try:
        doc = fitz.open(pdf_path)
        print(f"📄 PDF Pages: {len(doc)}")
        print(f"📄 PDF Metadata: {doc.metadata}")

        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n--- Page {page_num + 1} ---")

            # Fix: convert generator to list
            widgets = list(page.widgets())
            annots = list(page.annots()) if page.annots() else []

            print(f"Widgets: {len(widgets)}")
            print(f"Annotations: {len(annots)}")

            for widget in widgets:
                print(f"  Widget: name='{widget.field_name}', label='{widget.field_label}', type={widget.field_type}")

        doc.close()
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        import traceback
        traceback.print_exc()


def fill_pdf_form(input_pdf, output_pdf, data):
    """Fill a fillable (AcroForm) PDF using PyMuPDF with intelligent field mapping."""
    try:
        doc = fitz.open(input_pdf)

        # First pass: collect field info for GPT mapping
        field_info = {}
        for page_num in range(len(doc)):
            page = doc[page_num]

            for widget in page.widgets():
                field_name = widget.field_name or widget.field_label
                if field_name:
                    rect = widget.rect
                    nearby_text = page.get_text("text", clip=fitz.Rect(
                        rect.x0 - 100, rect.y0 - 20,
                        rect.x0, rect.y1 + 20
                    ))
                    field_info[field_name] = {
                        'context': nearby_text.strip(),
                        'page': page_num  # Store only page number, not widget
                    }

        if not field_info:
            print("⚠️ No fillable fields found")
            doc.close()
            return

        # Use GPT to map fields
        print("🤖 Mapping database fields to PDF form fields...")
        mapping_prompt = f"""
You have a PDF with form fields that have technical IDs, and a database with human-readable field names.
Map each PDF field ID to the most appropriate database field by analyzing the context text near each field.

PDF Fields with context:
{json.dumps({k: v['context'] for k, v in field_info.items()}, indent=2)}

Database fields:
{json.dumps(data, indent=2)}

Return ONLY valid JSON mapping PDF field IDs to database keys:
{{"dhFormfield-XXX": "name", "dhFormfield-YYY": "email", ...}}

If a PDF field has no good match, omit it from the mapping.
"""

        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "Output only valid JSON."},
                {"role": "user", "content": mapping_prompt}
            ],
            temperature=1
        )

        try:
            field_mapping = json.loads(response.choices[0].message.content)
            print(f"📋 Field mapping: {field_mapping}")
        except:
            print("⚠️ Failed to parse field mapping")
            doc.close()
            return

        # Second pass: fill fields using the mapping
        filled_count = 0
        for page_num in range(len(doc)):
            page = doc[page_num]

            for widget in page.widgets():
                field_name = widget.field_name or widget.field_label

                if field_name in field_mapping:
                    db_field_key = field_mapping[field_name]
                    if db_field_key in data:
                        value = data[db_field_key]
                        try:
                            widget.field_value = str(value)
                            widget.update()
                            filled_count += 1
                            print(f"✅ Filled '{field_name}' ({db_field_key}) = '{value}'")
                        except Exception as e:
                            print(f"⚠️ Failed to fill '{field_name}': {e}")

        if filled_count == 0:
            print("⚠️ No fields were filled!")
        else:
            print(f"✅ Successfully filled {filled_count} field(s)")

        doc.save(output_pdf, garbage=4, deflate=True)
        doc.close()
        print(f"💾 PDF saved to {output_pdf}")

    except Exception as e:
        print(f"❌ Fill operation failed: {e}")
        import traceback
        traceback.print_exc()


def fill_in_form_pdf(file_to_fill_in):
    """
    New function: fills an actual PDF (fillable or not)
    using GPT-5 for reasoning + coordinate estimation.
    """
    db = getFieldsFromTheDatabase()
    text = read_text(file_to_fill_in)

    print("🤖 Using GPT-5 to detect and match fields...")
    field_data = get_fields_to_fill_pdf(text, db)
    if not field_data:
        print("⚠️ No fillable fields detected.")
        return None

    output_pdf = "filled_output.pdf"
    form_fields = get_pdf_form_fields(file_to_fill_in)

    if form_fields:
        print("📋 Fillable (AcroForm) PDF detected.")
        fill_pdf_form(file_to_fill_in, output_pdf, field_data)
    else:
        print("⚠️ No fillable fields detected; static PDF filling not implemented yet.")
        return None

    print("✅ PDF form filling complete.")
    return output_pdf
