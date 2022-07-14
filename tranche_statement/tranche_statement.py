import os
import pathlib
import re
from typing import Dict, List

import PyPDF2
import pandas as pd
import streamlit as st
from stqdm import stqdm

# TRANCHE_PATH = '/Users/a1234/Desktop/PeedoRevoTest'
EMPTY_RESULT = None
TRANCHE_STATEMENT_COLS = [
    "TrancheNumber",
    "TrancheDate",
    "ParentContractNumber",
    "ParentContractDate",
    "TrancheAmount",
    "TrancheTerm",
    "TranchePercent",
    "TrancePercentYear",
    "TrancheFullAmount",
    "CustomerName",
    "CustomerBirth",
    "CustomerPassportSeries",
    "CustomerPassportNumber",
    "CustomerSignatureDate",
    "TrancheSigningDate"
]

UNKNOWN_CASE = 0
CASE_ONE = 1
CASE_TWO = 2
CASE_THREE = 3

ALL_CASES = [CASE_ONE, CASE_TWO, CASE_THREE]


def collect_documents(directory):
    docs = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if pathlib.Path(f).suffix in ('.pdf',):
                docs.append(os.path.abspath(os.path.join(dirpath, f)))

    return docs


def extract_tranche_number(s):
    pattern = r'(?<=Транш № )(.*?)(?= от)'
    match = re.search(pattern, s)
    if match:
        return match.group().strip()


def extract(s, p):
    match = re.search(p, s)
    if match:
        return match.group().strip()


def extract_tranche_date(s):
    pattern = '(?<=от )(.*?)(?=Договор)'
    match = re.search(pattern, s)
    if match:
        return match.group().strip()


def extract_parent_contract_number(s):
    pattern = r'(?<=Договор потребительского займа№)(.*?)(?=от)'
    match = re.search(pattern, s)
    if match:
        return match.group().strip()


def extract_customer_name(s):
    patterns = [
        r"(?<=Я, )[^,]+(?=,)",
        r'(?<=Заемщик \(Клиент\):)(.*?)(?=,)'
    ]
    for pattern in patterns:
        match = re.search(pattern, s)
        if match:
            return match.group()


def extract_customer_birth(s):
    pattern = '(?<=, )[^,]+(?=года )'
    match = re.search(pattern, s)
    if match:
        return match.group().strip()


def extract_customer_passport_series(s):
    patterns = [
        r'(?<=паспорт серия)(.*?)(?=номер)',
        r'(?<=паспорт:серия)(.*?)(?=номер)'
    ]
    for pattern in patterns:
        match = re.search(pattern, s)
        if match:
            return match.group().strip()


def extract_customer_passport_number(s):
    patterns = [
        r'(?<=номер)[^,]+(?=, прошу)',
        r'(?<=номер)[^,]+(?=,прошу)',
        r'(?<=номер )[^,]+(?=, телефон)'
    ]
    for pattern in patterns:
        match = re.search(pattern, s)
        if match:
            return match.group().strip()


def extract_customer_signature_date(s):
    pattern = r'(?<=\[)\d{1,2}\.\d{1,2}\.\d{2}(?:\d{2})?(?=\])'
    match = re.search(pattern, s)
    if match:
        return match.group()


def extract_tranche_signing_date(s):
    match = re.search(
        r"Дата подписания: \s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})\s*$", s
    )

    if match:
        return ".".join(match.groups())


# TODO здесь
def extract_tranche_full_amount(s):
    patterns = [
        r'(?<=Сумма Траншей \(максимальнаясумма, доступная по Виртуальнойкарте)(.*?)(?= руб)',
        r'(?<=Полная стоимость Траншапотребительского займа\(в денежном выражении\))(.*?)(?=коп)',
        r'(?<=Полная стоимость Траншапотребительского займа \(в денежномвыражении\))(.*?)(?=\.)'
    ]
    for pattern in patterns:
        match = re.search(pattern, s)
        if match:
            return match.group().strip()


def extract_tranche_amount(s):
    pattern = r'(?<=Сумма Транша)(.*?)(?= руб)'
    match = re.search(pattern, s)
    if match:
        return match.group().strip().replace("'", '')


def extract_tranche_term(s):
    pattern = r'(?<=Срок Транша)(.*?)(?=мес)'
    match = re.search(pattern, s)
    if match:
        return match.group().strip()


def extract_tranche_percent(s):
    pattern = r'(?<=Процентная ставка по Траншу)(.*?)(?=процентов)'
    match = re.search(pattern, s)
    if match:
        return match.group().strip()


def extract_tranche_percent_year(s):
    patterns = [
        r'(?<=Полная стоимость Траншапотребительского займа\(в процентах годовых\))(.*?)(?= процентов)',
        r'(?<=Полная стоимость Траншапотребительского займа \(в процентахгодовых\) )(.*?)(?= процентов)'
    ]
    for pattern in patterns:
        match = re.search(pattern, s)
        if match:
            return match.group().strip()


