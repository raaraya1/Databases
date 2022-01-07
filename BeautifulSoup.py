import urllib.request as req
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import streamlit as st
from io import BytesIO

class BeautifulSoup_st:
    def __init__(self, width=600, height=400):
        self.iframe_width = width
        self.iframe_height = height

    def load_page(self, url):
        # Visualizar la pagina
        self.url = url.replace("watch?v=", "embed/")
        page = req.urlopen(self.url)
        soup = bs(page)
        html_code = st.checkbox('Codigo HTML')
        if html_code: st.code(str(soup.prettify()))


    def filter_content(self, data_type='p'):
        page = req.urlopen(self.url)
        soup = bs(page)

        # Buscamos todos los tipos de datos en la pagina
        page_content = str(soup.body)
        data_type_options = [i[1:] for i in set(re.findall('<\w+', page_content))]
        data_type = st.selectbox('Tipo de item', options=data_type_options)

        # filtramos aplicando el tipo de dato escogido
        content_filtered_1 = [str(i) for i in soup.body.findAll(data_type)]
        second_filter = st.checkbox('Filtrar por atributo')

        # filtramos aplicando el atributo escogido
        if second_filter:
            content_str_filter = ''
            for i in content_filtered_1:
                content_str_filter += f' {i}'
            atribute_options = [i[:-1] for i in set(re.findall('\w+=', content_str_filter))]
            data_atribute = st.selectbox('Atributo', options=atribute_options)
            content_filtered_2 = [str(re.findall(f'.*{data_atribute}="([^"]*)".*', i)) for i in content_filtered_1]
            df = pd.DataFrame(content_filtered_2)
        else:
            df = pd.DataFrame(content_filtered_1)


        transform_to_text = st.checkbox('Obtener texto contenido')
        if transform_to_text:
            if second_filter:
                content = soup.body.findAll(data_type)
                result = []
                for item in content:
                    h = str(item).split('>')[0]
                    x = None
                    if data_atribute in h:
                        x = item[data_atribute]
                    result.append(x)
                df = pd.DataFrame(result)
            else:
                content = soup.body.findAll(data_type)
                function_usage = []
                for item in content:
                    item = item.getText('#')
                    item = item.replace('\n', '')
                    function_usage.append(item)
                data = [i.split('#') for i in function_usage]
                df = pd.DataFrame(data)
        self.df = df
        st.table(df)

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





        #https://docs.python.org/3/library/random.html
