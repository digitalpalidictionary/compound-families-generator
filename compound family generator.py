#!/usr/bin/env python3
# coding: utf-8

import re
import pandas as pd
import warnings
import os
import json

from datetime import date
from datetime import datetime
from timeis import timeis, yellow, red, blue, white, green, line, tic, toc
from delete_unused_files import del_unused_files
from superscripter import superscripter

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

today = date.today()
date = today.strftime("%d")

print(f"{timeis()} {yellow}compound families generator") 
print(f"{timeis()} {line}")

def setup_dpd_df():
	print(f"{timeis()} {green}setting up dpd dataframe")
	global dpd_df
	dpd_df = pd.read_csv ("../csvs/dpd-full.csv", sep="\t", dtype=str)
	dpd_df = dpd_df.fillna("") 
	return dpd_df

def extract_compound_family_names():
	print(f"{timeis()} {green}extracting compound family names")
	global compound_family_df

	test1 = dpd_df["Family2"] != ""
	test2 = dpd_df["Meaning IN CONTEXT"] != ""
	# test3 = dpd_df["Pāli Root"] == ""
	filter = test1 & test2 # & test3
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
	master_family_list = compound_family_df[0].tolist()
	
	return master_family_list

def generate_compound_families_html():
	print(f"{timeis()} {green}generating compound family html")

	dpd_df['Pāli3'] = dpd_df['Pāli1'].str.replace(" \\d*", "")

	test1 = dpd_df["Family2"] != ""
	test2 = dpd_df["Meaning IN CONTEXT"] != ""
	test3 = dpd_df['Pāli3'].str.len() < 30 # remove all the long words
	filter = test1 & test2 & test3
	df_reduced = dpd_df[filter]

	compound_family_count = compound_family_df.shape[0]

	anki_html = ""
	compound_family_dict = {}
	errors = []

	for row in range(compound_family_count):  # compound_family_count
		compound_family =  compound_family_df.iloc[row,0]
		compound_family_no_number = re.sub(r"\d", "", compound_family)
		
		test1 = df_reduced["Family2"].str.contains(rf"(^|\s){compound_family}(\s|$)")
		test2 = df_reduced["Pāli3"] != compound_family_no_number
		test3 = df_reduced["Pāli Root"] == ""
		filter = test1 & test2 & test3
		df_filtered = df_reduced.loc[filter, ["Pāli1", "POS", "Grammar", "Meaning IN CONTEXT", "Construction", "Word Family"]]

		if row % 500 == 0:
			print(f"{timeis()} {row}/{compound_family_count}\t{compound_family}")

		with open ("../exporter/assets/dpd-words.css", "r") as c:
			css = c.read()

		if df_filtered.shape[0] > 0:
			html = ""
			count = 0
			# html += f"<style>{css}</style>"
			length = df_filtered.shape[0]
			html += f"""<table class="table1"><tbody>"""
			anki_html += f"<b>{compound_family}</b>\t"
			anki_html += f"<table><tbody>"

			for row in range(length):
				cf_pali = df_filtered.iloc[row, 0]
				cf_pali = superscripter(cf_pali)
				cf_pos = df_filtered.iloc[row, 1]
				cf_grammar = df_filtered.iloc[row, 2]
				cf_english = df_filtered.iloc[row, 3]
				cf_constr = df_filtered.iloc[row, 4]
				cf_constr = re.sub (r"<br/>.+", "", cf_constr)
				cf_word_family = df_filtered.iloc[row, 5]

				if re.findall("\\bcomp\\b", cf_grammar) or re.findall("idiom|sandhi", cf_pos):

					html += f"<tr><th>{cf_pali}</th>"
					html += f"<td><b>{cf_pos}</b></td>"
					html += f"<td>{cf_english}</td></tr>"

					anki_html += f"<tr valign='top'><div style='color: #FFB380'><td>{cf_pali}</td><td><div style='color: #FF6600'>{cf_pos}</div></td><td><div style='color: #FFB380'>{cf_english}</td><td><div style='color: #FF6600'>{cf_constr}</div></td></tr>"

					count += 1
				
			if count == 0:
				errors += [compound_family] 

			html += f"</tbody></table>"
			anki_html += f"</tbody></table>"
			anki_html += f"\t{date}\n"

			with open (f"output/{compound_family}.html", 'w', encoding= "'utf-8") as html_file:
				html_file.write(html)
			
			# for external apps
			html_for_json = re.sub("table1", "compound-family", html)
			compound_family_dict[compound_family] = html_for_json

	with open("../csvs for anki/compound families.csv", "w") as anki_file:
		anki_file.write(anki_html)
	
	compound_families_json = json.dumps(compound_family_dict, ensure_ascii=False, indent=4)
	with open ("../dpd-app/data/compound-families.json", "w") as f:
		f.write(compound_families_json)

	print(f"{timeis()} {green}errors {red}{len(errors)}", end= " ")
	for error in errors:
		print(f"{error} ", end=" ")
	print()

	with open("compound family errors.tsv", "w") as f:
		for error in errors:
			f.write(f"{error}\n")


def delete_unused_family_files():
	file_dir = "output/"
	file_ext = ".html"
	del_unused_files(master_family_list, file_dir, file_ext)


tic()
dpd_df = setup_dpd_df()
master_family_list = extract_compound_family_names()
generate_compound_families_html()
delete_unused_family_files()
toc()
