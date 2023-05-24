

### importing required libraries
import os
from PyPDF2 import PdfReader, PdfWriter



file_path = os.path.dirname(__file__) 


for report in os.listdir(file_path + "\\original reports"):
    print(report)

    ### process for every single file

    ## reader object
    reader = PdfReader(file_path + "\\original reports\\" + report)

    ## finding the page with the "Inhaltsverzeichnis" (table of contents)
    number_of_pages = len(reader.pages)
    page_ihv = 0

    for page_number in range(number_of_pages):

        page = reader.pages[page_number]

        try:                                     # due to a report (SG 2020) not being read properly, I built in this checking mechanism
            text = page.extract_text()
        except:
            # raise Exception("Parsing error")   
            print(f"PDF '{report}' not read properly") # better to actually skip it and to the rest, in case of issues
            continue

        

        if "Inhaltsverzeichnis" in text:
            page_ihv = page_number
            break




    ## getting the content of the "Inhaltsverzeichnis" page
    content_ihv = reader.pages[page_ihv].extract_text()


    ## getting the right pages
    content_ihv = content_ihv.split("Aufwand")[1]

    start = ""
    end = ""

    shortened = ""
    for position in range(len(content_ihv)):
        if content_ihv[position].isdigit():
            start += content_ihv[position]
            if not content_ihv[position + 1].isdigit():
                break
        
        shortened += content_ihv[position]

    if "Ertrag" and "lle" not in shortened:       
        raise Exception("Parsing error")

    remainder = content_ihv.split(start)[1] 

    for position in range(len(remainder)):
        if remainder[position].isdigit():
            end += remainder[position]
            if not remainder[position + 1].isdigit():
                break
    

    start = int(start) + page_ihv - 1
    end = int(end) + page_ihv - 2



    writer = PdfWriter()

    export = open(file_path + "\\reduced reports\\reduced " + report, 'wb')


    ## exporting the pages needed
    for page in range(start, end + 1):

        content = reader.pages[page].extract_text()

        if len(content) < 150: # to ignore empty / semiempty pages (atapted from 50 to 150)
            continue

        writer.add_page(reader.pages[page])

    writer.write(export)
    export.close() 