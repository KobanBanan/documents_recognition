import zipfile
from io import BytesIO
from typing import Dict

import PyPDF2
import pandas as pd
import streamlit as st

from agreement.agreement import collect_agreement_data
from asp.asp import collect_asp_data
from credit_facility_agreement.credit_facility_agreement import collect_credit_facility_agreement_data
from document_classification import classify_documents
from statement.statement import collect_statement_data
from tranche_statement import collect_tranche_statement_data, collect_tranche_statement_schedule_data
import time

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def main():
    st.header("Сервис распознавания документов (DEMO)")
    st.subheader("FAQ")

    with st.expander("Какие типы документов поддерживаются?"):
        st.write(
            """
            1. Согласие на обработку персональных данных и обязательства
            2. Соглашение об использовании Аналога собственноручной подписи
            3. Заявления о предоставлении потребительского займа
            4. Заявление о предоставлении транша по договору потребительского займа
            5. График платежей по договору потребительского Займа

            """
        )

    with st.expander("Какие файлы поддерживаются?"):
        st.write(
            """ .PDF """
        )

    uploaded_zip = st.file_uploader('Загрузите архив', type="zip", key='uploaded_zip')
    if uploaded_zip:
        zf = zipfile.ZipFile(uploaded_zip)
        pdf_corpus: Dict[str, PyPDF2.PdfFileReader] = {
            file.filename:
                PyPDF2.PdfFileReader(BytesIO(zf.read(file))) for file in zf.filelist if
            file.filename.endswith('.pdf')
        }

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
            with st.spinner(
                    'Распознавание документов "Соглашения об использовании Аналога собственноручной подписи..'):
                if not isinstance(st.session_state.get('asp_data'), pd.DataFrame):
                    time.sleep(1)
                    asp_data = pd.read_csv('demo_examples/asp.csv')
                    st.session_state['asp_data'] = asp_data
                else:
                    asp_data = st.session_state['asp_data']
                st.dataframe(asp_data)
                asp_download = convert_df(asp_data)
                st.download_button(
                    "Скачать asp.csv",
                    asp_download,
                    "asp.csv",
                    "text/csv",
                    key='download-csv'
                )

                st.session_state['recognize_btn'] = True

            with st.spinner(
                    'Распознавание документов "Согласие на обработку персональных данных и обязательства..'):
                if not isinstance(st.session_state.get('agreement_data'), pd.DataFrame):
                    time.sleep(1)
                    agreement_data = pd.read_csv('demo_examples/agreement.csv')
                    st.session_state['agreement_data'] = agreement_data
                else:
                    agreement_data = st.session_state['agreement_data']

                st.dataframe(agreement_data)
                agreement_download = convert_df(agreement_data)
                st.download_button(
                    "Скачать agreement.csv",
                    agreement_download,
                    "agreement.csv",
                    "text/csv",
                    key='download-csv'
                )
                st.session_state['recognize_btn'] = True

            with st.spinner('Распознавание документов "Заявление о предоставлении потребительского займа..'):
                if not isinstance(st.session_state.get('statement_data'), pd.DataFrame):
                    time.sleep(1)
                    statement_data = pd.read_csv('demo_examples/statement.csv')
                    st.session_state['statement_data'] = statement_data
                else:
                    statement_data = st.session_state['statement_data']

                st.dataframe(statement_data)
                statement_download = convert_df(statement_data)
                st.download_button(
                    "Скачать statement.csv",
                    statement_download,
                    "statement.csv",
                    "text/csv",
                    key='download-csv'
                )
                st.session_state['recognize_btn'] = True

            with st.spinner('Распознавание документов "Заявление о предоставлении потребительского займа..'):
                if not isinstance(st.session_state.get('credit_facility_agreement_data'), pd.DataFrame):
                    time.sleep(1)
                    credit_facility_agreement_data = pd.read_csv('demo_examples/credit_facility_agreement_data.csv')
                    st.session_state['credit_facility_agreement_data'] = credit_facility_agreement_data
                else:
                    credit_facility_agreement_data = st.session_state['credit_facility_agreement_data']

                st.dataframe(credit_facility_agreement_data)
                credit_facility_agreement_download = convert_df(credit_facility_agreement_data)
                st.download_button(
                    "Скачать credit_facility_agreement.csv",
                    credit_facility_agreement_download,
                    "credit_facility_agreement_data.csv",
                    "text/csv",
                    key='download-csv'
                )
                st.session_state['recognize_btn'] = True

            with st.spinner('Распознавание документов "График платежей по договору потребительского Займа.."'):
                if not isinstance(st.session_state.get('tranche_statement_schedule_data'), pd.DataFrame):
                    time.sleep(1)
                    tranche_statement_schedule_data = pd.read_csv('demo_examples/tranche_statement_schedule.csv')
                    st.session_state['tranche_statement_schedule_data'] = tranche_statement_schedule_data
                else:
                    tranche_statement_schedule_data = st.session_state['tranche_statement_schedule_data']

                st.dataframe(tranche_statement_schedule_data)
                tranche_statement_schedule_download = convert_df(tranche_statement_schedule_data)
                st.download_button(
                    "Скачать tranche_statement_schedule.csv",
                    tranche_statement_schedule_download,
                    "tranche_statement_schedule.csv",
                    "text/csv",
                    key='download-csv'
                )
                st.session_state['recognize_btn'] = True

            with st.spinner('Распознавание документов "График платежей по договору потребительского Займа.."'):
                if not isinstance(st.session_state.get('tranche_statement_data'), pd.DataFrame):
                    time.sleep(1)
                    tranche_statement_data = pd.read_csv('demo_examples/tranche_statement.csv')
                    st.session_state['tranche_statement_data'] = tranche_statement_data
                else:
                    tranche_statement_data = st.session_state['tranche_statement_data']

                st.dataframe(tranche_statement_data)
                tranche_statement_download = convert_df(tranche_statement_data)
                st.download_button(
                    "Скачать tranche_statement.csv",
                    tranche_statement_download,
                    "tranche_statement.csv",
                    "text/csv",
                    key='download-csv'
                )
                st.session_state['recognize_btn'] = True


if __name__ == '__main__':
    main()
