import streamlit as st
from PIL import Image
import pathlib
import platform
from BeautifulSoup import BeautifulSoup_st
from MechanicalSoup import MechanicalSoup_st
from pandas_html import df_html
from PostgreSQL import SQL
from Mysql import MySQL
from sql_lite import sqlite
import os

# Funcion para guardar los archivos cargados
def save_uploadedfile(uploadedfile):
     with open(os.path.join("tmp",uploadedfile.name),"wb") as f:
         f.write(uploadedfile.getbuffer())
     return st.success("Saved File:{} to tmp".format(uploadedfile.name))


# methods to extract data from internet
st.write('''
## Web Scraping
''')

extract_choice = st.sidebar.selectbox('Web Scraping',
                    options=['BeautifulSoup',
                            'MechanicalSoup',
                            'Pandas (read_html)'])

if extract_choice == 'BeautifulSoup':
    navigation = BeautifulSoup_st()
    with st.expander('Cargar pagina web'):
        c1, c2 = st.columns([1, 2])
        c1.write('''### BeautifulSoup''')
        url = c2.text_input('URL')
    if url != '':
        navigation.load_page(f'{url}')
        with st.expander('Filtrar contenido'):
            navigation.filter_content()
        with st.expander('Guardar'):
            navigation.save()

elif extract_choice == 'MechanicalSoup':
    navigation = MechanicalSoup_st()
    with st.expander('Cargar pagina web'):
        c1, c2 = st.columns([1, 2])
        c1.write('''### MechanicalSoup''')
        url = c2.text_input('URL')
    if url != '':
        navigation.load_page(f'{url}')
        with st.expander('Filtrar contenido'):
            navigation.filter_content()
        with st.expander('Guardar'):
            navigation.save()

elif extract_choice == 'Pandas (read_html)':
    navigation = df_html()
    with st.expander('Cargar pagina web'):
        c1, c2 = st.columns([1, 2])
        c1.write('''### Pandas (read_html)''')
        url = c2.text_input('URL')
    if url != '':
        with st.expander('Tablas encontradas'):
            navigation.load_page(f'{url}')
        with st.expander('Guardar'):
            navigation.save()




# Methods to preproced data
st.write('''
## Structured Query Language (SQL)''')

work_choice = st.sidebar.selectbox('Structured Query Language (SQL)',
                                    options=['PostgreSQL',
                                    'MySQL',
                                    'SQLite'])

with st.expander('Conectar con una base de datos'):
    if work_choice == 'PostgreSQL':
        c1, c2 = st.columns([1, 1])
        img_logo = Image.open('img/PostgreSQL.png').resize((200, 200))
        c1.write('''#### PostgreSQL''')
        c1.image(img_logo)
        choice = st.radio('Conectar base de datos:', ['Externa', 'Interna'])
        if choice == 'Interna':
            database_name = st.secrets["postgres"]["dbname"]
            user_name = st.secrets["postgres"]["user"]
            password = st.secrets["postgres"]["password"]
            host = st.secrets["postgres"]["host"]
            port = st.secrets["postgres"]["port"]
            Postgre = SQL(database_name, user_name, password, host, port)
        elif choice == 'Externa':
            host = c2.text_input('Nombre del host')
            port = c2.text_input('Puerto')
            database_name = c2.text_input('Nombre de la base de datos')
            user_name = c2.text_input('Nombre de usuario')
            password = c2.text_input('Contraseña')

    elif work_choice == 'MySQL':
        c1, c2 = st.columns([1, 1])
        img_logo = Image.open('img/MySQL.png').resize((200, 200))
        c1.write('''#### MySQL''')
        c1.image(img_logo)
        choice = st.radio('Conectar base de datos:', ['Externa', 'Interna'])
        if choice == 'Interna':
            database_name = st.secrets["mysql"]["dbname"]
            user_name = st.secrets["mysql"]["user"]
            password = st.secrets["mysql"]["password"]
            host = st.secrets["mysql"]["host"]
            port = st.secrets["mysql"]["port"]
            Postgre = SQL(database_name, user_name, password, host, port)
        elif choice == 'Externa':
            host = c2.text_input('Nombre del host')
            port = c2.text_input('Puerto')
            database_name = c2.text_input('Nombre de la base de datos')
            user_name = c2.text_input('Nombre de usuario')
            password = c2.text_input('Contraseña')

    elif work_choice == 'SQLite':
        c1, c2 = st.columns([1, 3])
        img_logo = Image.open('img/SQLite.png').resize((160, 100))
        c1.image(img_logo)
        choice = st.radio('Conectar base de datos:', ['Externa', 'Interna'])
        database_path = None
        if choice == 'Interna': database_path = 'database.db'
        elif choice == 'Externa' and database_path == None:
            database_path = c2.file_uploader('Subir archivo de la base de datos')
            database_path = database_path.name
            st.write(str(database_path))

