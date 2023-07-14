import zipfile
from io import BytesIO
from typing import Dict

import PyPDF2
import ftfy
import pandas as pd
import streamlit as st

from docs import collect_restruct_agreement_data, collect_statement_court_order
from document_classification import classify_documents

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def read_pdf(zf: zipfile.ZipFile):
    result = {}
    file_list = [file for file in zf.filelist if file.filename.endswith('.pdf')]
    for file in file_list:
        try:
            result.update(
                {ftfy.fix_text(zf.getinfo(file.filename).filename): PyPDF2.PdfFileReader(BytesIO(zf.read(file)))})
        except PyPDF2.errors.PdfReadError:
            st.warning(f'Ошибка чтения файла {file.filename}')

    return result


def main():
    st.header("Сервис распознавания документов (DEMO)")
    st.subheader("FAQ")

    with st.expander("Какие типы документов поддерживаются?"):
        st.write(
            """
            1. Соглашение о реструктуризации задолженности
            2. Заявление о выдаче судебного приказа о взыскании долга по договору займа

            """
        )

    with st.expander("Какие файлы поддерживаются?"):
        st.write(
            """ .PDF """
        )

    uploaded_zip = st.file_uploader('Загрузите архив', type="zip", key='uploaded_zip')
    if uploaded_zip:
        zf = zipfile.ZipFile(uploaded_zip)

        pdf_corpus: Dict[str, PyPDF2.PdfFileReader] = read_pdf(zf)

        if not pdf_corpus:
            st.warning('В переданном архиве отсутствуют .pdf файлы')
            return

        with st.spinner('Классификация документов..'):
            if not st.session_state.get('classified_documents'):
                classified_documents = classify_documents(pdf_corpus)
                st.session_state['classified_documents'] = classified_documents
            else:
                classified_documents = st.session_state['classified_documents']

        classified_documents_ = classified_documents.get('classified')

        if classified_documents.get('unclassified'):
            with st.expander('Неклассифицированные документы'):
                unclassified_documents = classified_documents['unclassified']

                if not classified_documents_:
                    st.write('Документы не были найдены')
                    return

                st.write(unclassified_documents)

        if classified_documents.get('classified'):
            with st.expander('Классифицированные документы'):
                st.write(classified_documents_)

        recognize_btn = st.button("Распознать документы")
        if not st.session_state.get('recognize_btn'):
            st.session_state['recognize_btn'] = recognize_btn

        if st.session_state.get('recognize_btn'):

            with st.spinner('Распознавание документов "Соглашение о реструктуризации задолженности..."'):
                if not isinstance(st.session_state.get('restruct_agreement'), pd.DataFrame):
                    restruct_agreement = collect_restruct_agreement_data(classified_documents['restruct_agreement'])
                    st.session_state['restruct_agreement'] = restruct_agreement
                else:
                    restruct_agreement = st.session_state['restruct_agreement']

                if not restruct_agreement.empty:
                    st.dataframe(restruct_agreement)
                    restruct_agreement_download = convert_df(restruct_agreement)
                    st.download_button(
                        "Скачать restruct_agreement",
                        restruct_agreement_download,
                        "restruct_agreement.csv",
                        "text/csv",
                        key='download-csv'
                    )

                st.session_state['recognize_btn'] = True

            with st.spinner('Распознавание документов "Заявление о выдаче '
                            'судебного приказа о взыскании долга по договору займа..."'):
                if not isinstance(st.session_state.get('statement_court_order'), pd.DataFrame):
                    statement_court_order = collect_statement_court_order(classified_documents['statement_court_order'])
                    st.session_state['statement_court_order'] = statement_court_order
                else:
                    statement_court_order = st.session_state['statement_court_order']

                if not statement_court_order.empty:
                    st.dataframe(statement_court_order)
                    statement_court_order_download = convert_df(statement_court_order)
                    st.download_button(
                        "Скачать statement_court_order",
                        statement_court_order_download,
                        "statement_court_order.csv",
                        "text/csv",
                        key='download-csv'
                    )

                st.session_state['recognize_btn'] = True


if __name__ == '__main__':
    main()
