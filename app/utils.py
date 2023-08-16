import os
import pathlib
import re
from copy import deepcopy
from dataclasses import dataclass
from typing import List

import PyPDF2
import streamlit as st
from PIL.PpmImagePlugin import PpmImageFile
from pdf2image import convert_from_bytes
from zipfile import ZipFile


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


def extract_image(zf: ZipFile, file_name: str, poppler_path: str):
    try:
        result = convert_from_bytes(zf.read(file_name)) if not poppler_path \
            else convert_from_bytes(zf.read(file_name), poppler_path=poppler_path)

        first_image = deepcopy(result[0])
        del result
        return first_image
    except Exception as e:
        st.warning(f'Ошибка обработки файла {file_name}')


@dataclass
class PdfFile:
    file_name: str
    pdf_reader: PyPDF2.PdfFileReader
    images: List[PpmImageFile]
