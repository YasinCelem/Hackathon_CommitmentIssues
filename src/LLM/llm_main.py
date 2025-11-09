import llm_functions

#if __name__ == "__main__":
#    test_pdf = "template3.pdf"
#    result = llm_functions.fill_in_form_pdf(test_pdf)
#    print("Filled PDF saved as:", result)


def main():
    path = "../test_files/rental_contract_text.txt"
    path2 = "../test_files/slightly_modified_text.txt"
    text = llm_functions.document_analyzer(path)
    print(text)
    print("-----------------------")
    #difference_text = llm_functions.find_difference(path, path2)
    #print(difference_text)

if __name__ == "__main__":
    main()