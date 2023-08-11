from typing import Dict

import PyPDF2
import streamlit as st
from stqdm import stqdm

from docs import RestructAgreement, StatementCourtOrder
from utils import get_list_of_pages, pattern_match


def classify_restruct_agreement(pdf_dict):
    result = []
    with st.spinner('Соглашение о реструктуризации задолженности...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):
            first_page_data = pdf_reader.getPage(0).extract_text()
            if 'Соглашение о реструктуризации задолженности' in first_page_data:
                result.append(RestructAgreement(file_name, pdf_reader))

    return result


def classify_statement_court_order(pdf_dict):
    main_patterns = (
        'ЗАЯВЛЕНИЕ  о вынесении (о выдаче) судебного приказа о взыскании долга по договору займа',
        'ЗАЯВЛЕНИЕ о выдаче судебного приказа о взыскании долга по договору займа'
    )

    other_patterns = ('Выдать судебный приказ о взыскании', 'Вынести судебный приказ о взыскании')

    result = []
    with st.spinner('ЗАЯВЛЕНИЕ о выдаче судебного приказа о взыскании долга по договору займа...'):
        for (file_name, pdf_reader), _ in zip(pdf_dict.items(), stqdm(range(len(pdf_dict)))):

            pages = get_list_of_pages(pdf_reader)

            first_page_condition = any([p in pages[0] for p in main_patterns])
            other_conditions = any([pattern_match(pages, c) for c in other_patterns])

            if first_page_condition and other_conditions:
                result.append(StatementCourtOrder(file_name, pdf_reader))

    return result


def classify_documents(pdf_dict: Dict[str, PyPDF2.PdfFileReader]):
    """
    :param pdf_dict:
    :return:
    """

    restruct_agreement = classify_restruct_agreement(pdf_dict)
    statement_court_order = classify_statement_court_order(pdf_dict)

    classified = [r.file_name for r in restruct_agreement] + [s.file_name for s in statement_court_order]
    unclassified = set(pdf_dict.keys()) ^ set(classified)
    unclassified = [u for u in unclassified if u]

    return {
        'restruct_agreement': restruct_agreement,
        'statement_court_order': statement_court_order,
        'classified': classified,
        'unclassified': unclassified

    }
