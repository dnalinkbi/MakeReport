#!/bin/python

import json
import glob
import os.path
from os import path
import pandas as pd
import warnings
from pandas import json_normalize


warnings.simplefilter(action='ignore', category=FutureWarning)


def data_path(xml):
	with open("%s"%xml['clr'], 'r') as xml:
			path=[]
			files=[]
			for line in xml.readlines():
				if 'reads.bam' in line:
					for i in line.strip().split("="):
						if i.startswith('"/pacbio_ds2') or i.startswith('"/dlst'):
							path = i.split('"')[1]
							if path.endswith(".bam"):
								files.append(path)
			
			file_df = pd.DataFrame()
			for cell, file in enumerate(files):
				cell_number = cell+1
				analysis_folder_path = file.rsplit("/", 1)[0]
				unique_id = file.rsplit("/", 1)[1].rsplit(".", 3)[0]
				subreads_bam = analysis_folder_path + "/" + unique_id + ".subreads.bam"
				subreads_bam_pbi = analysis_folder_path + "/" + unique_id + ".subreads.bam.pbi"
				subreadset_xml = analysis_folder_path + "/" + unique_id + ".subreadset.xml"
				
				file_list = pd.Series([cell_number, analysis_folder_path, unique_id, subreads_bam, subreads_bam_pbi, subreadset_xml])
				file_df = file_df.append(file_list, ignore_index=True)
				#file_df = pd.concat([file_df, file_list], sort=False)
			file_df.columns = ['cell_number', 'analysis_forder_path', 'unique_id', 'bam', 'pbi', 'xml']
	return file_df

#-------------------------------------------------------------------------------------------------------------------

def ccs_data_path(xml):
	with open("%s"%xml['ccs'], 'r') as ccs_xml:
			path=[]
			files=[]
			for line in ccs_xml.readlines():
				if 'reads.bam' in line:
					for i in line.strip().split("="):
						if i.startswith('"/pacbio_ds2') or i.startswith('"/dlst'):
							path = i.split('"')[1]
							if path.endswith(".bam"):
								files.append(path)
			
			ccs_file_df = pd.DataFrame()
			for cell, file in enumerate(files):
				cell_number = cell+1
				analysis_folder_path = file.rsplit("/", 3)[0]
				hifi_fastq = glob.glob(analysis_folder_path + "/call-export_*/*/*fastq.gz")[0]
				hifi_fasta = glob.glob(analysis_folder_path + "/call-export_*/*/*fasta.gz")[0]
				
				file_list = pd.Series([cell_number, analysis_folder_path, hifi_fastq, hifi_fasta])
				ccs_file_df = ccs_file_df.append(file_list, ignore_index=True)
				#ccs_file_df = pd.concat([ccs_file_df, file_list])
			ccs_file_df.columns = ['cell_number', 'analysis_folder_path', 'fastq', 'fasta']
	return ccs_file_df

#-------------------------------------------------------------------------------------------------------------------

def rawdata(xml):
	xml = xml['clr'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'
	with open('%s/raw_data.report.json'%xml) as rawdata_json_file:
		rawdata_json_data = json.load(rawdata_json_file)
		rawdata_dataframe = pd.DataFrame(rawdata_json_data["attributes"])
		rawdata_dataframe = rawdata_dataframe[['name', 'value']]
	return rawdata_dataframe

#-------------------------------------------------------------------------------------------------------------------

def plot(xml):
	xml = xml['clr'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'
	with open('%s/raw_data.report.json'%xml) as rawdata_json_file:
		rawdata_json_data = json.load(rawdata_json_file)
		plot_dataframe = json_normalize(data = rawdata_json_data["plotGroups"], record_path='plots', errors='ignore', record_prefix='_', meta=['caption', 'id', 'image', 'plotType', 'thumbnail', 'title'])
		plot_dataframe = plot_dataframe[['title', '_image']]
		plot_dataframe['path'] = "%s"%xml
		plot_dataframe['fullpath'] = plot_dataframe['path'] + '/' + plot_dataframe['_image']
	return plot_dataframe

#-------------------------------------------------------------------------------------------------------------------

def ccs(xml):
	if xml['cell'] == "1":
		#xml = xml['ccs'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'
		if path.isdir(xml['ccs'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'):
			xml = xml['ccs'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'
		else:
		 	xml = xml['ccs'].rsplit('/', 3)[0] + '/call-pbreports_ccs2/execution/'
	else:
		if path.isdir(xml['ccs'].rsplit('/', 3)[0] + '/call-pbreports_ccs2/execution'):
			xml = xml['ccs'].rsplit('/', 3)[0] + '/call-pbreports_ccs2/execution/'
		else:
			xml = xml['ccs'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution/'
	with open('%s/ccs.report.json'%xml) as ccs_json_file:
		ccs_json_data = json.load(ccs_json_file)
		ccs_dataframe = pd.DataFrame(ccs_json_data["attributes"])
		ccs_dataframe = ccs_dataframe[['name', 'value']]
	return ccs_dataframe

#-------------------------------------------------------------------------------------------------------------------

def ccs_plot(xml):
	#xml = glob.glob(xml['ccs'].rsplit('/', 3)[0] + '/*/execution/ccs.report.json')[0]
	if xml['cell'] == "1":
		#xml = xml['ccs'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'
		if path.isdir(xml['ccs'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'):
			xml = xml['ccs'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'
		else:
			xml = xml['ccs'].rsplit('/', 3)[0] + '/call-pbreports_ccs2/execution/'
	else:
		if path.isdir(xml['ccs'].rsplit('/', 3)[0] + '/call-pbreports_ccs2/execution'):
			xml = xml['ccs'].rsplit('/', 3)[0] + '/call-pbreports_ccs2/execution/'
		else:
			xml = xml['ccs'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution/'
	with open('%s/ccs.report.json'%xml) as ccs_json_file:
		ccs_json_data = json.load(ccs_json_file)
		ccs_plot_dataframe = json_normalize(data = ccs_json_data["plotGroups"], record_path='plots', errors='ignore', record_prefix='_', meta=['caption', 'id', 'image', 'plotType', 'thumbnail', 'title'])
		ccs_plot_dataframe = ccs_plot_dataframe[['title', '_image']]
		ccs_plot_dataframe['path'] = "%s"%xml
		ccs_plot_dataframe['fullpath'] = ccs_plot_dataframe['path'] + '/' + ccs_plot_dataframe['_image']
	return ccs_plot_dataframe

#-------------------------------------------------------------------------------------------------------------------

def loading(xml):
	xml = xml['clr'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'
	with open('%s/loading.report.json'%xml) as loading_json_file:
		loading_json_data = json.load(loading_json_file)
		loading_dataframe = pd.DataFrame(loading_json_data["attributes"])
		loading_dataframe = loading_dataframe[['name', 'value']]
	return loading_dataframe

#-------------------------------------------------------------------------------------------------------------------

def adapter(xml):
	xml = xml['clr'].rsplit('/', 3)[0] + '/call-import_dataset_reports/execution'
	with open('%s/adapter.report.json'%xml) as adapter_json_file:
		adapter_json_data = json.load(adapter_json_file)
		adapter_dataframe = pd.DataFrame(adapter_json_data["attributes"])
		adapter_dataframe = adapter_dataframe[['name', 'value']]
	return adapter_dataframe
