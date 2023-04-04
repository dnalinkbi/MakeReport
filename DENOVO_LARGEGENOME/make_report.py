#!/bin/python

import optparse
import sys
import os
import subprocess
import time
import json
import pandas as pd
import readjson
import jinja2
from docxtpl import DocxTemplate, InlineImage, RichText
from docx.shared import Mm
import datetime as dt
#from docx2pdf import convert

def getOptions(args):
    parser = optparse.OptionParser(description = "Sequel Sequencing Report Generation")
    parser.add_option("-i", "--instituteName", dest = "instituteName", metavar = "INSTITUTE_NAME", help = "Institute/Company Name")
    parser.add_option("-c", "--clientName", dest = "clientName", metavar = "Client Name", help = "Client Name")
    parser.add_option("-S", "--subreadxml", dest = "subreadxml", metavar = "SUBREADXML", help = "CLR xml file full path [example : /pacbio_ds2/sequel/_2nd_Analysis_/cromwell-executions/sl_copy_dataset/89fb8e60-372f-481e-b30f-cc9189f013af/call-reheader_bams/execution/updated.consensusreadset.xml]", default = "None")
    parser.add_option("-C", "--ccsxml", dest = "ccsxml", metavar = "CCSXML", help = "CCS xml file full path [example : /pacbio_ds2/sequel/_2nd_Analysis_/cromwell-executions/sl_copy_dataset/89fb8e60-372f-481e-b30f-cc9189f013af/call-reheader_bams/execution/updated.consensusreadset.xml]", default = "None")
    parser.add_option("-A", "--analysisFolder", dest = "analysisfolder", metavar= "ANALYSISFOLDER", help = "analysis folder path", default = "")
    parser.add_option("-m", "--mode", dest = "mode", metavar="MODE", help = "0: CLR only / 1: CCS on instrument / 2: CLR to CCS manual conversion (default: 0)", default = "0")
    parser.add_option("-n", "--cell", dest = "cell", metavar="CELL", help = "# Cell (default: 1)", default = 1)
    parser.add_option("-N", "--samplename", dest = "samplename", metavar="SAMPLENAME", help = "Sample Name")
    parser.add_option("-t", "--servicetype", dest = "servicetype", metavar="SERVICETYPE", help = "Service Type", default = "Sequencing Only")
    return parser.parse_args()[0]

def basic_config(xml):
    values = readjson.loading(xml)['value']
    config = {
        "zmw_count": format(int(values[0]), ','),
        "zmw_percent": round(float(values[0]) / float(values[0]) * float(100), 1),
        "p0_count": format(int(values[1]), ','),
        "p0_percent": round(float(values[1]) / float(values[0]) * float(100), 1),
        "p1_count": format(int(values[2]), ','),
        "p1_percent": round(float(values[2]) / float(values[0]) * float(100), 1),
        "p2_count": format(int(values[3]), ','),
        "p2_percent": round(float(values[3]) / float(values[0]) * float(100), 1),
        "adapter_dimer": readjson.adapter(xml)['value'][0],
        "short_inserts": readjson.adapter(xml)['value'][1],
    }
    return config

