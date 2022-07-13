import zipfile
from io import BytesIO
from typing import Dict

import PyPDF2
import streamlit as st

from agreement.agreement import collect_agreement_data
from asp.asp import collect_asp_data
from credit_facility_agreement.credit_facility_agreement import collect_credit_facility_agreement_data
from document_classification import classify_documents
from statement.statement import collect_statement_data
from tranche_statement import collect_tranche_statement_data, collect_tranche_statement_schedule_data

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


@st.cache
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

    uploaded_zip = st.file_uploader('XML File', type="zip")
    if uploaded_zip:
        zf = zipfile.ZipFile(uploaded_zip)
        pdf_corpus: Dict[str, PyPDF2.PdfFileReader] = {
            file.filename:
                PyPDF2.PdfFileReader(BytesIO(zf.read(file))) for file in zf.filelist if
            file.filename.endswith('.pdf')
        }

        recognize_btn = st.button("Распознать документы")
        if recognize_btn:

            with st.spinner('Классификация документов..'):
                classified_documents = classify_documents(pdf_corpus)

            with st.expander('Классифицированные документы'):
                st.write({k: [x.get('file_name') for x in v] for k, v in classified_documents.items()})

            with st.spinner(
                    'Распознавание документов "Соглашения об использовании Аналога собственноручной подписи..'):
                asp_data = collect_asp_data(classified_documents['asp'])
                st.dataframe(asp_data)
                asp_download = convert_df(asp_data)
                st.download_button(
                    "Скачать asp.csv",
                    asp_download,
                    "asp.csv",
                    "text/csv",
                    key='download-csv'
                )

            with st.spinner(
                    'Распознавание документов "Согласие на обработку персональных данных и обязательства..'):
                agreement_data = collect_agreement_data(classified_documents['agreement'])
                st.dataframe(agreement_data)
                agreement_download = convert_df(agreement_data)
                st.download_button(
                    "Скачать agreement.csv",
                    agreement_download,
                    "agreement.csv",
                    "text/csv",
                    key='download-csv'
                )

            with st.spinner('Распознавание документов "Заявление о предоставлении потребительского займа..'):
                statement_data = collect_statement_data(classified_documents['statement'])
                st.dataframe(statement_data)
                statement_download = convert_df(statement_data)
                st.download_button(
                    "Скачать statement.csv",
                    statement_download,
                    "statement.csv",
                    "text/csv",
                    key='download-csv'
                )

            with st.spinner('Распознавание документов "Заявление о предоставлении потребительского займа..'):
                credit_facility_agreement_data = collect_credit_facility_agreement_data(
                    classified_documents['credit_facility_agreement']
                )
                st.dataframe(credit_facility_agreement_data)
                credit_facility_agreement_download = convert_df(credit_facility_agreement_data)
                st.download_button(
                    "Скачать credit_facility_agreement.csv",
                    credit_facility_agreement_download,
                    "credit_facility_agreement_data.csv",
                    "text/csv",
                    key='download-csv'
                )

            with st.spinner('Распознавание документов "График платежей по договору потребительского Займа.."'):
                tranche_statement_schedule_data = collect_tranche_statement_schedule_data(
                    classified_documents['tranche_statement']
                )
                st.dataframe(tranche_statement_schedule_data)
                tranche_statement_schedule_download = convert_df(tranche_statement_schedule_data)
                st.download_button(
                    "Скачать tranche_statement_schedule.csv",
                    tranche_statement_schedule_download,
                    "tranche_statement_schedule.csv",
                    "text/csv",
                    key='download-csv'
                )

            with st.spinner('Распознавание документов "График платежей по договору потребительского Займа.."'):
                tranche_statement_data = collect_tranche_statement_data(classified_documents['tranche_statement'])
                st.dataframe(tranche_statement_data)
                tranche_statement_download = convert_df(tranche_statement_data)
                st.download_button(
                    "Скачать tranche_statement.csv",
                    tranche_statement_download,
                    "tranche_statement.csv",
                    "text/csv",
                    key='download-csv'
                )


if __name__ == '__main__':
    main()
