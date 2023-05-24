
### importing required libraries

import os
from tabula import read_pdf
# import pandas as pd
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
    (LL_x_base, LL_y_base) = (0, 0)
    (UR_x_base, UR_y_base) = (595.276, 841.89)

    # difference from the base case report St. Gallen (reduced 2022 Rechnung). This report was used to determine the cutting coordinates
    (LL_x, LL_y) = reader.pages[1].cropbox.lower_left
    (UR_x, UR_y) = reader.pages[1].cropbox.upper_right

    D_LL_x = round(float(LL_x) - LL_x_base)
    D_LL_y = round(float(LL_y) - LL_y_base)
    D_UR_x = round(float(UR_x) - UR_x_base)
    D_UR_y = round(float(UR_y) - UR_y_base)

    # ratio height / width of the base report (SG 2022)
    base_ratio = round(841.89 / 595.276, 2)


    if float(round((UR_y - LL_y) / (UR_x - LL_x), 2)) != base_ratio:
        # raise Exception("Different ratio!")
        print(f'Different ratio! You need to cut it manually. Add the manually correct "{report}" now')
        # inp = "" ##
        inp = "continue"
        while inp != "continue":
            inp = input('Waiting for you to add the file. Type "continue" once you are done / you added the correct file to the folder.\nMessage: ')
        status = "skip"

    elif D_LL_x == D_LL_y == D_UR_x == D_UR_y:
        formula_UL = (0 + D_LL_x, 800 + D_UR_y)
        formula_LL = (0 + D_LL_x, 25 + D_LL_y)

    else:
        factor_x =  float(UR_x) / UR_x_base
        factor_y = float(UR_y) / UR_y_base
        print("PDF is being rescaled. These are the factors:", factor_x, factor_y, "\n")

        formula_UL = (0, 800 * factor_y)
        formula_LL = (0, 25 * factor_y)

    # cutting every page of the PDF and saving them alltogehter in the writer object

    if status != "skip":
        writer = PdfWriter()

        for page in range(len(reader.pages)):
            single_page = reader.pages[page]
            single_page.mediabox.upper_left = formula_UL
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



    cleaned_dfs = []

    for single_df in df:

        old_col_names = single_df.columns.to_list()
        new_col_names = []
        for name in old_col_names:
            first_line = " " + str(single_df.loc[0, name])
            if "nan" in first_line: # not copying nan values
                first_line = ""
            elif "AufwandErtrag" in first_line: # renaming "AufwandErtrag" with "Aufwand / Ertrag"
                first_line = " Aufwand / Ertrag"
            new_col_names.append(name + first_line)
        single_df.columns = new_col_names 
        single_df = single_df.iloc[1:, :]  # eliminating the first row
        single_df = single_df.rename({'Unnamed: 0': 'Beschreibung'}, axis=1)

        print(single_df.head())

        single_df = single_df.drop(columns=['Unnamed: 1']) # removing "Unnamed: 1"

        cleaned_dfs.append(single_df)
    
        inp = ""
        while inp != "continue":
            inp = input('write "continue"') 