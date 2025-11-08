import llm_functions 

def main():
    path = "../test_files/test1.txt"
    text = llm_functions.document_analyzer(path)
    print(text)

if __name__ == "__main__":
    main()