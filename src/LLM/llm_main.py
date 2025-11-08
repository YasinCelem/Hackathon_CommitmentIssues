import llm_functions 

def main():
    path = "../test_files/rental_contract_pdf.pdf"
    text = llm_functions.document_analyzer(path)
    print(text)

if __name__ == "__main__":
    main()