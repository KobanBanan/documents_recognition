import os
import pathlib
import re

import PyPDF2
import pandas as pd
from natasha import MorphVocab, NamesExtractor
from tqdm.auto import tqdm
from pathlib import Path

FIELDS = [
    "LoanAmount",
    "LastName",
    "FirstName",
    "MiddleName",
    "BirthDate",
    "PassportSeries",
    "PassportNumber",
    "SigningDate"
]

STATEMENT_PATH = '/Users/a1234/Desktop/archives/statement'

morph_vocab = MorphVocab()
names_extractor = NamesExtractor(morph_vocab)


def collect_documents(directory):
    docs = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if pathlib.Path(f).suffix in ('.pdf',):
                docs.append(os.path.abspath(os.path.join(dirpath, f)))

    return docs


def collect_statement_data(path_to_file: str):
    """

    :param path_to_file:
    :return:
    """

    pdf_file_obj = open(path_to_file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj, strict=False)

    num_pages = range(pdf_reader.numPages)
    first_page_data = pdf_reader.getPage(0).extractText()
    last_page_data = pdf_reader.getPage(num_pages[-1]).extractText()

    name = extract_name(first_page_data)
    name = [n for n in name.split(" ") if n]
    last, first, middle = (name[0], name[1], " ".join(name[2:])) if name else (None, None, None)

    passport = extract_passport(first_page_data)
    series, number = passport

    date = extract_date(last_page_data)

    birthday = extarc_birthday(first_page_data)
    birthday = ".".join(birthday) if birthday else None
    # pdf_file_obj.close()

    loan = extarc_load_amount(first_page_data)

    return {
        "file": Path(path_to_file).name,
        "LoanAmount": loan,
        "LastName": last,
        "FirstName": first,
        "MiddleName": middle,
        "BirthDate": birthday,
        "PassportSeries": series,
        "PassportNumber": number,
        "SigningDate": date
    }


# TODO оч плохо
def extarc_load_amount(f):
    loan = f.splitlines()[3]
    if loan:
        loan = ("".join([i for i in loan if i.isdigit()]))
        if loan:
            return int(loan)


def extarc_birthday(s):
    pattern = r'\s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})\s*'
    match = re.search(pattern, s.replace("\n", " "))
    if match:
        return match.groups()


def extract_passport(s):
    """
    Extract passport by mask
    :param s:
    :return:
    """

    match = re.search(r"паспорт серия (\d{4})\s* номер ?\s*(\d{6})", s.replace("\n", " "))
    if match:
        res = match.groups()
        return res[0].strip(), res[1].strip()

    return None, None


def extract_date(s):
    match = re.search(
        r"Дата подписания: \s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})\s*$", s
    )

    if match:
        return ".".join(match.groups())


def extract_name(s):
    """
    Extract name from raw string
    :param s:
    :return:
    """
    pattern = r'(?<=Я, )[^,]+(?=, \d+\.\d+\.\d+)'
    match = re.search(pattern, s)
    if match:
        return match.group().strip()

    return ""


collected_documents = collect_documents(STATEMENT_PATH)

result = []

for _, doc in zip(tqdm(range(len(collected_documents))), collected_documents):
    data = collect_statement_data(doc)
    result.append(data)

df = pd.DataFrame(result)
df.to_csv('statement.csv', index=False)
