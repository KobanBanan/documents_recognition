import os
import pathlib
import re
from typing import Dict, List

import PyPDF2
import pandas as pd
import streamlit as st
from stqdm import stqdm


RESTRUCT_AGREEMENT_COLS = [
    "restruct_agreement_city",
    "restruct_agreement_date"
    "restruct_agreement_customer_name",
    "restruct_agreement_contract_number",
    "restruct_agreement_contract_date",
    "restruct_agreement_amount",
    "restruct_agreement_due_date"
]


def collect_restruct_agreement_data(pdf_dict: List[Dict[str, PyPDF2.PdfFileReader]]):
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

            last_page = pdf_reader.getPage(num_pages[-1])
            last_page_data = last_page.extractText()

            # extract_data from first page

            result.append({
                "restruct_agreement_city": file_name,
                "restruct_agreement_date": "",
                "restruct_agreement_customer_name": "",
                "restruct_agreement_contract_number": "",
                "restruct_agreement_contract_date": "",
                "restruct_agreement_amount": "",
                "restruct_agreement_due_date": ""
            })

        except Exception as e:
            st.error(f'Ошибка разспознавания документа {file_name}')
            result.append({
                "file": file_name,
                "restruct_agreement_city": None,
                "restruct_agreement_date": None,
                "restruct_agreement_customer_name": None,
                "restruct_agreement_contract_number": None,
                "restruct_agreement_contract_date": None,
                "restruct_agreement_amount": None,
                "restruct_agreement_due_date": None
            })

    return pd.DataFrame(result)