def CLR_config(xml, docx):
    if xml['cell'] != "1":
        config = {
            "polymerase_bases": format(int(readjson.rawdata(xml)['value'][0]), ','),
            "polymerase_reads": format(int(readjson.rawdata(xml)['value'][1]), ','),
            "polymerase_length": format(int(readjson.rawdata(xml)['value'][2]), ','),
            "polymerase_n50": format(int(readjson.rawdata(xml)['value'][3]), ','),
            "longest_subread_length": format(int(readjson.rawdata(xml)['value'][4]), ','),
            "longest_subread_n50": format(int(readjson.rawdata(xml)['value'][5]), ','),
            "unique_my": format(int(readjson.rawdata(xml)['value'][6]), ','),
            "polymerase_read_length_plot": InlineImage(docx, 'html/images/{0}'.format(readjson.plot(xml)[readjson.plot(xml)['title'] == "Polymerase Read Length"]['_image'].values[0]), width=Mm(130)),
            "subread_length_plot": "",
            "base_yield_density_plot": "",
        }
    elif xml['mode'] == "1":
        config = {
            "polymerase_bases": format(int(readjson.rawdata(xml)['value'][0]), ','),
            "polymerase_reads": format(int(readjson.rawdata(xml)['value'][1]), ','),
            "polymerase_length": format(int(readjson.rawdata(xml)['value'][2]), ','),
            "polymerase_n50": format(int(readjson.rawdata(xml)['value'][3]), ','),
            "longest_subread_length": format(int(readjson.rawdata(xml)['value'][4]), ','),
            "longest_subread_n50": format(int(readjson.rawdata(xml)['value'][5]), ','),
            "unique_my": format(int(readjson.rawdata(xml)['value'][6]), ','),
            "polymerase_read_length_plot": InlineImage(docx, 'html/images/{0}'.format(readjson.plot(xml)[readjson.plot(xml)['title'] == "Polymerase Read Length"]['_image'].values[0]), width=Mm(130)),
            "subread_length_plot": InlineImage(docx, 'html/images/{0}'.format(readjson.plot(xml)[readjson.plot(xml)['title'] == "Subread Length"]['_image'].values[0]), width=Mm(130)),
            "base_yield_density_plot": InlineImage(docx, 'html/images/{0}'.format(readjson.plot(xml)[readjson.plot(xml)['title'] == "Base Yield Density"]['_image'].values[0]), width=Mm(130)),
        }
    elif xml['mode'] == "0":
        config = {
            "polymerase_bases": format(int(readjson.rawdata(xml)['value'][0]), ','),
            "polymerase_reads": format(int(readjson.rawdata(xml)['value'][1]), ','),
            "polymerase_length": format(int(readjson.rawdata(xml)['value'][2]), ','),
            "polymerase_n50": format(int(readjson.rawdata(xml)['value'][3]), ','),
            "subread_length": format(int(readjson.rawdata(xml)['value'][4]), ','),
            "subread_n50": format(int(readjson.rawdata(xml)['value'][5]), ','),
            "longest_subread_length": format(int(readjson.rawdata(xml)['value'][6]), ','),
            "longest_subread_n50": format(int(readjson.rawdata(xml)['value'][7]), ','),
            "unique_my": format(int(readjson.rawdata(xml)['value'][6]), ','),
            "polymerase_read_length_plot": InlineImage(docx, 'html/images/{0}'.format(readjson.plot(xml)[readjson.plot(xml)['title'] == "Polymerase Read Length"]['_image'].values[0]), width=Mm(130)),
            "subread_length_plot": InlineImage(docx, 'html/images/{0}'.format(readjson.plot(xml)[readjson.plot(xml)['title'] == "Subread Length"]['_image'].values[0]), width=Mm(130)),
            "base_yield_density_plot": InlineImage(docx, 'html/images/{0}'.format(readjson.plot(xml)[readjson.plot(xml)['title'] == "Base Yield Density"]['_image'].values[0]), width=Mm(130)),
        }
    else:
        config = {
            "polymerase_bases": format(int(readjson.rawdata(xml)['value'][0]), ','),
            "polymerase_reads": format(int(readjson.rawdata(xml)['value'][1]), ','),
            "polymerase_length": format(int(readjson.rawdata(xml)['value'][2]), ','),
            "polymerase_n50": format(int(readjson.rawdata(xml)['value'][3]), ','),
            #"subread_length": format(int(readjson.rawdata(xml)['value'][4]), ','),
            #"subread_n50": format(int(readjson.rawdata(xml)['value'][5]), ','),
            "longest_subread_length": format(int(readjson.rawdata(xml)['value'][4]), ','),
            "longest_subread_n50": format(int(readjson.rawdata(xml)['value'][5]), ','),
            "unique_my": format(int(readjson.rawdata(xml)['value'][6]), ','),
            "polymerase_read_length_plot": InlineImage(docx, 'html/images/{0}'.format(readjson.plot(xml)[readjson.plot(xml)['title'] == "Polymerase Read Length"]['_image'].values[0]), width=Mm(130)),
            "subread_length_plot": "",
            "base_yield_density_plot": InlineImage(docx, 'html/images/{0}'.format(readjson.plot(xml)[readjson.plot(xml)['title'] == "Base Yield Density"]['_image'].values[0]), width=Mm(130)),
        }
    return config

