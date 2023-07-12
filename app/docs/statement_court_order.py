import re
from typing import List, Dict

import PyPDF2
import pandas as pd
from stqdm import stqdm

from .doc import Document


class StatementCourtOrder(Document):
    patterns = {
        "statement_court_order_annex": re.compile(r'Приложение:(.*?)Представитель ООО «Ситиус»'),
    }

    def __init__(self, file_name: str, pdf_reader: PyPDF2.PdfFileReader):
        super().__init__(file_name, pdf_reader)

    def extract_annex(self):
        pattern = self.patterns['statement_court_order_annex']
        result = re.findall(pattern, self.text)
        return result[0] if result else self.DEFAULT_EXTRACT_VAlUE

    def parse_document(self) -> List[Dict]:
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


def collect_statement_court_order(doc_list: List[StatementCourtOrder]):
    result = []
    # noinspection PyTypeChecker
    for doc, _ in zip(doc_list, stqdm(range(len(doc_list)))):  # type: StatementCourtOrder
        result.extend(doc.parse_document())

    return pd.DataFrame(result)
