#imports
import PyPDF2
import openai
import os
import re
import unicodedata
from dotenv import load_dotenv
from textwrap import dedent
_ = load_dotenv()


client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1"
)


#functions
def clean_text(text: str) -> str:
    """Remove control characters and normalize spacing so the gateway doesn't error."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)  # remove control chars
    text = re.sub(r"[ \t\u00A0]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")
    return text.strip()

#takes as input a file (either pdf or text file?)
#returns (text)
# * key fields
# * deadlines & obligations
# * EFFECT: save key fields and deadlines & obligations to the database
def document_analyzer(file_to_analyze):
    text = read_text(file_to_analyze)   # ← this converts the PDF to UTF-8 text

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
            {"role": "system", "content": "You are a disciplined back-office assistant. Follow the output format EXACTLY. Be literal; do not guess. If a value is missing in the document, return null. Dates must be YYYY-MM-DD (assume Europe/Amsterdam naming if month names appear)."},
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
            return clean_text("\n".join(pages)) # i need this to be utf-8
        except Exception:
            raise RuntimeError("PDF read failed. ")
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


#form filler
# returns a filled in form
# also returns some text explanation (what exactly was filled,
#   what we are unsure about,
#   what we need more data on)
def fill_in_form(file_to_fill_in):
    text = read_text(file_to_fill_in)
    
    #we first use the LLM + the list of fields we have in the database to identify the fields that are missing.
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
    
    #helper part, text processing
    s = fields_to_fill.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    # split on commas, trim whitespace & optional quotes
    fields_textprocessed = [
        f.strip().strip('"').strip("'")
        for f in s.split(",")
        if f.strip()
    ]
    with_database_results = {}
    for field in fields_textprocessed:
        with_database_results[field] = getFromDatabase(field)
    print("after we get the values from database: ", with_database_results)
    
    #we then use the retrieved data from the database + the original file + the LLM to fill it back in. 
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
    
    #maybe convert this into a PDF file? idk
    #TODO

def getFromDatabase(field: str): #this is just a mockup! add database integration later
    """User-provided function. Example stub."""
    fake_db = {
        "name": "Avery Doe",
        "email": "avery@example.com",
        "address": "123 Maple Street, Utrecht",
        "date_of_birth": "1990-03-14",
        "phone": "+31 6 1234 5678",
    }
    return fake_db.get(field)

def getFieldsFromTheDatabase(): #very much just a mockup...
    """User-provided function. Example stub."""
    fake_db = {
        "name": "Avery Doe",
        "email": "avery@example.com",
        "address": "123 Maple Street, Utrecht",
        "date_of_birth": "1990-03-14",
        "phone": "+31 6 1234 5678",
    }
    return fake_db.keys()

#checks the difference betweeen the files
#returns 
def find_difference(file1, file2):

    text1 = read_text(file1)
    text2 = read_text(file2)

    prompt = prompt = f"""\
    You are a contract comparer. Compare FILE_OLD (previous year) vs FILE_NEW (this year).
    Return a SHORT, human-friendly overview of the most important differences.

    RULES
    - Be precise and neutral. No legal advice.
    - Show only material differences (money, dates, notice/penalties, deposits, insurance, pets, maintenance thresholds, access/entry, utilities, subletting, clauses added/removed).
    - Max 12 bullets. Each bullet ≤ 110 characters.
    - Use tags [HIGH], [MED], [LOW] for likely impact on the tenant.
    - Format as Markdown; no preface, no conclusions, no extra text.
    - Prefer “Old → New” style for clarity.
    - If no differences, output: "_No material differences found._"

    OUTPUT FORMAT (Markdown only)
    - A heading: "### Differences"
    - Then up to 12 bullets, each one line:
    - "<tag> Section/Field: Old → New"
    - Example: "[HIGH] Rent: €1,650 → €1,725"
    - Optionally (only if present), a compact "Added/Removed Clauses" section with up to 3 bullets each.

    This is the initial document:
    {text1}

    and this is the new document:
    {text2}
    """

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a contract comparer. Compare FILE_OLD (previous year) vs FILE_NEW (this year). Return a SHORT, human-friendly overview of the most important differences."},
            {"role": "user", "content": prompt}
        ],
        temperature=1
    )

    return response.choices[0].message.content


# create a reminder depending on the kind of file edited
def create_reminder():
    pass

# send reminder
def send_reminder():
    pass


