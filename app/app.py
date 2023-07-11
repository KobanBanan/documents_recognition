import zipfile
from io import BytesIO
from typing import Dict

import PyPDF2
import pandas as pd
import streamlit as st

from document_classification import classify_documents
from restruct_agreement import collect_restruct_agreement_data
from statement_court_order import collect_statement_court_order

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
            result.update({file.filename: PyPDF2.PdfFileReader(BytesIO(zf.read(file)))})
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
            # with st.spinner(
            #         'Распознавание документов "Соглашения об использовании Аналога собственноручной подписи..'):
            #     if not isinstance(st.session_state.get('asp_data'), pd.DataFrame):
            #         asp_data = collect_asp_data(classified_documents['asp'])
            #         st.session_state['asp_data'] = asp_data
            #     else:
            #         asp_data = st.session_state['asp_data']
            #
            #     if not asp_data.empty:
            #         st.dataframe(asp_data)
            #         asp_download = convert_df(asp_data)
            #         st.download_button(
            #             "Скачать asp.csv",
            #             asp_download,
            #             "asp.csv",
            #             "text/csv",
            #             key='download-csv'
            #         )
            #
            #     st.session_state['recognize_btn'] = True
            #
            # with st.spinner(
            #         'Распознавание документов "Согласие на обработку персональных данных и обязательства..'):
            #     if not isinstance(st.session_state.get('agreement_data'), pd.DataFrame):
            #         agreement_data = collect_agreement_data(classified_documents['agreement'])
            #         st.session_state['agreement_data'] = agreement_data
            #     else:
            #         agreement_data = st.session_state['agreement_data']
            #
            #     if not agreement_data.empty:
            #         st.dataframe(agreement_data)
            #         agreement_download = convert_df(agreement_data)
            #         st.download_button(
            #             "Скачать agreement.csv",
            #             agreement_download,
            #             "agreement.csv",
            #             "text/csv",
            #             key='download-csv'
            #         )
            #
            #     st.session_state['recognize_btn'] = True
            #
            # with st.spinner('Распознавание документов "Заявление о предоставлении потребительского займа..'):
            #     if not isinstance(st.session_state.get('statement_data'), pd.DataFrame):
            #         statement_data = collect_statement_data(classified_documents['statement'])
            #         st.session_state['statement_data'] = statement_data
            #     else:
            #         statement_data = st.session_state['statement_data']
            #
            #     if not statement_data.empty:
            #         st.dataframe(statement_data)
            #         statement_download = convert_df(statement_data)
            #         st.download_button(
            #             "Скачать statement.csv",
            #             statement_download,
            #             "statement.csv",
            #             "text/csv",
            #             key='download-csv'
            #         )
            #
            #     st.session_state['recognize_btn'] = True
            #
            # with st.spinner('Распознавание документов "Заявление о предоставлении потребительского займа..'):
            #     if not isinstance(st.session_state.get('credit_facility_agreement_data'), pd.DataFrame):
            #         credit_facility_agreement_data = collect_credit_facility_agreement_data(
            #             classified_documents['credit_facility_agreement']
            #         )
            #         st.session_state['credit_facility_agreement_data'] = credit_facility_agreement_data
            #     else:
            #         credit_facility_agreement_data = st.session_state['credit_facility_agreement_data']
            #
            #     if not credit_facility_agreement_data.empty:
            #         st.dataframe(credit_facility_agreement_data)
            #         credit_facility_agreement_download = convert_df(credit_facility_agreement_data)
            #         st.download_button(
            #             "Скачать credit_facility_agreement.csv",
            #             credit_facility_agreement_download,
            #             "credit_facility_agreement_data.csv",
            #             "text/csv",
            #             key='download-csv'
            #         )
            #
            #     st.session_state['recognize_btn'] = True
            #
            # with st.spinner('Распознавание документов "График платежей по договору потребительского Займа.."'):
            #     if not isinstance(st.session_state.get('tranche_statement_schedule_data'), pd.DataFrame):
            #         tranche_statement_schedule_data = collect_tranche_statement_schedule_data(
            #             classified_documents['tranche_statement']
            #         )
            #         st.session_state['tranche_statement_schedule_data'] = tranche_statement_schedule_data
            #     else:
            #         tranche_statement_schedule_data = st.session_state['tranche_statement_schedule_data']
            #
            #     if not tranche_statement_schedule_data.empty:
            #         st.dataframe(tranche_statement_schedule_data)
            #         tranche_statement_schedule_download = convert_df(tranche_statement_schedule_data)
            #         st.download_button(
            #             "Скачать tranche_statement_schedule.csv",
            #             tranche_statement_schedule_download,
            #             "tranche_statement_schedule.csv",
            #             "text/csv",
            #             key='download-csv'
            #         )
            #
            #     st.session_state['recognize_btn'] = True
            #
            # with st.spinner('Распознавание документов "График платежей по договору потребительского Займа.."'):
            #     if not isinstance(st.session_state.get('tranche_statement_data'), pd.DataFrame):
            #         tranche_statement_data = collect_tranche_statement_data(classified_documents['tranche_statement'])
            #         st.session_state['tranche_statement_data'] = tranche_statement_data
            #     else:
            #         tranche_statement_data = st.session_state['tranche_statement_data']
            #
            #     if not tranche_statement_data.empty:
            #         st.dataframe(tranche_statement_data)
            #         tranche_statement_download = convert_df(tranche_statement_data)
            #         st.download_button(
            #             "Скачать tranche_statement.csv",
            #             tranche_statement_download,
            #             "tranche_statement.csv",
            #             "text/csv",
            #             key='download-csv'
            #         )
            #
            #     st.session_state['recognize_btn'] = True

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
