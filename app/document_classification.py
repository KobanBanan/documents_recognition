from typing import List

import streamlit as st
from stqdm import stqdm

from docs import RestructAgreement, StatementCourtOrder
from utils import get_list_of_pages, pattern_match, PdfFile


def classify_restruct_agreement(pdf_list: List[PdfFile]):
    result = []
    with st.spinner('Соглашение о реструктуризации задолженности...'):
        for pdf, _ in zip(pdf_list, stqdm(range(len(pdf_list)))):
            first_page_data = pdf.pdf_reader.getPage(0).extract_text()
            if 'Соглашение о реструктуризации задолженности' in first_page_data:
                result.append(RestructAgreement(pdf.file_name, pdf.pdf_reader))

    return result


def classify_statement_court_order(pdf_list: List[PdfFile]):
    main_patterns = (
        'ЗАЯВЛЕНИЕ  о вынесении (о выдаче) судебного приказа о взыскании долга по договору займа',
        'ЗАЯВЛЕНИЕ  о выдаче судебного приказа о взыскании долга по договору займа',
        'ЗАЯВЛЕНИЕ о выдаче судебного приказа о взыскании долга по договору займа',
    )

    other_patterns = (
        'Выдать судебный приказ о взыскании',
        'Вынести судебный приказ о взыскании',
        'Выдать вступивший в законную силу судебный приказ'
    )

    result = []
    with st.spinner('ЗАЯВЛЕНИЕ о выдаче судебного приказа о взыскании долга по договору займа...'):
        for pdf, _ in zip(pdf_list, stqdm(range(len(pdf_list)))):

            pages = get_list_of_pages(pdf.pdf_reader)

            first_page_condition = any([p in pages[0] for p in main_patterns])
            other_conditions = any([pattern_match(pages, c) for c in other_patterns])

            if first_page_condition and other_conditions:
                result.append(StatementCourtOrder(pdf.file_name, pdf.pdf_reader, pdf.pdf_bytes))

    return result


def classify_documents(pdf_list: List[PdfFile]):
    """
    :param pdf_list:
    :return:
    """

    # restruct_agreement = classify_restruct_agreement(pdf_list)
    restruct_agreement = []
    statement_court_order = classify_statement_court_order(pdf_list)

    classified = [r.file_name for r in restruct_agreement] + [s.file_name for s in statement_court_order]
    unclassified = set([pdf.file_name for pdf in pdf_list]) ^ set(classified)
    unclassified = [u for u in unclassified if u]

    return {
        'restruct_agreement': restruct_agreement,
        'statement_court_order': statement_court_order,
        'classified': classified,
        'unclassified': unclassified

    }
