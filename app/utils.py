import os
import pathlib
import re
from dataclasses import dataclass
from PIL.PpmImagePlugin import PpmImageFile
from typing import List
import PyPDF2


def collect_documents(directory):
    docs = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if pathlib.Path(f).suffix in ('.pdf',):
                docs.append(os.path.abspath(os.path.join(dirpath, f)))

    return docs


def pattern_match(strings, pattern):
    for string in strings:
        if re.search(pattern, string):
            return True
    return False


def get_list_of_pages(reader):
    text_list = []
    num_pages = len(reader.pages)
    for page_number in range(num_pages):
        page = reader.pages[page_number]
        text_list.append(page.extract_text().replace('\n', " ").strip())

    return text_list


@dataclass
class PdfFile:

    file_name: str
    pdf_reader: PyPDF2.PdfFileReader
    images: List[PpmImageFile]
