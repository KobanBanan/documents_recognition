import re
from typing import List

import PyPDF2
import pandas as pd
from stqdm import stqdm

from .doc import Document


class RestructAgreement(Document):
    patterns = {
        'restruct_agreement_city': r'г\.\s([^., ]+)',
        'restruct_agreement_date': r'\d{2}\.\d{2}\.\d{4}',
        'restruct_agreement_customer_name': r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)',
        'restruct_agreement_contract_number': r'№\s+(\d+)',
        'restruct_agreement_contract_date': r'\d{2}\.\d{2}\.\d{4}',
        'restruct_agreement_amount': r'(\d+)\s+рублей\s+(\d+)\s+копеек',
        'restruct_agreement_due_date': r'\d{2}\.\d{2}\.\d{4}'
    }

    def __init__(self, file_name: str, pdf_reader: PyPDF2.PdfFileReader):
        super().__init__(file_name, pdf_reader)

    def _extract_agreement_amount(self):
        pattern = self.patterns['restruct_agreement_amount']
        amount = None
        amount_matches = re.search(pattern, self.text_list[0])
        if amount_matches:
            rubles = amount_matches.group(1)
            kopeks = amount_matches.group(2)
            amount = float(rubles + '.' + kopeks)

        return amount

    def _extract_city(self):
        pattern = self.patterns['restruct_agreement_city']
        return self.extract(pattern, self.text_list[0])

    def _extract_dates(self):
        pattern = r'\d{2}\.\d{2}\.\d{4}'
        return self.extract(pattern, self.text_list[0], return_first_match=False) or [None, None, None]

    def _extract_names(self):
        pattern = r'([А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+)'
        return self.extract(pattern, self.text_list[0], return_first_match=False) or [None, None]

    def _extract_contract_number(self):
        pattern = self.patterns['restruct_agreement_contract_number']
        return self.extract(pattern, self.text_list[0])

    @property
    def city(self):
        return self._extract_city()

    @property
    def dates(self):
        return self._extract_dates()

    @property
    def names(self):
        return self._extract_names()

    @property
    def agreement_amount(self):
        return self._extract_agreement_amount()

    @property
    def contract_number(self):
        return self._extract_contract_number()

    def collect_annex_list(self):
        dates = self.dates
        return {
            "file": self.file_name,
            "restruct_agreement_city": self.city,
            "restruct_agreement_date": dates[0],
            "restruct_agreement_customer_name": self.names[0],
            "restruct_agreement_contract_number": self.contract_number,
            "restruct_agreement_contract_date": dates[1],
            "restruct_agreement_amount": self.agreement_amount,
            "restruct_agreement_due_date": dates[2]
        }


def collect_restruct_agreement_data(doc_list: List[RestructAgreement]):
    """
    :param doc_list: List[RestructAgreement]
    :return:
    """
    result = []

    # noinspection PyTypeChecker
    for doc, _ in zip(doc_list, stqdm(range(len(doc_list)))):  # type: RestructAgreement
        result.append(doc.collect_annex_list())

    return pd.DataFrame(result)
