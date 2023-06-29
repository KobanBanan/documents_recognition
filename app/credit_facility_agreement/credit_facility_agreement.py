import os
import re
from pathlib import Path
from typing import Dict, List

import PyPDF2
import pandas as pd
import streamlit as st
from stqdm import stqdm

CREDIT_FACILITY_AGREEMENT_COLS = [
    "ContractNumber",
    "ContractDate",
    "LastName",
    "FirstName",
    "MiddleName",
    "BirthDate",
    "PassportSeries",
    "PassportNumber",
    "LoanAmount",
    "CreditLimit",
    "PercentRate",
    "FullAmountPercent",
    "FullAmountMoney",
    "CreditorName",
    "OrderNumber",
    "OrderDate",
    "SignatureDate",
    "SigningDate"
]
# CREDIT_FACILITY_AGREEMENT_PATH = '/Users/a1234/Desktop/PeedoRevoTest'

contract_number_regex = re.compile(r'(?<=№)(.*?)(?= №)')
loan_amount_regex = re.compile('(?<=)(.*?)(?=коп.)')
percent_rate_regex = re.compile('(?<=заемщику индивидуальных условий)(.*?)(?=% ПРОЦЕНТОВ ГОДОВЫХ)')
full_percent_rate_regex = re.compile(r'(?<=\))(.*?)(?= % годовых)')
credit_limit_regex = re.compile(r'(?<=Лимит кредитования:)(.*?)(?=руб)')
birthday_regex = re.compile(r'(?<=,)[^,]+(?=года)')
passport_regex = re.compile(r"паспорт: серия (\d{4})\s* номер ?\s*(\d{6})")
sign_date_regex = re.compile(r"Дата подписания: \s*(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})\s*$")
signature_date_regex = re.compile(r'(?<=\[)\d{1,2}\.\d{1,2}\.\d{2}(?:\d{2})?(?=\])')
name_regex = re.compile(r'(?<=\))(.*?)(?=,)')
creditor_name_regex = re.compile(r'(?<=директора)(.*?)(?=№)')
order_number_regex = re.compile(r'(?<=№ )(.*?)(?=от)')
order_date_regex = re.compile(r'(?<=от )(.*?)(?=г)')

contract_number_contract_date_1 = re.compile('(?<=№)(.*?)(?= от)')
contract_number_contract_date_2 = re.compile('(?<=от )(.*?)(?=По)')
contract_number_contract_date_3 = re.compile('(?<=от )(.*?)(?=№)')

fio_1 = re.compile(r'(?<=а\))(.*?)(?=,)')
full_amount_percent_1 = re.compile(r'(?<=\))(.*?)(?= %годовых)')
creditor_name_1 = re.compile(r'(?<=бщество – )(.*?)(?=\(ОГРН)')
order_date_1 = re.compile(r'(?<=с )(.*?)(?=г)')


def collect_documents(directory):
    docs = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if Path(f).suffix in ('.pdf',):
                docs.append(os.path.abspath(os.path.join(dirpath, f)))

    return docs


def extract(s, p):
    match = re.search(p, s)
    if match:
        return match.group().strip()
    return ""


def collect_contract_number_and_date(s):
    match = re.search(contract_number_regex, s.replace("\n", " "))
    if match:
        return match.group().split('от')

    return None, None


def extarc_load_amount(s):
    match = re.search(loan_amount_regex, s)
    if match:
        return float(".".join(match.group().split('руб.')).strip().replace(" ", ""))


def extract_percent_rate(s):
    match = re.search(percent_rate_regex, s)
    if match:
        return match.group().strip()


def extract_full_percent_rate(s):
    match = re.search(full_percent_rate_regex, s.replace('\n', ''))
    if match:
        return match.group().strip()


def extract_credit_limit(s):
    match = re.search(credit_limit_regex, s)
    if match:
        return match.group().strip()


def extract_birthday(s):
    match = re.search(birthday_regex, s)
    if match:
        return match.group().strip()


def extract_passport(s):
    """
    Extract passport by mask
    :param s:
    :return:
    """

    match = re.search(passport_regex, s.replace("\n", " "))
    if match:
        res = match.groups()
        return res[0].strip(), res[1].strip()

    return None, None


def extract_sign_date(s):
    match = re.search(sign_date_regex, s)
    if match:
        return ".".join(match.groups())


def extract_signature_date(s):
    match = re.search(signature_date_regex, s)
    if match:
        return match.group()


def extract_name(s):
    """
    Extract name from raw string
    :param s:
    :return:
    """
    match = re.search(name_regex, s)
    if match:
        return [n for n in match.group().split(' ') if n]

    return [None, None, None]


def extract_creditor_name(s):
    match = re.search(creditor_name_regex, s)
    if match:
        return match.group().strip()


def extract_order_number(s):
    match = re.search(order_number_regex, s)
    if match:
        return match.group().strip()


