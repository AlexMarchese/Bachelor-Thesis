

### importing required libraries
import os
from PyPDF2 import PdfReader, PdfWriter



file_path = os.path.dirname(__file__) 


for report in os.listdir(file_path + "\\original reports"):
    print(report)


    ### process for every single file

    reader = PdfReader(file_path + "\\original reports\\" + report, strict=False)
    
    # finding the page with the "Inhaltsverzeichnis" (table of contents)
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
            # print(page_ihv)
            break


    

    ## getting the content of the "Inhaltsverzeichnis" page
    content_ihv = reader.pages[page_ihv].extract_text()


    ##### this is needed to fix a buf encountered for Bern: the page on which the IHV (table of contents) is, is not always the same. 
    ##### Therefore, when assessing the difference between the displayed page of the IHV (on the report) and the actual one measured here via code,
    ##### the difference cannot be hardcoded -> we need to also get the value of the page displayed on the IHV (on the report itself). We do not change that 
    ##### for the other municipalities, as this page value, might not always be displayed in the same position
    
    initial_char_IHV = content_ihv[:30]                      # taking the first digit encountered among the first 30 characters of the IHV's page content
    
    page_shown_on_IHV = 0
    for position in range(len(initial_char_IHV)):

        if initial_char_IHV[position].isdigit():
            page_shown_on_IHV = int(initial_char_IHV[position])
            break



    report_type = ""       ### given that there are two types of report [for one (filtered out with the words "Rechnung nach Arten") we then need to filter further, the other type (tried in case of
                           ### an exception, we no longer have to filer out)]

  
    ## getting the right pages
    try:
        content_ihv = content_ihv.split("Rechnung nach Arten")[1]                   ### for Bern, it is ideal to look for "Rechnung nach Arten"
    except:
        content_ihv = content_ihv.split("Sachgruppen")[1].split("Haushalt")[1]      ### if it does not work, filter out for "Sachgruppen" and then "Haushalt"
        report_type = "ignore filter"                                               ### needed to skip the filtering later on

    start = ""
    end = ""

    shortened = ""


    for position in range(len(content_ihv)):
        if content_ihv[position].isdigit():
            # start += content_ihv[position]
            # if not content_ihv[position + 1].isdigit():  ### this code cannot be used here (the issue is that the pages numbers get mixed up with the next numb and sometimes there is no space)
            #     break
            start += content_ihv[position : position + 2]   ### knowing that we are dealing with 2 digit numbers, it automatically takes the digit and the next one -> need to apply the logic also to the end value
            break
        
        shortened += content_ihv[position] 

    
    
    remainder = content_ihv.split(start)[1] 

    for position in range(len(remainder)):
        # if remainder[position].isdigit():              ### as before the code cannot be used  (the issue is that the pages numbers get mixed up with the next numb and sometimes there is no space)
            # end += remainder[position]                     
            # if not remainder[position + 1].isdigit():
            #     break
        
        if remainder[position : position + 2].isdigit():
            end += remainder[position : position + 2]     ### knowing that we are dealing with 2 digit numbers, we need to take the first 2 digit number (not 2. smth)
            break

 
    # start = int(start) + page_ihv - 1              ##### this code needs to be adapted for Bern (-> taking out the hardcoded values)
    # end = int(end) + page_ihv - 2
    start = int(start) + page_ihv - page_shown_on_IHV       
    end = int(end) + page_ihv - page_shown_on_IHV - 1 ##### -1 at the end, because the end value we get is the page number of the following  
                                                      ##### content (not of interest to us), therefore we need to end at one page before



    writer = PdfWriter()

    export = open(file_path + "\\reduced reports\\reduced " + report, 'wb')


    ## exporting the pages needed
    for page in range(start, end + 1):

        content = reader.pages[page].extract_text()
        
                                                        
                                                        ### to ignore empty / semiempty pages, exclude where "Sonderrechnungen (konsolidiert)" and the page containing the word "Jahresbericht" or still keep reports where report_type = "ignore filter"
        if len(content) > 100 and "Rechnung: " not in content and "Jahresbericht" not in content and "Sonderrechnungen (konsolidiert)" not in content or report_type == "ignore filter":                                        
            writer.add_page(reader.pages[page])

    writer.write(export)
    export.close() 
 