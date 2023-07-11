import re
from typing import Dict, List

import PyPDF2
import pandas as pd
import streamlit as st
from stqdm import stqdm

RESTRUCT_AGREEMENT_COLS = [
    "statement_court_order_path",
    "statement_court_order_row_number",
    "statement_court_order_annex"
]


def get_list_of_pages(reader):
    text_list = []
    num_pages = len(reader.pages)
    for page_number in range(num_pages):
        page = reader.pages[page_number]
        text_list.append(page.extract_text().replace('\n', " ").strip())

    return text_list


def extract_annex(s):
    pattern = r'Приложение:(.*?)Представитель ООО «Ситиус»'
    result = re.findall(pattern, s, re.IGNORECASE)
    return result[0] if result else ""


def collect_statement_court_order(pdf_dict: List[Dict[str, PyPDF2.PdfFileReader]]):
    result = []
    for file, _ in zip(pdf_dict, stqdm(range(len(pdf_dict)))):
        try:
            file_name, pdf_reader = file.get('file_name'), file.get('pdf_reader')
            text = "".join(get_list_of_pages(pdf_reader))
            annex = extract_annex(text).strip()
            bullet_points = re.split(r'\s*\d+\.\s', annex)
            bullet_points = [bp.strip() for bp in bullet_points if bp.strip()]

            for index, bullet_point in zip(range(1, (len(bullet_points)) + 1), bullet_points):
                result.append({
                    "statement_court_order_path": file_name,
                    "statement_court_order_row_number": index,
                    "statement_court_order_annex": bullet_point,
                })
        except Exception as e:
            st.error(f'Ошибка разспознавания документа {file_name}')
            result.append(
                {
                    "statement_court_order_path": file_name,
                    "statement_court_order_row_number": None,
                    "statement_court_order_annex": None,
                }
            )

    return pd.DataFrame(result)