def extract_parent_contract_date(s):
    pattern = r'\s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})\s*'
    match = re.search(pattern, s)
    if match:
        return ".".join(match.groups())


def extract_payment_schedule(s):
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


def get_case(s):
    tranche_number, tranche_date = extract_tranche_number(s), extract_tranche_date(s.replace('\n', ''))

    # case 3 - нет номера транша, только номер займа
    if not tranche_number:
        return CASE_THREE

    # case 2 - есть дата транша и номер транша
    elif tranche_number and tranche_date:
        return CASE_TWO

    # case 1 - есть номер транша но нет даты транша
    elif tranche_number and not tranche_date:
        return CASE_ONE

    return UNKNOWN_CASE


def collect_tranche_statement_data(pdf_dict: List[Dict[str, PyPDF2.PdfFileReader]]):
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
            pre_penultimate_page = pdf_reader.getPage(num_pages[-3]).extractText() if len(
                num_pages) > 2 else first_page_data
            penultimate_page = pdf_reader.getPage(num_pages[-2]).extractText() if len(
                num_pages) > 1 else first_page_data
            last_page_data = pdf_reader.getPage(num_pages[-1]).extractText()

            case = get_case(first_page_data)

            if case == CASE_ONE:
                # case 2
                # --------------------------------------------------------------------------------------------------------------
                tranche_number = extract(first_page_data.replace('\n', ' '), r'(?<=Транш № )(.*?)(?=Договор)')
                parent_contract_date = extract_parent_contract_date(first_page_data.replace('\n', ''))
                parent_contract_number = extract_parent_contract_number(first_page_data)
                tranche_amount = extract_tranche_amount(first_page_data)
                tranche_term = extract_tranche_term(first_page_data)
                tranche_percent = extract_tranche_percent(first_page_data)
                tranche_percent_year = extract_tranche_percent_year(first_page_data.replace('\n', ''))
                tranche_full_amount = extract_tranche_full_amount(first_page_data.replace('\n', ''))  # todo

                customer_name = extract_customer_name(last_page_data)
                customer_birth = extract(last_page_data, r'(?<=, )[^,]+(?= года)')
                customer_passport_series = extract_customer_passport_series(last_page_data.replace('\n', ''))
                customer_passport_number = extract_customer_passport_number(last_page_data)
                customer_signature_date = extract_customer_signature_date(last_page_data)
                tranche_signing_date = extract_tranche_signing_date(last_page_data.replace('\n', ''))

                result.append({
                    'case': case,
                    "file": file_name,
                    "TrancheNumber": tranche_number,
                    "TrancheDate": EMPTY_RESULT,
                    "ParentContractNumber": parent_contract_date,
                    "ParentContractDate": parent_contract_number,
                    "TrancheAmount": tranche_amount,
                    "TrancheTerm": tranche_term,
                    "TranchePercent": tranche_percent,
                    "TrancePercentYear": tranche_percent_year,
                    "TrancheFullAmount": tranche_full_amount,
                    "CustomerName": customer_name,
                    "CustomerBirth": customer_birth,
                    "CustomerPassportSeries": customer_passport_series,
                    "CustomerPassportNumber": customer_passport_number,
                    "CustomerSignatureDate": customer_signature_date,
                    "TrancheSigningDate": tranche_signing_date
                })

            if case == CASE_TWO:
                # case 2
                # --------------------------------------------------------------------------------------------------------------

                third_page_data = pdf_reader.getPage(2).extractText()

                tranche_number = extract_tranche_number(first_page_data)
                tranche_date = extract_tranche_date(first_page_data.replace('\n', ''))
                parent_contract_date = extract_parent_contract_date(first_page_data.replace('\n', ''))
                parent_contract_number = extract_parent_contract_number(first_page_data)
                tranche_amount = extract_tranche_amount(first_page_data)
                tranche_term = extract_tranche_term(first_page_data)
                tranche_percent = extract_tranche_percent(first_page_data)
                tranche_percent_year = extract_tranche_percent_year(first_page_data)
                tranche_full_amount = extract_tranche_full_amount(first_page_data.replace('\n', ''))

                customer_name = (
                        extract_customer_name(penultimate_page) or
                        extract_customer_name(pre_penultimate_page)
                )
                # customer_name = [n for n in customer_name.split(" ") if n] if all(customer_name) else customer_name
                customer_birth = (
                        extract_customer_birth(penultimate_page) or
                        extract_customer_birth(pre_penultimate_page)
                )
                customer_passport_series = (
                        extract_customer_passport_series(penultimate_page) or
                        extract_customer_passport_series(pre_penultimate_page)
                )
                customer_passport_number = (
                        extract_customer_passport_number(penultimate_page) or
                        extract_customer_passport_number(pre_penultimate_page)
                )
                customer_signature_date = (
                        extract_customer_signature_date(penultimate_page) or
                        extract_customer_signature_date(pre_penultimate_page)
                )
                tranche_signing_date = (
                        extract_tranche_signing_date(penultimate_page.replace('\n', '')) or
                        extract_tranche_signing_date(pre_penultimate_page.replace('\n', ''))
                )

                result.append({
                    'case': case,
                    "file": file_name,
                    "TrancheNumber": tranche_number,
                    "TrancheDate": tranche_date,
                    "ParentContractNumber": parent_contract_number,
                    "ParentContractDate": parent_contract_date,
                    "TrancheAmount": tranche_amount,
                    "TrancheTerm": tranche_term,
                    "TranchePercent": tranche_percent,
                    "TrancePercentYear": tranche_percent_year,
                    "TrancheFullAmount": tranche_full_amount,
                    "CustomerName": customer_name,
                    "CustomerBirth": customer_birth,
                    "CustomerPassportSeries": customer_passport_series,
                    "CustomerPassportNumber": customer_passport_number,
                    "CustomerSignatureDate": customer_signature_date,
                    "TrancheSigningDate": tranche_signing_date
                })

            if case == CASE_THREE:
                # case 3
                # --------------------------------------------------------------------------------------------------------------
                tranche_full_amount = extract_tranche_full_amount(first_page_data.replace('\n', '').replace(')', ''))
                tranche_term = extract(first_page_data, '(?<=составляет)(.*?)(?=мес)')
                parent_contract_date = extract_parent_contract_date(first_page_data.replace('\n', ''))
                parent_contract_number = extract_parent_contract_number(first_page_data)

                customer_name = extract_customer_name(penultimate_page)
                # customer_name = [n for n in customer_name.split(" ") if n] if all(customer_name) else customer_name
                customer_birth = extract_customer_birth(penultimate_page)
                customer_passport_series = extract_customer_passport_series(penultimate_page)
                customer_passport_number = extract_customer_passport_number(penultimate_page.replace('\n', ''))
                customer_signature_date = extract_customer_signature_date(penultimate_page)
                tranche_signing_date = extract_tranche_signing_date(penultimate_page)

                result.append({
                    'case': case,
                    "file": file_name,
                    "TrancheNumber": EMPTY_RESULT,
                    "TrancheDate": EMPTY_RESULT,
                    "ParentContractNumber": parent_contract_number,
                    "ParentContractDate": parent_contract_date,
                    "TrancheAmount": tranche_full_amount,
                    "TrancheTerm": tranche_term,
                    "TranchePercent": EMPTY_RESULT,
                    "TrancePercentYear": EMPTY_RESULT,
                    "TrancheFullAmount": tranche_full_amount,
                    "CustomerName": customer_name,
                    "CustomerBirth": customer_birth,
                    "CustomerPassportSeries": customer_passport_series,
                    "CustomerPassportNumber": customer_passport_number,
                    "CustomerSignatureDate": customer_signature_date,
                    "TrancheSigningDate": tranche_signing_date
                })
            if case == UNKNOWN_CASE:
                result.append({
                    "case": 0,
                    "file": file_name,
                    "TrancheNumber": None,
                    "TrancheDate": None,
                    "ParentContractNumber": None,
                    "ParentContractDate": None,
                    "TrancheAmount": None,
                    "TrancheTerm": None,
                    "TranchePercent": None,
                    "TrancePercentYear": None,
                    "TrancheFullAmount": None,
                    "CustomerName": None,
                    "CustomerBirth": None,
                    "CustomerPassportSeries": None,
                    "CustomerPassportNumber": None,
                    "CustomerSignatureDate": None,
                    "TrancheSigningDate": None
                })
        except Exception as e:
            st.error(f'Ошибка разспознавания документа {file_name}')
            result.append({
                "case": 0,
                "file": file_name,
                "TrancheNumber": None,
                "TrancheDate": None,
                "ParentContractNumber": None,
                "ParentContractDate": None,
                "TrancheAmount": None,
                "TrancheTerm": None,
                "TranchePercent": None,
                "TrancePercentYear": None,
                "TrancheFullAmount": None,
                "CustomerName": None,
                "CustomerBirth": None,
                "CustomerPassportSeries": None,
                "CustomerPassportNumber": None,
                "CustomerSignatureDate": None,
                "TrancheSigningDate": None
            })

    return pd.DataFrame(result)

# collected_documents = collect_documents(TRANCHE_PATH)
# # collected_documents = ['/Users/a1234/Desktop/archives/tranche_statement/011490954/011490954_tranche_statement.pdf']
# result = []
#
# for _, doc in zip(tqdm(range(len(collected_documents))), collected_documents):
#     data = collect_tranche_statement_data(doc)
#     result.append(data)
#
# df = pd.DataFrame(result)
# df.to_csv('tranche_statement.csv', index=False)
