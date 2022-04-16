#!/usr/bin/env python3
# coding: utf-8

import re
import pandas as pd
import warnings
from datetime import date
from datetime import datetime
import os
from timeis import timeis, yellow, red, blue, white, green, line

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

today = date.today()
date = today.strftime("%d")

print(f"{timeis()} {yellow}compound families generator") 
print(f"{timeis()} {line}")

def setup_dpd_df():
	print(f"{timeis()} {green}setting up dpd dataframe")
	global dpd_df
	global dpd_df_length
	dpd_df = pd.read_csv ("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df = dpd_df.fillna("")
	dpd_df['Pāli3'] = dpd_df['Pāli1'].str.replace(" \d*$", "")
	test1 = dpd_df["Meaning IN CONTEXT"] != ""
	dpd_df = dpd_df.loc[test1, ["Pāli1", "POS", "Meaning IN CONTEXT", "Construction", "Family2", "Pāli3"]]
	dpd_df = dpd_df.reset_index()
	# print(dpd_df)
	dpd_df_length = len(dpd_df)

def extract_compound_family_names():
	print(f"{timeis()} {green}extracting compound family names")
	global compound_family_set 

	family2_string = ""

	for row in range(dpd_df_length):
		family2 = dpd_df.loc[row, "Family2"]
		family2_string += family2 + " "
	
	compound_family_set = sorted(set(family2_string.split(" ")))
	compound_family_set.remove("")
	# print(compound_family_set)

	if "+" in compound_family_set:
		compound_family_set.remove("+")
		print(f"{timeis()} {red}please remove +'s from family2")


def generate_compound_families_html():
	print(f"{timeis()} {green}generating compound family html")

	anki_html = ""
	counter = 0

	for family in compound_family_set:

		if counter % 500 == 0:
			print(f"{timeis()} {counter}/{len(compound_family_set)}\t{family}")
		
		family_clean = re.sub("/d", "", family)
		test1 = dpd_df["Family2"].str.contains(rf"(^|\s){family}(\s|$)")
		test2 = dpd_df["Pāli3"] != family_clean
		family_df = dpd_df.loc[test1 & test2, ["Pāli1", "POS", "Meaning IN CONTEXT"]]
		family_df = family_df.set_index("Pāli1")
		family_df.index.name = None
		
		family_html = family_df.to_html(escape=False, header = None, index = True)
		family_html = re.sub ('table border="1" class="dataframe"', 'table class="table1"', family_html)
		with open(f"output/family/{family}.html", "w") as f:
			f.write(family_html)
		
		anki_html += f"<b>{family}</b>\t"
		anki_family_html = family_df.to_html(escape=False, header = None, index = True)
		anki_family_html = re.sub(f"\n", "", anki_family_html)
		anki_html += anki_family_html
		anki_html += f"\t{date}\n"
		
		counter += 1
	
	anki_html = re.sub ('table border="1" class="dataframe"', 'table', anki_html)

	with open("../csvs for anki/compound families_test.csv", "w") as anki_file:
		anki_file.write(anki_html)

def delete_unused_family_files():
	print(f"{timeis()} {green}deleting unused family files")
	
	for root, dirs, files in os.walk("output/family/", topdown=True):
		for file in files:
			try:
				file_clean = re.sub(".html", "", file)
				if file_clean not in compound_family_set:
					os.remove(f"output/family/{file_clean}.html")
					print(f"{timeis()} {file}")
			except:
				print(f"{timeis()} {red}{file} not found")
		
setup_dpd_df()
extract_compound_family_names()
generate_compound_families_html()
delete_unused_family_files()

print(f"{timeis()} {line}")