
### importing required libraries

import os
from tabula import read_pdf
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter




file_path = os.path.dirname(__file__) 

for report in os.listdir(file_path + "\\reduced reports"):
    # print("\n")
    print(report)

    ### process for every single file

    status = "" # used later to skip a part of code (if a report needs to be cropped manually)

    # instantiating a reader object
    reader = PdfReader(file_path + "\\reduced reports\\" + report, "r")

    # base case
    (LL_x_base, LL_y_base) = (0, 0)         ### -> Bern 2005
    (UR_x_base, UR_y_base) = (595.22, 842)

    # difference from the base case report St. Gallen (reduced 2022 Rechnung). This report was used to determine the cutting coordinates ### Now no longer SG but Bern
    (LL_x, LL_y) = reader.pages[1].cropbox.lower_left
    (UR_x, UR_y) = reader.pages[1].cropbox.upper_right

    D_LL_x = round(float(LL_x) - LL_x_base)
    D_LL_y = round(float(LL_y) - LL_y_base)
    D_UR_x = round(float(UR_x) - UR_x_base)
    D_UR_y = round(float(UR_y) - UR_y_base)

    # ratio height / width of the base report (SG 2022)   ### -> Bern 2005
    base_ratio = round(842 / 595.22, 2)


    if float(round((UR_y - LL_y) / (UR_x - LL_x), 2)) != base_ratio:
        # raise Exception("Different ratio!")
        print(f'Different ratio! You need to cut it manually. Add the manually correct "{report}" now')
        # inp = "" ##
        inp = "continue"
        while inp != "continue":
            inp = input('Waiting for you to add the file. Type "continue" once you are done / you added the correct file to the folder.\nMessage: ')
        status = "skip"

    elif D_LL_x == D_LL_y == D_UR_x == D_UR_y:                         ### adding (in a hardcoded way) the values where to cut
        formula_UR = (576 + D_LL_x, 775 + D_UR_y)
        formula_LL = (30 + D_LL_x, 46 + D_LL_y)

    else:
        factor_x =  float(UR_x) / UR_x_base
        factor_y = float(UR_y) / UR_y_base
        print("PDF is being rescaled. These are the factors:", factor_x, factor_y, "\n")

        formula_UR = (576, 775 * factor_y)
        formula_LL = (30, 46 * factor_y)

    # cutting every page of the PDF and saving them alltogehter in the writer object

    if status != "skip":
        writer = PdfWriter()

        for page in range(len(reader.pages)):
            single_page = reader.pages[page]
            single_page.mediabox.upper_right = formula_UR
            single_page.mediabox.lower_left = formula_LL
            writer.add_page(single_page)

        # export = open("2021 SG cropped.pdf", 'wb')
        # writer.write(export)
        # export.close() 

        export = open(file_path + "\\cut reports\\cut " + report, 'wb')
        writer.write(export)
        export.close()

    

    ## reading the cropped PDF with tabula and performing needed data manipultation operations

    df = read_pdf(file_path + "\\cut reports\\cut " + report, pages="all")

    year = int(report.split(" ")[-1].split(".")[0])  # this code is needed to retreive the year of the currently processed report

    columns = [f"Type", f"Rechnung {year}", f"Budget {year}", f"Rechnung {year - 1}"]   # new columns
    

    for single_df in df:
        single_df.iloc[0] = single_df.columns
        try:
            single_df.columns = columns
        except:
            print(f"It did not work with {report}")

    final_df = pd.concat(df)   # concatenating the DFs
    final_df = final_df.reset_index(drop=True)  # resetting the index

    try:
        final_df.to_excel(f"combined\\combined {year} Bern.xlsx")
    except:
        print(f"report {report} had an issue when being exported as PDF")



