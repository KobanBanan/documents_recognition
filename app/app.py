import gc
import zipfile
from io import BytesIO
from typing import List, Tuple

import PyPDF2
import ftfy
import pandas as pd
import streamlit as st

from docs import collect_statement_court_order, \
    collect_statement_court_order_annex_list
from document_classification import classify_documents
from utils import PdfFile

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Function to clear session state and all memory
def clear_memory():
    st.session_state.clear()


# Add a button to the sidebar for clearing memory
st.sidebar.info('При нажатии сессия будет очищена и все данные будут удалены')
st.sidebar.button("Clear Memory", on_click=clear_memory)


def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def download_json(json_data):
    # Download JSON file when the button is clicked
    with open('data.json', 'w') as f:
        f.write(json_data)


def read_pdf(zf: zipfile.ZipFile) -> Tuple[List[PdfFile], List[str]]:
    result = []
    errors = []
    file_list = [file for file in zf.filelist if file.filename.endswith('.pdf')]
    for file in file_list:
        try:
            with zf.open(file.filename) as pdf_file:
                pdf_data = pdf_file.read()
                result.append(
                    PdfFile(
                        ftfy.fix_text(file.filename),
                        PyPDF2.PdfFileReader(BytesIO(pdf_data)),
                        pdf_data
                    )
                )
        except PyPDF2.errors.PdfReadError as e:
            errors.append(file.filename)
            print(f"Error reading {file.filename}: {str(e)}")

    return result, errors


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
        with st.spinner('Чтение арихва и подготовка данных...'):
            if not st.session_state.get('pdf_corpus'):
                pdf_corpus, error_list = read_pdf(zf)
                st.session_state['pdf_corpus'] = pdf_corpus
                st.session_state['error_list'] = error_list
            else:
                pdf_corpus = st.session_state['pdf_corpus']
                error_list = st.session_state['error_list']

        if not pdf_corpus:
            st.warning('В переданном архиве отсутствуют .pdf файлы')
            return

        if error_list:
            st.warning('Внимание! Присутствуют ошибки разбора')
            with st.expander('Непрочитанные файлы'):
                st.write(error_list)

        with st.spinner('Классификация документов..'):
            if not st.session_state.get('classified_documents'):
                classified_documents = classify_documents(pdf_corpus)
                st.session_state['classified_documents'] = classified_documents
            else:
                classified_documents = st.session_state['classified_documents']

        classified_documents_ = classified_documents.get('classified')
        st.markdown('#')
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

            # with st.spinner('Распознавание документов "Соглашение о реструктуризации задолженности..."'):
            #     if not isinstance(st.session_state.get('restruct_agreement'), pd.DataFrame):
            #         restruct_agreement = collect_restruct_agreement_data(classified_documents['restruct_agreement'])
            #         st.session_state['restruct_agreement'] = restruct_agreement
            #     else:
            #         restruct_agreement = st.session_state['restruct_agreement']
            #
            #     if not restruct_agreement.empty:
            #         st.dataframe(restruct_agreement)
            #         restruct_agreement_download = convert_df(restruct_agreement)
            #         st.download_button(
            #             "Скачать restruct_agreement",
            #             restruct_agreement_download,
            #             "restruct_agreement.csv",
            #             "text/csv",
            #             key='download-csv'
            #         )
            #
            #     st.session_state['recognize_btn'] = True

            with st.spinner('Распознавание документов "Заявление о выдаче '
                            'судебного приказа о взыскании долга по договору займа..."'):
                if not isinstance(st.session_state.get('statement_court_order'), pd.DataFrame):
                    statement_court_order_annex_list = collect_statement_court_order_annex_list(
                        classified_documents['statement_court_order'])

                    statement_court_order, statement_court_order_errors = collect_statement_court_order(
                        classified_documents['statement_court_order']
                    )
                    st.session_state['statement_court_order_annex_list'] = statement_court_order_annex_list
                    st.session_state['statement_court_order'] = statement_court_order
                    st.session_state['statement_court_order_errors'] = statement_court_order_errors
                else:
                    statement_court_order_annex_list = st.session_state['statement_court_order_annex_list']
                    statement_court_order = st.session_state['statement_court_order']
                    statement_court_order_errors = st.session_state['statement_court_order_errors']

                st.subheader('Заявление на вынесение судебного приказа')

                st.markdown("---")
                st.markdown('##### Список приложений')
                if not statement_court_order_annex_list.empty:
                    st.dataframe(statement_court_order_annex_list)
                    statement_court_order_annex_list_download = convert_df(statement_court_order_annex_list)
                    st.download_button(
                        "Скачать statement_court_order_annex_list.csv",
                        statement_court_order_annex_list_download,
                        "statement_court_order_annex_list.csv",
                        "text/csv",
                        key='download-csv'
                    )

                    st.download_button(
                        label='Скачать statement_court_order_annex_list.json',
                        data=statement_court_order_annex_list.to_json(orient='records'),
                        file_name='statement_court_order_annex_list.json',
                        mime='application/json'
                    )
                st.session_state['recognize_btn'] = True

                st.markdown("---")
                st.markdown('##### Содержимое заявлений')
                if not statement_court_order.empty:
                    st.dataframe(statement_court_order)
                    statement_court_order_download = convert_df(statement_court_order)
                    st.download_button(
                        "Скачать statement_court_order.csv",
                        statement_court_order_download,
                        "statement_court_order.csv",
                        "text/csv",
                        key='download-csv'
                    )
                    st.download_button(
                        label='Скачать statement_court_order.json',
                        data=statement_court_order.to_json(orient='records'),
                        file_name='statement_court_order.json',
                        mime='application/json'
                    )

                st.markdown("---")
                st.markdown('##### Ошибки')
                if not statement_court_order_errors.empty:
                    with st.expander('[ОШИБКИ]: Заявление на вынесение судебного приказа'):
                        st.write(statement_court_order_errors)
                        statement_court_order_errors_download = convert_df(statement_court_order_errors)
                        st.download_button(
                            "Скачать statement_court_order_errors.csv",
                            statement_court_order_errors_download,
                            "statement_court_order_errors.csv",
                            "text/csv",
                            key='download-csv'
                        )


if __name__ == '__main__':
    main()
