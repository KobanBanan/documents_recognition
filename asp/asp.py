import os
import pathlib
import re
from typing import Dict, List

import PyPDF2
import pandas as pd
import streamlit as st
from stqdm import stqdm

ASP_FIELDS = [
    "DocName",
    "CreditorName",
    "AcceptDate"
]

# ASP_PATH = '/Users/a1234/Desktop/PeedoRevoTest'
acceptance_date_regex = re.compile(r"\s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})\s*")
creditor_name_regex = (
    re.compile(r'(?<=предложением)(.*)(?= заключить)'),
    re.compile(r'(?<=Общество — )(.*)(?= \(адрес)')
)
doc_name_regex = (
    re.compile(r'(?<=все условия)(.*)(?=» Проставляя)'),
    re.compile(r'(?<=все условия)(.*)(?=»Проставляя)')
)


def collect_documents(directory):
    docs = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if pathlib.Path(f).suffix in ('.pdf',):
                docs.append(os.path.abspath(os.path.join(dirpath, f)))

    return docs


def collect_asp_data(pdf_dict: List[Dict[str, PyPDF2.PdfFileReader]]):
    """
    :param pdf_dict:
    :return:
    """
    result = []

    for file, _ in zip(pdf_dict, stqdm(range(len(pdf_dict)))):
        file_name, pdf_reader = file.get('file_name'), file.get('pdf_reader')
        try:
            num_pages = range(pdf_reader.numPages)

            first_page_data = pdf_reader.getPage(0).extractText()
            last_page_data = pdf_reader.getPage(num_pages[-1]).extractText()

            doc_name = extract_doc_name(first_page_data)
            creditor_name = extract_creditor_name(first_page_data)

            accept_date = extract_accept_date(last_page_data)

            result.append(
                {
                    "file": file_name,
                    "DocName": doc_name,
                    "CreditorName": creditor_name,
                    "AcceptDate": accept_date

                }
            )
        except:
            st.error(f'Ошибка разспознавания документа {file_name}')
            result.append(
                {
                    "file": None,
                    "DocName": None,
                    "CreditorName": None,
                    "AcceptDate": None

                }
            )
    return pd.DataFrame(result).dropna(subset=ASP_FIELDS, how='all')


def extract_doc_name(s):
    for pattern in doc_name_regex:
        match = re.search(pattern, s.replace("\n", ""))
        if match:
            return match.group()


def extract_creditor_name(s):
    for pattern in creditor_name_regex:
        match = re.search(pattern, s)
        if match:
            return match.group()


def extract_accept_date(s):
    match = re.search(acceptance_date_regex, s.replace('\n', ' '))
    if match:
        return ".".join(match.groups())

# collected_documents = collect_documents(ASP_PATH)
#
# result = []
#
# for _, doc in zip(tqdm(range(len(collected_documents))), collected_documents):
#     data = collect_data(doc)
#     result.append(data)
#
# df = pd.DataFrame(result)
# df.to_csv('asp.csv', index=False)
