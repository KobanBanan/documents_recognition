import re
from typing import Dict

import PyPDF2
import streamlit as st
from stqdm import stqdm


def classify_agreement(pdf_dict):
    result = []

    with st.spinner('Согласие на обработку персональных данных и обязательства...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):
            try:
                first_page_data = pdf_reader.getPage(0).extractText()
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
                first_page_data = pdf_reader.getPage(0).extractText()
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
                first_page_data = pdf_reader.getPage(0).extractText()
                second_page_data = pdf_reader.getPage(1).extractText()
                eight_page_data = pdf_reader.getPage(7).extractText()

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
                first_page_data = pdf_reader.getPage(0).extractText()
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
                first_page_data = pdf_reader.getPage(0).extractText()
                last_page_data = pdf_reader.getPage(num_pages[-1]).extractText()
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


def classify_documents(pdf_dict: Dict[str, PyPDF2.PdfFileReader]):
    """
    :param pdf_dict:
    :return:
    """
    agreement = classify_agreement(pdf_dict)
    asp = classify_asp(pdf_dict)
    credit_facility_agreement = classify_credit_facility_agreement(pdf_dict)
    statement = classify_statement(pdf_dict)
    tranche_statement = classify_tranche_statement(pdf_dict)

    classified = (
            [a.get('file_name') for a in agreement] + [a.get('file_name') for a in asp] +
            [s.get('file_name') for s in statement] + [c.get('file_name') for c in credit_facility_agreement] +
            [t.get('file_name') for t in tranche_statement]
    )

    unclassified = set(pdf_dict.keys()) ^ set(classified)

    unclassified = [u for u in unclassified if u]

    return {
        'agreement': agreement,
        'asp': asp,
        'credit_facility_agreement': credit_facility_agreement,
        'statement': statement,
        'tranche_statement': tranche_statement,
        'classified': classified,
        'unclassified': unclassified

    }
