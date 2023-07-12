from typing import Dict

import PyPDF2
import streamlit as st
from stqdm import stqdm

from utils import get_list_of_pages, pattern_match


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