def CCS_config(xml, docx):
    ccs = readjson.ccs(xml)
    ccs_plot = readjson.ccs_plot(xml)
    config = {
        "hifi_bases": f"{int(ccs[ccs['name'] == 'HiFi Yield (bp)']['value'].values[0]):,}",
        "hifi_reads": f"{int(ccs[ccs['name'] == 'HiFi Reads']['value'].values[0]):,}",
        "hifi_length": f"{int(ccs[ccs['name'] == 'HiFi Read Length (mean, bp)']['value'].values[0]):,}",
        "hifi_quality": f"{ccs[ccs['name'] == 'HiFi Read Quality (median)']['value'].values[0]}",
        "hifi_passes": f"{int(ccs[ccs['name'] == 'HiFi Number of Passes (mean)']['value'].values[0]):,}",
        "read_length_distribution_plot": InlineImage(docx, f"html/images/{ccs_plot[ccs_plot['title'] == 'Read Length Distribution']['_image'].values[0]}", width=Mm(130)),
        "total_read_length_distribution_plot": InlineImage(docx, f"html/images/{ccs_plot[ccs_plot['title'] == 'Read Length Distribution']['_image'].values[1]}", width=Mm(130)),
        "number_of_passes_plot": InlineImage(docx, f"html/images/{ccs_plot[ccs_plot['title'] == 'Number of Passes']['_image'].values[0]}", width=Mm(130)),
        "read_qulity_distribution_plot": InlineImage(docx, f"html/images/{ccs_plot[ccs_plot['title'] == 'Read Quality Distribution']['_image'].values[0]}", width=Mm(130)),
    }
    return config

def analysis_assembly(analysis_folder):
    assembly_data = pd.read_csv(f"{analysis_folder}/report-data/genome.csv", sep=",", header=None).T
    assembly_data = assembly_data[assembly_data[0].str.contains("scaffold")]
    assembly_data = assembly_data[assembly_data[0].str.contains("Percentage of scaffolds") != True]
    busco_data = pd.read_csv(f"{analysis_folder}/report-data/busco.tsv", sep="\t", header=None)

    config = {
        'contig': assembly_data[assembly_data[0] == 'Number of scaffolds'].iloc[0,1],
        'size': assembly_data[assembly_data[0] == 'Total size of scaffolds'].iloc[0,1],
        'longest': assembly_data[assembly_data[0] == 'Longest scaffold'].iloc[0,1],
        'shortest': assembly_data[assembly_data[0] == 'Shortest scaffold'].iloc[0,1],
        'K': assembly_data[assembly_data[0] == 'Number of scaffolds > 1K nt'].iloc[0,1],
        'KK': assembly_data[assembly_data[0] == 'Number of scaffolds > 10K nt'].iloc[0,1],
        'KKK': assembly_data[assembly_data[0] == 'Number of scaffolds > 100K nt'].iloc[0,1],
        'M': assembly_data[assembly_data[0] == 'Number of scaffolds > 1M nt'].iloc[0,1],
        'MM': assembly_data[assembly_data[0] == 'Number of scaffolds > 10M nt'].iloc[0,1],
        'mean': assembly_data[assembly_data[0] == 'Mean scaffold size'].iloc[0,1],
        'median': assembly_data[assembly_data[0] == 'Median scaffold size'].iloc[0,1],
        'n50': assembly_data[assembly_data[0] == 'N50 scaffold length'].iloc[0,1],
        'l50': assembly_data[assembly_data[0] == 'L50 scaffold count'].iloc[0,1],
        'gc': round(float(assembly_data[assembly_data[0] == 'scaffold %C'].iloc[0,1]) + float(assembly_data[assembly_data[0] == 'scaffold %G'].iloc[0,1]), 2),

        'complete': busco_data.iloc[0,1],
        'completeSC': busco_data.iloc[1,1],
        'completeD': busco_data.iloc[2,1],
        'fragmented': busco_data.iloc[3,1],
        'missing': busco_data.iloc[4,1],
        'total': busco_data.iloc[5,1],
        'completep': busco_data.iloc[0,2],
        'completeSCp': busco_data.iloc[1,2],
        'completeDp': busco_data.iloc[2,2],
        'fragmentedp': busco_data.iloc[3,2],
        'missingp': busco_data.iloc[4,2],
        'db': busco_data.iloc[6,0],
    }
    return config

