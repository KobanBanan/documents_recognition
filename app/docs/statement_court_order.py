import os
import re
from copy import deepcopy
from typing import List, Dict

import PyPDF2
import pandas as pd
import streamlit as st
from pdf2image import convert_from_bytes
from pyzbar.pyzbar import decode
from stqdm import stqdm

from .doc import Document
from .utils import collect_garbage


class StatementCourtOrder(Document):
    patterns = {
        "statement_court_order_annex": re.compile(r'Приложение:(.*?)Представитель ООО «Ситиус»'),
    }

    def __init__(self, file_name: str, pdf_reader: PyPDF2.PdfFileReader, pdf_bytes: bytes):
        super().__init__(file_name, pdf_reader)
        self.image = self._extract_image(pdf_bytes, os.environ.get('POPPLER_PATH'))

    def extract_annex(self):
        pattern = self.patterns['statement_court_order_annex']
        result = re.findall(pattern, self.text)
        return result[0] if result else self.DEFAULT_EXTRACT_VAlUE

    @staticmethod
    def _extract_image(pdf_bytes: bytes, poppler_path: str):
        try:
            result = convert_from_bytes(pdf_bytes) if not poppler_path \
                else convert_from_bytes(pdf_bytes, poppler_path=poppler_path)

            first_image = deepcopy(result[0])
            del result
            return first_image
        except Exception:
            return

    @collect_garbage
    def collect_annex_list(self) -> List[Dict]:
        result = []
        annex = self.extract_annex().strip()
        bullet_points = re.split(r'\s*\d+\.\s', annex)
        bullet_points = [bp.strip() for bp in bullet_points if bp.strip()]
        for index, bullet_point in zip(range(1, (len(bullet_points)) + 1), bullet_points):
            result.append({
                "statement_court_order_path": self.file_name,
                "statement_court_order_row_number": index,
                "statement_court_order_annex": bullet_point,
            })

        return result
        # noinspection PyTypeChecker

    def get_barcode(self):
        try:
            return decode(self.image)[0].data.decode()
        except (TypeError, IndexError):
            st.warning(f"Ошибка извлечения bar-code'а {self.file_name}")
            return None

    @collect_garbage
    def parse_document(self):
        first_page_data = self.text_list[0]
        passport = self.extract(r'Паспорт: серия \d+ № \d+', first_page_data)
        name_full = self.extract(r"Должник:(.*?)Паспорт", first_page_data)
        dates = self.extract(
            r'\b\d{2}\.\d{2}\.\d{4}\b',
            first_page_data,
            return_first_match=False,
            return_value=[None, None]
        )
        addressee_appellation = self.extract(r'(.*?)\s*Адрес:', first_page_data)
        court_address = self.extract(r"Адрес:([\s\S]+?)Взыскатель:", first_page_data)

        contract_number = self.extract_mass((r"№\s*\d+-\d+", r'договору потребительского займа(.*?)от',
                                             r'Договор займа\)(.*?)от'), first_page_data)

        barcode = self.get_barcode()

        return {
            'statement_court_order_path': self.file_name,
            "statement_court_order_barcode_value": barcode,
            "statement_court_order_debtor_name_full": name_full,
            "statement_court_order_debtor_birth_date": dates[0],
            "statement_court_order_debtor_passport_full_number": passport,
            "statement_court_order_addressee_appellation": addressee_appellation,
            "statement_court_order_court_address_string": court_address,
            "statement_court_order_loan_contract_number": contract_number,
            "statement_court_order_loan_contract_date": dates[1]
        }


def collect_statement_court_order_annex_list(doc_list: List[StatementCourtOrder]):
    result = []
    # noinspection PyTypeChecker
    for doc, _ in zip(doc_list, stqdm(range(len(doc_list)))):  # type: StatementCourtOrder
        result.extend(doc.collect_annex_list())

    return pd.DataFrame(result)


def collect_statement_court_order(doc_list: List[StatementCourtOrder]):
    result = []
    # noinspection PyTypeChecker
    for doc, _ in zip(doc_list, stqdm(range(len(doc_list)))):  # type: StatementCourtOrder
        result.append(doc.parse_document())

    return pd.DataFrame(result)
