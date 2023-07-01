import re
from typing import Dict, List

import PyPDF2
import pandas as pd
import streamlit as st
from stqdm import stqdm


AGREEMENT_COLS = [
    "LastName",
    "FirstName",
    "MiddleName",
    "PassportSeries",
    "PassportNumber",
    "SigningDate"
]


def extract_passport(s):
    """
    Extract passport by mask
    :param s:
    :return:
    """
    match = re.search(r"паспорт (\d{4})\s*-?\s*(\d{6})", s)
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
    patterns = [
        r"(?<=Я)(.*)(?= \(паспорт)",
        r'(?<=Я,)(.*)(?= даю свое согласие)'
    ]
    for pattern in patterns:
        match = re.search(pattern, s)
        if match:
            return match.group().replace(',', '').strip()

    return ""


def collect_agreement_data(pdf_dict: List[Dict[str, PyPDF2.PdfFileReader]]):
    """
    :param pdf_dict:
    :return:
    """
    result = []

    for file, _ in zip(pdf_dict, stqdm(range(len(pdf_dict)))):
        file_name, pdf_reader = file.get('file_name'), file.get('pdf_reader')
        try:
            num_pages = range(pdf_reader.numPages)

            first_page_data = pdf_reader.getPage(0).extract_text()

            last_page = pdf_reader.getPage(num_pages[-1])
            last_page_data = last_page.extract_text()

            # extract_data from first page

            name = extract_name(first_page_data)
            name = [n for n in name.split(" ") if n]
            last, first, middle = (name[0], name[1], " ".join(name[2:])) if name else (None, None, None)

            series, number = extract_passport(first_page_data)
            date = extract_date(last_page_data)

            result.append({
                "file": file_name,
                "LastName": last,
                "FirstName": first,
                "MiddleName": middle,
                "PassportSeries": series,
                "PassportNumber": number,
                "SigningDate": date
            })

        except Exception as e:
            st.error(f'Ошибка разспознавания документа {file_name}')
            result.append({
                "file": file_name,
                "LastName": None,
                "FirstName": None,
                "MiddleName": None,
                "PassportSeries": None,
                "PassportNumber": None,
                "SigningDate": None
            })

    return pd.DataFrame(result)
