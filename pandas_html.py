import pandas as pd
import streamlit as st
import ssl
from io import BytesIO

#ssl._create_default_https_context = ssl._create_unverified_context

class df_html():
    def load_page(self, url):
        scraped = pd.read_html(url)
        dic_tables = {f'Tabla {idx+1}':table for idx, table in enumerate(scraped)}
        tablas = [i for i in dic_tables]
        table_selected = st.selectbox('Seleccionar tabla', options=tablas)
        if table_selected != '':
            self.df = pd.DataFrame(dic_tables[table_selected])
            st.dataframe(dic_tables[table_selected])

    def save(self):
        c1, c2, c3 = st.columns([7, 1, 1])

        # Descargar csv
        c1.write('''
        **Formato de descarga**''')
        csv = self.df.to_csv(header=False, index=False).encode('utf-8')
        c2.download_button(
             label="csv",
             data=csv,
             file_name='DB.csv')

        # Descargar excel
        output = BytesIO()
        excel_file = pd.ExcelWriter(output, engine='xlsxwriter')
        content_file = self.df.to_excel(excel_file, header=False, index=False)
        excel_file.save()
        data = output.getvalue()
        c3.download_button(
             label="excel",
             data=data,
             file_name='DB.xlsx')
