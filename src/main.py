import sys
from pathlib import Path

from src.FrontEnd.notification_helper import create_compare_notification, create_transaction_notification, \
    create_form_notification

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.BackEnd.app import create_app
import LLM.llm_functions

from pathlib import Path

def latest_pdf(folder: str | Path, recursive: bool = False) -> str | None:
    folder = Path(folder)
    pattern = "**/*.[pP][dD][fF]" if recursive else "*.[pP][dD][fF]"
    pdfs = [p for p in folder.glob(pattern) if p.is_file()]
    latest = max(pdfs, key=lambda p: p.stat().st_mtime, default=None)
    return str(latest) if latest else None



def decide_file_type():
    #read latest pddf fropm saved pdfs
    #decide which type of doc it is (what worfklow to run)
    #call it
    print(1)
    file_path = latest_pdf("src/gmail_worker/downloads", False)
    print(f"Processing file: {file_path}")

    text = LLM.llm_functions.read_text(file_path)
    print(text)
    if LLM.llm_functions.get_fields_to_fill_pdf(text,LLM.llm_functions.getFieldsFromTheDatabase()):
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
    print(f"Comparing {file_path} with {file_path2}")
    response1 = LLM.llm_functions.find_difference(file_path, file_path2)
    create_compare_notification(response1)

def fill_workflow(file_path):
    print("Filling form for file:", file_path)
    pdf = LLM.llm_functions.fill_in_form_pdf(file_path)
    create_form_notification("Form filled successfully.")

def transaction_workflow(file_path):
    print("Processing transaction for file:", file_path)
    create_transaction_notification("Transaction is pending. Confirm to send.")


