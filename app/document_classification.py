import re
from typing import Dict

import PyPDF2
import streamlit as st
from stqdm import stqdm

from utils import get_list_of_pages, pattern_match


def classify_agreement(pdf_dict):
    result = []

    with st.spinner('Согласие на обработку персональных данных и обязательства...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):
            try:
                first_page_data = pdf_reader.getPage(0).extract_text()
                if bool(re.search('Согласие на обработку персональных данных и обязательства', first_page_data)):
                    result.append({'file_name': file_name, 'pdf_reader': pdf_reader})
            except Exception:
                continue

    return result


def classify_asp(pdf_dict):
    result = []
    with st.spinner('Соглашения об использовании Аналога собственноручной подписи...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):
            try:
                first_page_data = pdf_reader.getPage(0).extract_text()
                if bool(re.search('СОГЛАШЕНИЕ ОБ ИСПОЛЬЗОВАНИИ АНАЛОГА СОБСТВЕННОРУЧНОЙ ПОДПИСИ', first_page_data)):
                    result.append({'file_name': file_name, 'pdf_reader': pdf_reader})
            except Exception:
                continue

    return result


def classify_credit_facility_agreement(pdf_dict):
    result = []
    with st.spinner('Заявление о предоставлении потребительского займа...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):
            try:
                first_page_data = pdf_reader.getPage(0).extract_text()
                second_page_data = pdf_reader.getPage(1).extract_text()
                eight_page_data = pdf_reader.getPage(7).extract_text()

                if all(
                        (
                                bool(re.search('ЗАЯВЛЕНИЕ О ПРЕДОСТАВЛЕНИИ\nПОТРЕБИТЕЛЬСКОГО ЗАЙМА', first_page_data)),
                                bool(re.search('Лимит кредитования', first_page_data)),

                        )
                ):
                    result.append({'file_name': file_name, 'pdf_reader': pdf_reader})
            except Exception:
                continue

    return result


def classify_statement(pdf_dict):
    result = []
    with st.spinner('Заявление о предоставлении потребительского займа...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):
            try:
                first_page_data = pdf_reader.getPage(0).extract_text()
                if bool(re.search('ЗАЯВЛЕНИЕ О ПРЕДОСТАВЛЕНИИ\nПОТРЕБИТЕЛЬСКОГО ЗАЙМА', first_page_data)) and \
                        bool(re.search('Сумма займа', first_page_data)):
                    result.append({'file_name': file_name, 'pdf_reader': pdf_reader})
            except Exception:
                continue

    return result


def classify_tranche_statement(pdf_dict):
    result = []
    with st.spinner('Заявление о предоставлении транша по договору потребительского займа...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):
            try:
                num_pages = range(pdf_reader.numPages)
                first_page_data = pdf_reader.getPage(0).extract_text()
                last_page_data = pdf_reader.getPage(num_pages[-1]).extract_text()
                if all(
                        (
                                bool(re.search('Заявление о предоставлении транша\nпо договору потребительского займа',
                                               first_page_data)),
                                bool(re.search('Транш', first_page_data)),
                                bool(re.search('Сумма Транша', first_page_data)),
                                bool(re.search('Срок Транша', first_page_data)),
                                bool(re.search('Процентная ставка по Траншу', first_page_data)),
                                bool(re.search('График платежей по договору потребительского Займа', last_page_data))
                        ),

                ) or all(
                    (
                            bool(re.search(
                                'Заявление о подписке на пакет Мокка и\nпредоставлении траншей на Виртуальную карту',
                                first_page_data)),
                            bool(re.search('Срок Транша', first_page_data)),
                            bool(re.search('Ставка Транша', first_page_data)),
                            bool(re.search('График платежей по договору потребительского Займа', last_page_data))
                    )
                ):
                    result.append({'file_name': file_name, 'pdf_reader': pdf_reader})
            except Exception:
                continue

    return result


def classify_restruct_agreement(pdf_dict):
    result = []
    with st.spinner('Соглашение о реструктуризации задолженности...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):
            first_page_data = pdf_reader.getPage(0).extract_text()
            if 'Соглашение о реструктуризации задолженности' in first_page_data:
                result.append({'file_name': file_name, 'pdf_reader': pdf_reader})

    return result


def classify_statement_court_order(pdf_dict):
    result = []
    with st.spinner('ЗАЯВЛЕНИЕ о выдаче судебного приказа о взыскании долга по договору займа...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):

            pages = get_list_of_pages(pdf_reader)
            first_page_condition = 'ЗАЯВЛЕНИЕ о выдаче судебного приказа о взыскании долга по договору займа' \
                                   in pages[0]
            other_conditions = [
                pattern_match(pages, c) for c in (
                    'Выдать судебный приказ о взыскании', 'Выдать судебный приказ о взыскании'
                )
            ]

            if first_page_condition and all(other_conditions):
                result.append({'file_name': file_name, 'pdf_reader': pdf_reader})

    return result


def classify_documents(pdf_dict: Dict[str, PyPDF2.PdfFileReader]):
    """
    :param pdf_dict:
    :return:
    """

    restruct_agreement = classify_restruct_agreement(pdf_dict)
    statement_court_order = classify_statement_court_order(pdf_dict)

    classified = [r.get('file_name') for r in restruct_agreement] + [s.get('file_name') for s in statement_court_order]
    unclassified = set(pdf_dict.keys()) ^ set(classified)
    unclassified = [u for u in unclassified if u]

    return {
        'restruct_agreement': restruct_agreement,
        'statement_court_order': statement_court_order,
        'classified': classified,
        'unclassified': unclassified

    }