def download_config(samplename, cell, docx, xml):
    subreads_bam_key = [f"subreads_bam_{i}" for i in range(1,cell+1)]
    subreads_bam_value = [RichText(f"Subreads Cell {i} BAM", url_id=docx.build_url_id(f"http://download.dnalink.com/Report/PacBio/{samplename}.{i}Cell.subreads.bam.tar.gz"), color='#1357a6', size=24, font="나눔스퀘어OTF", underline=True) for i in range(1,cell+1)]
    subreads_fasta_key = [f"subreads_fasta_{i}" for i in range(1,cell+1)]
    subreads_fasta_value = [RichText(f"Subreads Cell {i} FASTA", url_id=docx.build_url_id(f"http://download.dnalink.com/Report/PacBio/{samplename}.{i}Cell.subreads.fasta.gz"), color='#1357a6', size=24, font="나눔스퀘어OTF", underline=True) for i in range(1,cell+1)]
    hifi_bam_key = [f"hifi_bam_{i}" for i in range(1,cell+1)]
    hifi_bam_value = [RichText(f"HiFi Cell {i} BAM", url_id=docx.build_url_id(f"http://download.dnalink.com/Report/PacBio/{samplename}.{i}Cell.hifi.bam.tar.gz"), color='#1357a6', size=24, font="나눔스퀘어OTF", underline=True) for i in range(1,cell+1)]
    hifi_fasta_key = [f"hifi_fasta_{i}" for i in range(1,cell+1)]
    hifi_fasta_value = [RichText(f"HiFi Cell {i} FASTA", url_id=docx.build_url_id(f"http://download.dnalink.com/Report/PacBio/{samplename}.{i}Cell.hifi.fasta.gz"), color='#1357a6', size=24, font="나눔스퀘어OTF", underline=True) for i in range(1,cell+1)]
    hifi_fastq_key = [f"hifi_fastq_{i}" for i in range(1,cell+1)]
    hifi_fastq_value = [RichText(f"HiFi Cell {i} FASTQ", url_id=docx.build_url_id(f"http://download.dnalink.com/Report/PacBio/{samplename}.{i}Cell.hifi.fastq.gz"), color='#1357a6', size=24, font="나눔스퀘어OTF", underline=True) for i in range(1,cell+1)]

    md5 = RichText('MD5', url_id=docx.build_url_id(f"http://download.dnalink.com/Report/PacBio/{samplename}.md5"), color='#1357a6', size=24, font="나눔스퀘어OTF", underline=True)
    pacbio_pdf = RichText('PacBio manual PDF', url_id=docx.build_url_id('https://www.pacb.com/wp-content/uploads/SMRT_Link_User_Guide_v11.0.pdf'), color='#1357a6', size=24, font="나눔스퀘어OTF", underline=True)

    config = dict(zip(subreads_bam_key, subreads_bam_value))
    config.update(dict(zip(subreads_fasta_key, subreads_fasta_value)))
    config.update(dict(zip(hifi_bam_key, hifi_bam_value)))
    config.update(dict(zip(hifi_fasta_key, hifi_fasta_value)))
    config.update(dict(zip(hifi_fastq_key, hifi_fastq_value)))
    config.update({'md5': md5})
    config.update({'pacbio_pdf': pacbio_pdf})

    if xml['mode'] == "0":
        config.pop('hifi_bam', None)
        config.pop('hifi_fastq', None)

    return config

