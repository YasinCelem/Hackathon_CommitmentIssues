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

    text = read_text(file_to_analyze)

    prompt = (
        f"You are a helpful secretary/financial and logistical assistant. You will go over the provided legal file (such as a rental contract), and you will get the most important information out of it. Specifically, you will pay attention to the following information: key fields (personal information of the parties signing the document) and deadlines and obligations present in the document. You will also explain the key points of the document in natural language. The provided document is: {text}"
    )

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
            return "\n".join(pages)
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