def extract_order_date(s):
    match = re.search(order_date_regex, s)
    if match:
        return match.group().strip()


def collect_credit_facility_agreement_data(pdf_dict: List[Dict[str, PyPDF2.PdfFileReader]]):
    """

    :param pdf_dict:
    :return:
    """
    contract_number = None
    contract_date = None
    last = None
    first = None
    middle = None
    birthday = None
    series = None
    number = None
    loan_amount = None
    percent_rate = None
    full_amount_percent = None
    full_amount_money = None
    creditor_name = None
    order_number = None
    order_date = None
    credit_limit = None
    signature_date = None
    signing_date = None

    result = []
    for file, _ in zip(pdf_dict, stqdm(range(len(pdf_dict)))):
        file_name, pdf_reader = file.get('file_name'), file.get('pdf_reader')
        try:
            num_pages = pdf_reader.numPages

            # Pages
            first_page_data = pdf_reader.getPage(0).extractText()
            second_page_data = pdf_reader.getPage(1).extractText()
            third_page_data = pdf_reader.getPage(2).extractText()
            six_page_data = pdf_reader.getPage(5).extractText()
            seven_page_data = pdf_reader.getPage(6).extractText()
            eight_page_data = pdf_reader.getPage(7).extractText()
            nine_page_data = pdf_reader.getPage(8).extractText()

            # Permanent data
            # CreditLimit 10
            # --------------------------------------------------------------------------------------------------------------
            credit_limit = extract_credit_limit(first_page_data)

            # Dates 17, 18
            # --------------------------------------------------------------------------------------------------------------
            signature_date = extract_signature_date(first_page_data)
            signing_date = extract_sign_date(first_page_data)

            if num_pages == 9:

                # ContractNumber 1, ContractDate 2
                # --------------------------------------------------------------------------------------------------------------
                contract_number, contract_date = collect_contract_number_and_date(third_page_data)

                # FIO 3, 4, 5
                # --------------------------------------------------------------------------------------------------------------
                last, first, middle = extract_name(eight_page_data)

                # Birthday 6
                # --------------------------------------------------------------------------------------------------------------
                birthday = extract_birthday(eight_page_data)

                # Passport 7, 8
                # --------------------------------------------------------------------------------------------------------------
                passport = extract_passport(eight_page_data)
                series, number = passport

                # LoanAmount 9
                # --------------------------------------------------------------------------------------------------------------
                loan_amount = extarc_load_amount(second_page_data)

                # Percent 11, 12
                # --------------------------------------------------------------------------------------------------------------
                percent_rate = extract_percent_rate(third_page_data)
                full_amount_percent = extract_full_percent_rate(second_page_data)

                # FullAmountMoney 13
                # --------------------------------------------------------------------------------------------------------------
                full_amount_money = loan_amount

                # CreditorName, OrderNumber, OrderDate 15, 16
                # --------------------------------------------------------------------------------------------------------------
                creditor_name = None
                order_number = None
                order_date = None

            elif num_pages in (21, 23, 25, 24, 26, 27, 31, 35, 32, 36,):

                twenty_one_page_data = pdf_reader.getPage(20).extractText()

                mapping = {
                    21: {
                        'creditor_name': eight_page_data.replace('\n', ''),
                        'order_number': "",
                        'order_date': twenty_one_page_data
                    },
                    23: {
                        'creditor_name': eight_page_data.replace('\n', ''),
                        'order_number': "",
                        'order_date': twenty_one_page_data
                    },
                    24: {
                        'creditor_name': seven_page_data.replace('\n', ''),
                        'order_number': seven_page_data.replace('\n', ''),
                        'order_date': seven_page_data.replace('\n', '')
                    },
                    25: {
                        'creditor_name': seven_page_data.replace('\n', ''),
                        'order_number': seven_page_data.replace('\n', ''),
                        'order_date': seven_page_data.replace('\n', '')
                    },
                    26: {
                        'creditor_name': eight_page_data.replace('\n', ''),
                        'order_number': eight_page_data.replace('\n', ''),
                        'order_date': eight_page_data.replace('\n', '')
                    },
                    27: {
                        'creditor_name': eight_page_data.replace('\n', ''),
                        'order_number': eight_page_data.replace('\n', ''),
                        'order_date': eight_page_data.replace('\n', '')
                    },
                    31: {
                        'creditor_name': seven_page_data.replace('\n', ''),
                        'order_number': seven_page_data.replace('\n', ''),
                        'order_date': seven_page_data.replace('\n', '')
                    },
                    32: {
                        'creditor_name': eight_page_data.replace('\n', ''),
                        'order_number': eight_page_data.replace('\n', ''),
                        'order_date': eight_page_data.replace('\n', '')
                    },
                    35: {
                        'creditor_name': eight_page_data.replace('\n', ''),
                        'order_number': eight_page_data.replace('\n', ''),
                        'order_date': eight_page_data.replace('\n', '')
                    },
                    36: {
                        'creditor_name': eight_page_data.replace('\n', ''),
                        'order_number': eight_page_data.replace('\n', ''),
                        'order_date': eight_page_data.replace('\n', '')
                    },
                }

                # ContractNumber 1, ContractDate 2
                # --------------------------------------------------------------------------------------------------------------
                contract_number, contract_date = (
                    extract(second_page_data, contract_number_contract_date_1),
                    extract(second_page_data.replace('\n', ""), contract_number_contract_date_2) or
                    extract(second_page_data.replace('\n', ""), contract_number_contract_date_3)
                )

                # FIO 3, 4, 5
                # --------------------------------------------------------------------------------------------------------------
                fio = (
                        extract(six_page_data, fio_1) or
                        extract(nine_page_data, fio_1) or
                        extract(seven_page_data, fio_1)
                )
                try:
                    last, first, middle = fio.split(" ")
                except ValueError:
                    last, first, middle = None, None, None

                # Birthday 6
                # --------------------------------------------------------------------------------------------------------------
                birthday = extract_birthday(six_page_data) or extract_birthday(seven_page_data)

                # Passport 7, 8
                # --------------------------------------------------------------------------------------------------------------
                passport = (
                        extract_passport(six_page_data) or extract_passport(nine_page_data) or extract_passport(
                    seven_page_data)
                )
                series, number = passport

                # LoanAmount 9
                # --------------------------------------------------------------------------------------------------------------
                loan_amount = extarc_load_amount(second_page_data)

                # Percent 11, 12
                # --------------------------------------------------------------------------------------------------------------
                percent_rate = extract_percent_rate(third_page_data.replace('\n', ' '))
                full_amount_percent = (
                        extract_full_percent_rate(second_page_data) or
                        extract(second_page_data.replace("\n", " "), full_amount_percent_1)
                )

                # FullAmountMoney 13
                # --------------------------------------------------------------------------------------------------------------
                full_amount_money = loan_amount

                # CreditorName, OrderNumber, OrderDate 14, 15, 16
                # --------------------------------------------------------------------------------------------------------------
                creditor_name = (
                        extract_creditor_name(mapping[num_pages]['creditor_name']) or
                        extract(mapping[num_pages]['creditor_name'], creditor_name_1)
                )
                order_number = extract_order_number(mapping[num_pages]['order_number'])
                order_date = (
                        extract_order_date(mapping[num_pages]['order_date']) or
                        extract(mapping[num_pages]['order_date'], order_date_1)
                )
            result.append({
                "file": file_name,
                "ContractNumber": contract_number,
                "ContractDate": contract_date,
                "LastName": last,
                "FirstName": first,
                "MiddleName": middle,
                "BirthDate": birthday,
                "PassportSeries": series,
                "PassportNumber": number,
                "LoanAmount": loan_amount,
                "CreditLimit": credit_limit,
                "PercentRate": percent_rate,
                "FullAmountPercent": full_amount_percent,
                "FullAmountMoney": full_amount_money,
                "CreditorName": creditor_name,
                "OrderNumber": order_number,
                "OrderDate": order_date,
                "SignatureDate": signature_date,
                "SigningDate": signing_date,
            })
        except Exception as e:
            # st.error(f'Ошибка разспознавания документа {file_name}')
            result.append({
                "file": file_name,
                "ContractNumber": contract_number,
                "ContractDate": contract_date,
                "LastName": last,
                "FirstName": first,
                "MiddleName": middle,
                "BirthDate": birthday,
                "PassportSeries": series,
                "PassportNumber": number,
                "LoanAmount": loan_amount,
                "CreditLimit": credit_limit,
                "PercentRate": percent_rate,
                "FullAmountPercent": full_amount_percent,
                "FullAmountMoney": full_amount_money,
                "CreditorName": creditor_name,
                "OrderNumber": order_number,
                "OrderDate": order_date,
                "SignatureDate": signature_date,
                "SigningDate": signing_date,
            })

    return pd.DataFrame(result)

# if __name__ == '__main__':
#     collected_documents = collect_documents(CREDIT_FACILITY_AGREEMENT_PATH)[:100]
#     result = []
#     with Pool(cpu_count()) as p:
#         r = tqdm(p.imap(collect_credit_facility_agreement_data, collected_documents), total=len(collected_documents))
#
#     df = pd.DataFrame(list(r))
#     df.to_csv('credit_facility_agreement.csv', index=False)

# result = []
# collected_documents = collect_documents(CREDIT_FACILITY_AGREEMENT_PATH)
# for _, doc in zip(tqdm(range(len(collected_documents))), collected_documents):
#     data = collect_credit_facility_agreement_data(doc)
#     result.append(data)
#
# df = pd.DataFrame(list(result))
# df.to_csv('credit_facility_agreement.csv', index=False)