def main():
    
    #| OPTIONS  
    options = getOptions(sys.argv)
    institution = options.instituteName
    client = options.clientName
    clr_xml = options.subreadxml
    ccs_xml = options.ccsxml
    analysis_folder = options.analysisfolder
    mode = options.mode
    cell = int(options.cell)
    samplename = str(options.samplename)
    servicetype = options.servicetype

    #| MERGE subset files
    jinja_env = jinja2.Environment()
    jinja_env.trim_blocks = True
    jinja_env.lstrip_blocks = True
    master = DocxTemplate("master-report.docx")
    clr_report = master.new_subdoc("sequencing-clr-report.docx")
    ccs_report = master.new_subdoc("sequencing-ccs-report.docx")
    download_report = master.new_subdoc("download-report.docx")
    analysis_assembly_report = master.new_subdoc("analysis-assembly-report.docx")

    main_config = {
        "date": dt.datetime.now().strftime("%d-%b-%Y"),
        "client": client,
        "company": institution,
        "samplename": samplename,
        "servicetype": servicetype,
        "cell": cell,
        "CLRreport": clr_report,
        "CCSreport": ccs_report,
        "download": download_report,
        "analysis_assembly": analysis_assembly_report if analysis_folder != "" else "",
    }
    master.render(main_config)

    #| TABLE 값 config 파일 작성
    #| RAW DATA 항목
    if mode == "0":
        xml = {"cell" : "%s"%cell, "mode" : "%s"%mode, "clr" : "%s"%clr_xml}
        for i,j in enumerate(readjson.plot(xml)['fullpath']):
            os.system("\\cp %s ./html/images/"%j)
        config = dict(basic_config(xml).items() | CLR_config(xml, master).items() | download_config(samplename, cell, master, xml).items()) 
    elif mode == "1":
        xml = {"cell" : "%s"%cell, "mode" : "%s"%mode, "clr" : "%s"%ccs_xml, "ccs" : "%s"%ccs_xml}
        for i,j in enumerate(readjson.plot(xml)['fullpath']):
            os.system("\\cp %s ./html/images/"%j)
        for i,j in enumerate(readjson.ccs_plot(xml)['fullpath']):
            os.system("\\cp %s ./html/images/"%j)
        config = dict(basic_config(xml).items() | CCS_config(xml, master).items() | download_config(samplename, cell, master, xml).items()) 
    else:
        xml = {"cell" : "%s"%cell, "mode" : "%s"%mode, "clr" : "%s"%clr_xml, "ccs" : "%s"%ccs_xml}
        for i,j in enumerate(readjson.plot(xml)['fullpath']):
            os.system("\\cp %s ./html/images/"%j)
        for i,j in enumerate(readjson.ccs_plot(xml)['fullpath']):
            os.system("\\cp %s ./html/images/"%j)
        config = dict(basic_config(xml).items() | CLR_config(xml, master).items() | CCS_config(xml, master).items() | download_config(samplename, cell, master, xml).items()) 

    # ANALYSIS ASSEMBLY 항목
    if analysis_folder != "":
        config = dict(config.items() | analysis_assembly(analysis_folder).items())

    master.render(config)
    master.save(f"{dt.datetime.now().strftime('%Y%m%d')}.{institution}.{client}.{samplename}.report.docx")


if __name__ == "__main__":
    main()


