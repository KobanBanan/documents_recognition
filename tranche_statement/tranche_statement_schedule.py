import os
import pathlib
import re
from typing import Dict, List

import PyPDF2
import pandas as pd
import streamlit as st
from stqdm import stqdm

# TRANCHE_PATH = '/Users/a1234/Desktop/PeedoRevoTest'
TRANCHE_STATEMENT_SCHEDULE_COLS = [
    "HasPaymentSchedule",
    "PaymentScheduleDate",
    "PaymentScheduleMainDebtAmount"
]


def extract_has_payment_schedule(s):
    pattern = 'График платежей по Траншу'
    match = re.search(pattern, s)
    if match:
        return True

    return False


def extract_payment_schedule_date(s):
    pattern = r'(?<=График платежей по договору потребительского Займа от)(.*?)(?=Дата)'
    match = re.search(pattern, s)
    if match:
        return match.group()


def extract_payment_schedule_main_debt_amount(s):
    pattern = '(?<=ИТОГО:).*$'
    match = re.search(pattern, s)
    if match:
        amount = match.group().split('\x00')
        if len(amount) > 3:
            return amount[2].strip().replace(',', '.').replace(' ', '')


def collect_documents(directory):
    docs = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if pathlib.Path(f).suffix in ('.pdf',):
                docs.append(os.path.abspath(os.path.join(dirpath, f)))

    return docs


def collect_tranche_statement_schedule_data(pdf_dict: List[Dict[str, PyPDF2.PdfFileReader]]):
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

            result.append({
                "file": file_name,
                "HasPaymentSchedule": extract_has_payment_schedule(first_page_data),
                "PaymentScheduleDate": extract_payment_schedule_date(last_page_data.replace('\n', '')),
                "PaymentScheduleMainDebtAmount": extract_payment_schedule_main_debt_amount(last_page_data)
            })
        except Exception as e:
            st.error(f'Ошибка разспознавания документа {file_name}')
            result.append({
                "file": file_name,
                "HasPaymentSchedule": None,
                "PaymentScheduleDate": None,
                "PaymentScheduleMainDebtAmount": None
            })

    return pd.DataFrame(result).dropna(subset=TRANCHE_STATEMENT_SCHEDULE_COLS, how='all')

#
# collected_documents = collect_documents(TRANCHE_PATH)
# # collected_documents = ['/Users/a1234/Desktop/ocr/Revo3/tranche_statement/000062273/000062273_tranche_statement.pdf']
# result = []
#
# for _, doc in zip(tqdm(range(len(collected_documents))), collected_documents):
#     data = collect_tranche_statement_data(doc)
#     result.append(data)
#
# df = pd.DataFrame(result)
# df.to_csv('tranche_statement_schedule.csv', index=False)
