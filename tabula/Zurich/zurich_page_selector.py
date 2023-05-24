

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

    report_type = ""       ### given that there are two types of report (for one we need 2 pages meaning two entries from the IHV as Aufwand and Ertrag are on different pages, for the other only one)
 
    try:
        content_ihv = content_ihv.split("Aufwand")[1]   ### word taken is "Aufwand", if it is not found (meaning it was a changed invoice, it looks for another word)
        report_type = "split"

    except:
        content_ihv = content_ihv.split("Erfolgsrechnung")[1].split("Gesamthaushalt")[1] #  first for "Erfolgsrechnung", then for "Gesamthaushalt"
        report_type = "together"

    start = ""
    end = ""

    shortened = ""


    # print(content_ihv)

    for position in range(len(content_ihv)):
        if content_ihv[position].isdigit():
            # start += content_ihv[position]
            # if not content_ihv[position + 1].isdigit():  ### this code cannot be used here (the issue is that the pages numbers get mixed up with the next numb and sometimes there is no space)
            #     break
            start += content_ihv[position : position + 2]   ### knowing that we are dealing with 2 digit numbers, it automatically takes the digit and the next one -> need to apply the logic also to the end value
            break
        
        shortened += content_ihv[position] 

    

    # if "Ertrag" and "lle" not in shortened:       ### does not make sense here
    #     raise Exception("Parsing error")

    remainder = content_ihv.split(start)[1] 

    for position in range(len(remainder)):
        # if remainder[position].isdigit():              ### as before the code cannot be used  (the issue is that the pages numbers get mixed up with the next numb and sometimes there is no space)
            # end += remainder[position]                     
            # if not remainder[position + 1].isdigit():
            #     break
        
        if remainder[position : position + 2].isdigit():
            end += remainder[position : position + 2]     ### knowing that we are dealing with 2 digit numbers, we need to take the first 2 digit number (not 2. smth)
            break
    
    # print(start, end)   #############
    # print(page_ihv)     ###############

    start = int(start) + page_ihv - 1

    if report_type == "split":
        end = int(end) + page_ihv - 1
    else:
        end = int(end) + page_ihv - 2

    # print(start, end)   ##################
    print("\n")

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