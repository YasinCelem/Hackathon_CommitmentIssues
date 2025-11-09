import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.BackEnd.app import create_app
import LLM.llm_functions

from pathlib import Path

def latest_pdf(folder: str | Path, recursive: bool = False) -> Path | None:
    folder = Path(folder)
    pattern = "**/*.pdf" if recursive else "*.pdf"
    pdfs = [p for p in folder.glob(pattern) if p.is_file() and p.suffix.lower() == ".pdf"]
    return max(pdfs, key=lambda p: p.stat().st_mtime, default=None)

# Example
path = latest_pdf(r"C:\Users\you\Documents", recursive=False)
if path:
    print("Latest PDF:", path)
else:
    print("No PDFs found.")

def decide_file_type():
    #read latest pddf fropm saved pdfs
    #decide which type of doc it is (what worfklow to run)
    #call it
    
    file_path = latest_pdf("src/gmail_worker/downloads", False)

    text = LLM.llm_functions.read_text(file_path)
    if (LLM.llm_functions.get_fields_to_fill_pdf(text)):
        #if there are fields 
        fill_workflow(file_path)
    else:
        response = LLM.llm_functions.document_analyzer(file_path)
        if ("bill" in response):
            transaction_workflow(file_path)
        else:
            compare_workflow(file_path)

    

def compare_workflow(file_path):
    file_path2 = "test_files/rental_contract_pdf.pdf"
    response1 = LLM.llm_functions.find_difference(file_path, file_path2)
    print(response1)
    # idk with what
    field_notify(pdf)
    send_email(pdf) 
    

def fill_workflow(file_path):
    pdf = LLM.llm_functions.fill_in_form_pdf(file_path)
    field_notify(pdf)
    send_email(pdf) 

def transaction_workflow(file_path):

    field_notify(pdf)
    send_email(pdf) 
    pass