if work_choice == 'PostgreSQL':
    if database_name != '' and user_name != '' and password != '' and host != '' and port != '':
        Postgre = SQL(database_name, user_name, password, host, port)
        with st.expander('Tablas cargadas'):
            c1, c2, c3 = st.columns([2, 1, 1])
            mostrar_tablas = c1.checkbox('Mostrar tablas', key='mostrar')
            Importar_tabla = c2.checkbox('Importar tabla', key='importar')
            Eliminar_tabla = c2.checkbox('Eliminar tabla', key='eliminar')
            Primary_key = c3.checkbox('Primary Key', key='primary_key')
            Foreign_Key = c3.checkbox('Foreign Key', key='foreign_key')
            c1, c2 = st.columns(2)
            with c1.container():
                if mostrar_tablas: Postgre.todas_las_tablas()
            with c2.container():
                if Importar_tabla: Postgre.importar_tabla()
                elif Eliminar_tabla: Postgre.eliminar_tabla()
                elif Primary_key: Postgre.primary_key_st()
            if Foreign_Key: Postgre.foreign_key_st()

        with st.expander('Ejecutar un comando'):
            comand = str(st.text_area('Comando de SQL'))
            if comand != '': Postgre.mostrar_tabla(comand)

elif work_choice == 'MySQL':
    if database_name != '' and user_name != '' and password != '' and host != '' and port != '':
        mysql = MySQL(database_name, user_name, password, host, port)
        with st.expander('Tablas cargadas'):
            c1, c2, c3 = st.columns([2, 1, 1])
            mostrar_tablas = c1.checkbox('Mostrar tablas', key='mostrar')
            Importar_tabla = c2.checkbox('Importar tabla', key='importar')
            Eliminar_tabla = c2.checkbox('Eliminar tabla', key='eliminar')
            Primary_key = c3.checkbox('Primary Key', key='primary_key')
            Foreign_Key = c3.checkbox('Foreign Key', key='foreign_key')
            c1, c2 = st.columns(2)
            with c1.container():
                if mostrar_tablas: mysql.todas_las_tablas()
            with c2.container():
                if Importar_tabla: mysql.importar_tabla()
                elif Eliminar_tabla: mysql.eliminar_tabla()
                elif Primary_key: mysql.primary_key_st()
            if Foreign_Key: mysql.foreign_key_st()

        with st.expander('Ejecutar un comando'):
            comand = str(st.text_area('Comando de SQL'))
            if comand != '': mysql.mostrar_tabla(comand)

elif work_choice == 'SQLite':
# NOTA:
# sqlite no deja modificar las tablas, por eso lo que hay que hacer es
# copiar la info, crear una nueva tabla (con las modificaciones) y luego hacer los
# cambios. Esto metodo lo voy a hacer para establecer las primary key y las
# Foreign keys

    if database_path != '':
        SQLITE = sqlite(database_path)
        with st.expander('Tablas cargadas'):
            c1, c2, c3 = st.columns([2, 1, 1])
            mostrar_tablas = c1.checkbox('Mostrar tablas', key='mostrar')
            Importar_tabla = c2.checkbox('Importar tabla', key='importar')
            Eliminar_tabla = c2.checkbox('Eliminar tabla', key='eliminar')
            Primary_key = c3.checkbox('Primary Key', key='primary_key')
            Foreign_Key = c3.checkbox('Foreign Key', key='foreign_key')
            c1, c2 = st.columns(2)
            with c1.container():
                if mostrar_tablas: SQLITE.todas_las_tablas()
            with c2.container():
                if Importar_tabla: SQLITE.importar_tabla()
                elif Eliminar_tabla: SQLITE.eliminar_tabla()
                elif Primary_key: SQLITE.primary_key_st()
            if Foreign_Key: SQLITE.foreign_key_st()

        with st.expander('Ejecutar un comando'):
            comand = str(st.text_area('Comando de SQL'))
            if comand != '': SQLITE.mostrar_tabla(comand)
