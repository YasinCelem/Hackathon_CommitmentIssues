#imports
import PyPDF2
import openai
import os
from dotenv import load_dotenv
_ = load_dotenv()


client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://fj7qg3jbr3.execute-api.eu-west-1.amazonaws.com/v1"
)


#functions

#takes as input a file (either pdf or text file?)
#returns (text)
# * key fields
# * deadlines & obligations
# * EFFECT: save key fields and deadlines & obligations to the database
def document_analyzer(file_to_analyze):
    text = read_text(file_to_analyze)   # ← this converts the PDF to UTF-8 text

    prompt = f"""
    You are a precise secretary/financial & logistical assistant.
    Extract key personal details (tenant), deadlines present in the document, 
    and a concise factual explanation. Be literal; do not guess—use null for missing values.
    Dates must be YYYY-MM-DD (assume Europe/Amsterdam if needed). 
    Emails are plain strings (no mailto:). Output exactly the template below,
    inside one fenced code block, and nothing else.

    Key personal details:
    {{
    "name": null,
    "id": null,
    "current_address": null,
    "email": null
    }}

    Deadlines: []
    Natural Language Explanation: <120 words max. Factual, plain language, no legal advice.>

    Rules:
    - If a field is missing, set scalars to null and lists to [].
    - If there are multiple tenants, list only the primary tenant (first named).
    - For recurring items (e.g., rent due monthly), use "day N each month" or "after day N each month".
    - Do not include any content outside the single code block.

    The provided document is:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes legal documents."},
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
            print("\n".join(pages))
            return "\n".join(pages) # i need this to be utf-8
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
    pass


# create a reminder depending on the kind of file edited
def create_reminder():
    pass

# send reminder
def send_reminder():
    pass


