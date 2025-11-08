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
def fill_in_form(form):
    pass

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


