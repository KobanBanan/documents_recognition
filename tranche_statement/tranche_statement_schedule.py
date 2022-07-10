import os
import pathlib
import re
from pathlib import Path

import PyPDF2
import pandas as pd
from tqdm.auto import tqdm

TRANCHE_PATH = '/Users/a1234/Desktop/archives/tranche_statement'


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


def collect_tranche_statement_data(path_to_file: str):
    """

    :param path_to_file:
    :return:
    """

    pdf_file_obj = open(path_to_file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj, strict=False)

    num_pages = range(pdf_reader.numPages)

    first_page_data = pdf_reader.getPage(0).extractText()
    last_page_data = pdf_reader.getPage(num_pages[-1]).extractText()

    return {
        "file": Path(path_to_file).name,
        "HasPaymentSchedule": extract_has_payment_schedule(first_page_data),
        "PaymentScheduleDate": extract_payment_schedule_date(last_page_data.replace('\n', '')),
        "PaymentScheduleMainDebtAmount": extract_payment_schedule_main_debt_amount(last_page_data)
    }


collected_documents = collect_documents(TRANCHE_PATH)
# collected_documents = ['/Users/a1234/Desktop/ocr/Revo3/tranche_statement/000062273/000062273_tranche_statement.pdf']
result = []

for _, doc in zip(tqdm(range(len(collected_documents))), collected_documents):
    data = collect_tranche_statement_data(doc)
    result.append(data)

df = pd.DataFrame(result)
df.to_csv('tranche_statement_schedule.csv', index=False)
