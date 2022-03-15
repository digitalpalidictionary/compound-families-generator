#!/usr/bin/env python3
# coding: utf-8

import re
import pandas as pd
import warnings
from datetime import datetime

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

def timeis():
	global blue
	global yellow
	global green
	global red
	global white

	blue = "\033[38;5;33m" #blue
	green = "\033[38;5;34m" #green
	red= "\033[38;5;160m" #red
	yellow = "\033[38;5;220m" #yellow
	white = "\033[38;5;251m" #white
	now = datetime.now()
	current_time = now.strftime("%Y-%m-%d %H:%M:%S")
	return (f"{blue}{current_time}{white}")

print(f"{timeis()} {yellow}compound families generator") 
print(f"{timeis()} ----------------------------------------")

def setup_dpd_df():
	print(f"{timeis()} {green}setting up dpd dataframe")
	global dpd_df
	dpd_df = pd.read_csv ("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df = dpd_df.fillna("") 

def extract_compound_family_names():
	print(f"{timeis()} {green}extracting compound family names")
	global compound_family_df

	test1 = dpd_df["Family2"] != ""
	test2 = dpd_df["Meaning IN CONTEXT"] != ""
	test3 = dpd_df["Pāli Root"] == ""
	test4 = dpd_df["Metadata"] == ""
	filter = test1 & test2 & test3 & test4
	compound_family_df = dpd_df.loc[filter, ["Family2"]]

	#make compound family list
	compound_family_list = []
	compound_family_df["Family2"].str.split()
	compound_family_list = compound_family_df["Family2"].to_list()

	#flatten list
	compound_family_list = [item for sublist in compound_family_list for item in sublist.split(" ")]
	with open ("compound_family_list.csv", "w") as write_list:
		for item in compound_family_list:
			write_list.write(item + "\n")
	
	if "+" in compound_family_list:
		compound_family_list.remove("+")
		print(f"{timeis()} {red}please remove +'s from family2")

	# import compound_family_list as dataframe
	compound_family_df = pd.DataFrame(compound_family_list)
	compound_family_df.drop_duplicates(keep="first", inplace=True)
	compound_family_df.sort_values([0], ascending=True, inplace=True)
	compound_family_df.reset_index(drop=True, inplace=True)

def generate_compound_families_html():
	print(f"{timeis()} {green}generating compound family lists")

	dpd_df['Pāli3'] = dpd_df['Pāli1'].str.replace(" \d*", "")

	test1 = dpd_df["Family2"] != ""
	test2 = dpd_df["Meaning IN CONTEXT"] != ""
	test3 = dpd_df["Pāli Root"] == ""
	test4 = dpd_df["Metadata"] != "yes"
	filter = test1 & test2 & test3 & test4
	df_reduced = dpd_df[filter]

	compound_family_count = compound_family_df.shape[0]

	for row in range (compound_family_count):
		compound_family =  compound_family_df.iloc[row,0]
		compound_family_no_number = re.sub(r"\d", "", compound_family)
		
		test1 = df_reduced["Family2"].str.contains(rf"(^|\s){compound_family}(\s|$)")
		test2 = df_reduced["Pāli3"] != compound_family_no_number
		filter = test1 & test2
		df_filtered = df_reduced.loc[filter, ["Pāli1", "POS", "Meaning IN CONTEXT"]]

		if row % 500 == 0:
			print(f"{timeis()} {row}/{compound_family_count}\t{compound_family}")

		if df_filtered.shape[0] > 0:
			html = ""
			length = df_filtered.shape[0]
			html += f"""<tbody>"""

			for row in range(length):
				cf_pali = df_filtered.iloc[row, 0]
				cf_pos = df_filtered.iloc[row, 1]
				cf_english = df_filtered.iloc[row, 2]
			
				html += f"<tr><th>{cf_pali}</th>"
				html += f"<td>{cf_pos}</td>"
				html += f"<td>{cf_english}</td></tr>"
			html += f"</tbody>"

			with open (f"output/{compound_family}.html", 'w', encoding= "'utf-8") as html_file:
				html_file.write(html)

setup_dpd_df()
extract_compound_family_names()
generate_compound_families_html()

print(f"{timeis()} ----------------------------------------")
