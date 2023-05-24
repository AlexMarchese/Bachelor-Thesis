
### importing required libraries

import os
from tabula import read_pdf
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
import numpy as np




file_path = os.path.dirname(__file__) 

for report in os.listdir(file_path + "\\reduced reports"):

                                                                  ### this code is needed to skip the reports that cannot be read by tabula
    if report == "reduced Rechnung 2022 prov.pdf" or report == "reduced Rechnung 2021.pdf" or report == "reduced Rechnung 2020.pdf" or report == "reduced Rechnung 2019.pdf":        
        # print("skipped", report) 
        continue

    # print("\n")
    print(report)
 
    
    ### process for every single file

    status = "" # used later to skip a part of code (if a report needs to be cropped manually)

    # instantiating a reader object
    reader = PdfReader(file_path + "\\reduced reports\\" + report, "r")

    # base case                                           ### -> ZRH 2010
    (LL_x_base, LL_y_base) = (0, 0)
    (UR_x_base, UR_y_base) = (595, 842)

    # difference from the base case report St. Gallen (reduced 2022 Rechnung). This report was used to determine the cutting coordinates   ### Now it is no longer SG but Zurich, meaning we need to change 
    (LL_x, LL_y) = reader.pages[1].cropbox.lower_left                                                                               ### the hardcoded values (using the zurich report reading.ipynb) for that
    (UR_x, UR_y) = reader.pages[1].cropbox.upper_right

    D_LL_x = round(float(LL_x) - LL_x_base)
    D_LL_y = round(float(LL_y) - LL_y_base)
    D_UR_x = round(float(UR_x) - UR_x_base)
    D_UR_y = round(float(UR_y) - UR_y_base)

    # ratio height / width of the base report (SG 2022)     ### -> ZRH 2010
    base_ratio = round(842 / 595, 2)


    if float(round((UR_y - LL_y) / (UR_x - LL_x), 2)) != base_ratio:
        # raise Exception("Different ratio!")
        print(f'Different ratio! You need to cut it manually. Add the manually correct "{report}" now')
        # inp = "" ##
        inp = "continue"
        while inp != "continue":
            inp = input('Waiting for you to add the file. Type "continue" once you are done / you added the correct file to the folder.\nMessage: ')
        status = "skip"

    elif D_LL_x == D_LL_y == D_UR_x == D_UR_y:
        formula_UR = (537 + D_LL_x, 750 + D_UR_y)    ### -> ZRH 2010, adding in a hardcoded way the values of where to cut
        formula_LL = (73 + D_LL_x, 520 + D_LL_y)

    else:
        factor_x =  float(UR_x) / UR_x_base
        factor_y = float(UR_y) / UR_y_base
        print("PDF is being rescaled. These are the factors:", factor_x, factor_y, "\n")

        formula_UR = (537, 750 * factor_y)
        formula_LL = (73, 520 * factor_y)

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

    ## values of column "Verwaltungsrechnung gesamt" -> hardcoded (as they either got not or badly read)
    missing_col_vals_df_1 = ["30 Personalaufwand", "31 Sachaufwand", "32 Passivzinsen", "33 Abschreibungen", "35 Entschädigungen an Gemeinwesen", "36 Eigene Beiträge", \
                    "37 Durchlaufende Beiträge", "38 Einlagen in Spezialfinanzierungen", "39 Interne Verrechnungen", "Aufwand gesamt"]
    missing_col_vals_df_2 = ["40 Steuern", "41 Regalien Konzessionen", "42 Vermögenserträge", "43 Entgelte", "44 Anteile und Beiträge ohne Zweckb.", "45 Rückerstattungen von Gemeinwesen", \
                         "46 Beiträge für eigene Rechnung", "47 Durchlaufende Beiträge", "48 Entnahmen aus Spezialfinanzierungen", "49 Interne Verrechnungen", "Ertrag gesamt neu"]
    

    year = int(report.split(" ")[-1].split(".")[0])  # this code is needed to retreive the year of the currently processed report

    cols_to_keep = [f"R {str(year - 1)}", f"B {str(year)}", f"ZK {str(year)}", f"R {str(year)}", "Anteil"]

    df_1 = df[0]
    df_2 = df[1]

    df_1 = df_1[cols_to_keep] # keeping only the relevant columns
    df_1 = df_1.dropna(how='all').reset_index(drop=True)
    df_1.insert(0, "Verwaltungsrechnung gesamt", missing_col_vals_df_1)

    df_2.insert(3, f"ZK {year}", np.nan)
    df_2 = df_2[cols_to_keep] # keeping only the relevant columns
    df_2 = df_2.dropna(how='all').reset_index(drop=True)
    df_2.insert(0, "Verwaltungsrechnung gesamt", missing_col_vals_df_2)

    # concatenating the 2 DFs

    df = pd.concat([df_1, df_2])


    # print(df)
            
    df.to_excel(f"combined\\combined {year} ZRH.xlsx")