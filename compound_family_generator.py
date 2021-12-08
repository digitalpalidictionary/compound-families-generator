#!/usr/bin/env python3.10
# coding: utf-8

import re
import logging
import pandas as pd

#setup logger
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%I:%M:%S')

#import dpd csv as dataframe
logging.warning(f"opening dpd.csv as data frame")
csv_file = "/home/bhikkhu/Bodhirasa/Dropbox/dpd/dpd.csv"
df = pd.read_csv (csv_file, sep="\t")

#extract compound_family_list
logging.warning(f"extracting compound_family_list")

test1 = ~df["Family2"].isnull()
test2 = ~df["Meaning IN CONTEXT"].isnull()
test3 = df["Pāli Root"].isnull()
test4 = ~df["Metadata"].isnull() == False
filter = test1 & test2 & test3 & test4
filtered_df = df.loc[filter, ["Family2"]]

#make compound family list
compound_family_list = []
filtered_df["Family2"].str.split()
compound_family_list = filtered_df["Family2"].to_list()
compound_family_list = compound_family_list

#flatten list
compound_family_list = [item for sublist in compound_family_list for item in sublist.split(" ")]

# import compound_family_list as dataframe
compound_family_list = pd.DataFrame(compound_family_list)

#drop dupes and sort
compound_family_list.drop_duplicates(keep="first", inplace=True)
compound_family_list.sort_values([0], ascending=True, inplace=True)
compound_family_list.reset_index(drop=True, inplace=True)

# row count
compound_family_count = compound_family_list.shape[0]
logging.warning(f"compound_family_count = {compound_family_count}")

# writing compound_families.csv
logging.warning ("writing compound_families.csv")
txt_file = open ("compound_families.csv", 'w', encoding= "'utf-8")
logging.warning ("~" *40)
row = 0

for row in range (0, compound_family_count):
    compound_family =  compound_family_list.iloc[row,0]
    if row % 100 == 0:
        logging.warning (f"{row} {compound_family}")
    
    test1 = ~df["Family2"].isnull()
    test2 = df["Family2"].str.contains(rf"\b{compound_family}\b")
    test3 = ~df["Meaning IN CONTEXT"].isnull()
    test4 = df["Pāli Root"].isnull()
    
    filter = test1 & test2 & test3 & test4
    filtered_df = df.loc[filter, ["Pāli1", "POS", "Meaning IN CONTEXT", "Construction"]]

    with open("compound_families.csv", 'a') as txt_file:
        txt_file.write (f"{compound_family}\n")
        txt_file.write (f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
        filtered_df.to_csv(txt_file, header=False, index=False, sep="\t")
        txt_file.write (f"\n")

logging.warning(f"fin")
