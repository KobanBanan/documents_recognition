import re
from typing import Tuple, Iterable, Dict

import PyPDF2


class Document:
    patterns = {}
    DEFAULT_EXTRACT_VAlUE = str()

    def __init__(self, file_name: str, pdf_reader: PyPDF2.PdfFileReader):
        self.file_name = file_name
        self.text_list, self.text = self._get_list_of_pages(pdf_reader)
        self.pdf_reader = pdf_reader

    @staticmethod
    def _get_list_of_pages(reader) -> Tuple[Iterable[str], str]:
        text_list = []
        num_pages = len(reader.pages)
        for page_number in range(num_pages):
            page = reader.pages[page_number]
            text_list.append(page.extract_text().replace('\n', " ").strip())

        return text_list, " ".join(text_list)

    def empty_return(self) -> Dict:
        res = {key: None for key in self.patterns.keys()}
        res.update({'file': self.file_name})
        return res

    def extract(self, pattern, text, return_first_match=True, return_value=None):
        result = re.findall(pattern, text, re.IGNORECASE)
        if return_first_match:
            return result[0].strip() if result else self.DEFAULT_EXTRACT_VAlUE
        return result or (return_value or self.DEFAULT_EXTRACT_VAlUE)

    def extract_mass(self, pattern_list: Iterable[str], text):
        for pattern in pattern_list:
            res = self.extract(pattern, text)
            if res:
                return res

        return self.DEFAULT_EXTRACT_VAlUE

    def collect_annex_list(self):
        pass
