import os
import pathlib
import re
from pathlib import Path

import PyPDF2
import pandas as pd
from tqdm.auto import tqdm

FIELDS = [
    "DocName",
    "CreditorName",
    "AcceptDate"
]

ASP_PATH = '/Users/a1234/Desktop/archives/asp'
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


def collect_data(path_to_file: str):
    """

    :param path_to_file:
    :return:
    """

    pdf_file_obj = open(path_to_file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj, strict=False)

    num_pages = range(pdf_reader.numPages)

    first_page_data = pdf_reader.getPage(0).extractText()
    last_page_data = pdf_reader.getPage(num_pages[-1]).extractText()

    doc_name = extract_doc_name(first_page_data)
    creditor_name = extract_creditor_name(first_page_data)

    accept_date = extract_accept_date(last_page_data)

    return {
        "file": Path(path_to_file).name,
        "DocName": doc_name,
        "CreditorName": creditor_name,
        "AcceptDate": accept_date

    }


def extract_doc_name(s):
    for pattern in doc_name_regex:
        match = re.search(pattern, s.replace("\n", ""))
        if match:
            return match.group()


def extract_date(s):
    pass


def extract_creditor_name(s):
    for pattern in creditor_name_regex:
        match = re.search(pattern, s)
        if match:
            return match.group()


def extract_accept_date(s):
    match = re.search(acceptance_date_regex, s.replace('\n', ' '))
    if match:
        return ".".join(match.groups())


collected_documents = collect_documents(ASP_PATH)

result = []

for _, doc in zip(tqdm(range(len(collected_documents))), collected_documents):
    data = collect_data(doc)
    result.append(data)

df = pd.DataFrame(result)
df.to_csv('asp.csv', index=False)
