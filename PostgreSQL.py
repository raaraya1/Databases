import streamlit as st
import psycopg2
import pandas as pd
import re
from sqlalchemy import create_engine


class SQL():
    def __init__(self, data_base, user_name, password):
        #, user, password
        self.conexion = f'dbname={data_base} user={user_name} password={password}'
        self.conn_string = f'postgres://{user_name}:{password}@localhost/{data_base}'
        self.db = create_engine(self.conn_string)

    def ejecutar(self, comando):
        conn = psycopg2.connect(self.conexion)
        cur = conn.cursor()
        cur.execute(comando)
        conn.commit()
        cur.close()
        conn.close()

    def df_to_sql(self, df, nombre_tabla):
        conn = self.db.connect()
        columnas = df.columns
        sql_columns = '('
        for col in columnas:
            sql_columns += str(col) + ', '
        sql_columns = sql_columns[:-2] + ')'

        # guardamos la data en la tabla
        df.to_sql(nombre_tabla, conn, if_exists='replace', index=False)
        conn.close()

    def todas_las_tablas(self, show=True):
        # Mostrar tablas
        conn = psycopg2.connect(self.conexion)
        cur = conn.cursor()
        comando = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        cur.execute(comando)
        lista = []
        for table in cur.fetchall():
            lista.append(str(table)[2:-3])
        self.df_tables = pd.DataFrame(lista)
        self.df_tables.columns=['Tablas']

        if show: st.dataframe(self.df_tables)
        conn.commit()
        cur.close()
        conn.close()

    def importar_tabla(self):
        # Importar archivos y generar tablas
        nombre_tabla = st.text_input('Nombre de la tabla')
        file_type = st.radio('Extencion del archivo', ['csv', 'xlsx'])
        importar = False
        if file_type == 'csv':
            file_csv = st.file_uploader('Subir archivo csv')
            if file_csv:
                st.write('Previsualizacion')
                df_file = pd.read_csv(file_csv, sep=';')
                st.dataframe(df_file)
                importar = st.button('Importar')
        elif file_type == 'xlsx':
            file_xlsx = st.file_uploader('Subir archivo xlsx', type="xlsx")
            if file_xlsx:
                st.write('Previsualizacion')
                df_file = pd.read_excel(file_xlsx).astype(str) # esto lo hacemos por un error con streamlit
                st.dataframe(df_file)
                importar = st.button('Importar')

        if importar and nombre_tabla != '':
            self.df_to_sql(df_file, nombre_tabla)

    def eliminar_tabla(self):
        # Eliminar tabla
        nombre_tabla = st.text_input('Nombre de la tabla')
        if nombre_tabla != '':
            Eliminar = st.button('Eliminar')
            comando = f'drop table {nombre_tabla}'
            if Eliminar: self.ejecutar(comando)

    def mostrar_tabla(self, comando, nombre_tabla=False, show=True):
        conn = psycopg2.connect(self.conexion)
        cur = conn.cursor()
        cur.execute(comando)
        rows = cur.fetchall()
        # para sacar el nombre de las columnas
        self.columns_table = [cur.description[i][0] for i in range(len(cur.description))]

        df = pd.DataFrame(rows)
        df.columns = self.columns_table
        conn.commit()
        cur.close()
        conn.close()
        if show: st.dataframe(df)
        return df

    def column_type_int(self, nombre_tabla, nombre_columna):
        nombre_tabla = str(nombre_tabla)
        nombre_columna = str(nombre_columna)

        comando_base = 'select {} from {}'.format(nombre_columna, nombre_tabla)
        df = self.mostrar_tabla(comando_base)
        columna_guardada = list(df[0][:])
        columna_guardada = [int(valor) for valor in columna_guardada]

        comando = 'alter table {} drop column {}'.format(nombre_tabla, nombre_columna)
        self.ejecutar(comando)

        comando = 'alter table {} add column {} int'.format(nombre_tabla, nombre_columna)
        self.ejecutar(comando)

        comando = 'alter table {} add column indice serial'.format(nombre_tabla)
        self.ejecutar(comando)

        for ind, valor in enumerate(columna_guardada):
            comando = 'update {} set {} = {} where indice = {}'.format(nombre_tabla, nombre_columna, valor, (ind+1))
            self.ejecutar(comando)

        comando = 'alter table {} drop column indice'.format(nombre_tabla)
        self.ejecutar(comando)


    def agregar_columna(self, nombre_tabla, nombre_columna, lista_datos, tipo_columna='varchar(50)'):
        comando = 'alter table {} add column indice serial'.format(nombre_tabla)
        self.ejecutar(comando)

        if tipo_columna == 'varchar(50)':
            comando_base = 'alter table {} add column {} {}'.format(nombre_tabla, nombre_columna, tipo_columna)
            self.ejecutar(comando_base)

            for ind, valor in enumerate(lista_datos):
                comando_base = "update {} set {} = '{}' where indice = {}".format(nombre_tabla, nombre_columna, valor, ind+1)
                self.ejecutar(comando_base)

        else:
            comando_base = 'alter table {} add column {} {}'.format(nombre_tabla, nombre_columna, 'int')
            self.ejecutar(comando_base)

            for ind, valor in enumerate(lista_datos):
                comando_base = 'update {} set {} = {} where indice = {}'.format(nombre_tabla, nombre_columna, valor, ind+1)
                self.ejecutar(comando_base)

        comando = 'alter table {} drop column indice'.format(nombre_tabla)
        self.ejecutar(comando)

    # esta parte del codigo es para establecer la primary key de una tabla (con posibilidad de generar la columna)
    def valores_duplicados(self, columna_nueva):
        num_col_nueva = len(columna_nueva)
        conjunto = set(columna_nueva)
        num_conj_nueva = len(conjunto)
        duplicados = num_col_nueva - num_conj_nueva
        return duplicados

    def dic_duplicados(self, df, columna_nueva):
        indices =  range(len(df))
        diccionario = {}
        for ind in indices:
            diccionario[columna_nueva[ind]] = indices[ind]
        indices_dic = list(diccionario.values())
        ind_duplicados = [valor for valor in indices]
        for ind in indices_dic:
            ind_duplicados.remove(ind)
        # corregir la posicion
        ind_duplicados = [i+1 for i in ind_duplicados]
        return ind_duplicados

    def generar_columna(self, df, columnas_generadoras):
        columna_nueva = []
        for i in range(len(df)):
            columna_nueva.append('')
            for j in columnas_generadoras:
                columna_nueva[i] += df[j][i] + '_'
            columna_nueva[i] = columna_nueva[i][:-1]
        return columna_nueva

    def primary_key_st(self):
        # lista_tablas
        self.todas_las_tablas(show=False)
        lista_tablas = list(self.df_tables['Tablas'])
        nombre_tabla = st.selectbox('nombre de la tabla', options=lista_tablas)

        if nombre_tabla != '':
            comando = f'select * from {str(nombre_tabla)}'
            _ = self.mostrar_tabla(comando, show=False)
            lista_columnas = list(self.columns_table)
            nombre_columna = st.selectbox('nombre de la columna', options=lista_columnas)
            num_col = lista_columnas.index(nombre_columna)

        if nombre_tabla != '' and nombre_columna != '':
            generar = st.button('Generar primary key')
            if generar:
                self.primary_key(nombre_tabla=nombre_tabla,
                                nombre_columna=nombre_columna,
                                num_columna=num_col)


    def primary_key(self, nombre_tabla, nombre_columna, num_columna, columna_adicional=False, columnas_generadoras=[]):
        # generar dataframe
        comando = 'select * from {}'.format(nombre_tabla)
        df = self.mostrar_tabla(comando, show=False)

        # generar columna para verificar
        if columna_adicional == True:
            columna_nueva = self.generar_columna(df, columnas_generadoras)
        # en caso contrario se asigna a columna_nueva la columna que se quiere verificar
        else:
            columna_nueva = list(df[nombre_columna])

        # calcular cantidad de duplicados de la nueva columna
        duplicados = self.valores_duplicados(columna_nueva)

        # caso 1 -> no existen valores duplicados y columna adicional
        if columna_adicional == True and duplicados == 0:
            self.agregar_columna(nombre_tabla, 'columna_nueva', columna_nueva)
            comando = 'alter table {} add primary key (columna_nueva)'.format(nombre_tabla)
            self.ejecutar(comando)

        # caso 2 -> no existen valores duplicados y sin columna adicional
        elif columna_adicional == False and duplicados == 0:
            comando = 'alter table {} add primary key ("{}")'.format(nombre_tabla, nombre_columna)
            self.ejecutar(comando)

        # caso 3 -> existen valores duplicados y columna adicional
        if columna_adicional == True and duplicados > 0:
            # generar la columna indice
            comando = 'alter table {} add column indice serial'.format(nombre_tabla)
            self.ejecutar(comando)

            # indice de las filas que hay que eliminar
            ind_duplicados = self.dic_duplicados(df, columna_nueva)

            # para eliminarlas ejecutamos el siguiente comando
            for ind in ind_duplicados:
                comando_base = 'delete from {} where indice = {}'.format(nombre_tabla, ind)
                self.ejecutar(comando_base)

            # recordamos eliminar la columna indice
            comando = 'alter table {} drop column indice'.format(nombre_tabla)
            self.ejecutar(comando)

            # volvemos a generar la nueva columna (pero ahora corregida)
            comando = 'select * from {}'.format(nombre_tabla)
            df = self.mostrar_tabla(comando)

            # restablecemos la columna nueva
            columna_nueva = self.generar_columna(df, columnas_generadoras)

            # verificar condicion de valores duplicados
            duplicados = self.valores_duplicados(columna_nueva)
            if duplicados == 0:
                self.agregar_columna(nombre_tabla, nombre_columna, columna_nueva)
                comando = 'alter table {} add primary key ({})'.format(nombre_tabla, nombre_columna)
                self.ejecutar(comando)

        # caso 4 -> existen valores duplicados y sin columna adicional
        elif columna_adicional == False and duplicados > 0:
            # indice de las filas que hay que eliminar
            ind_duplicados = self.dic_duplicados(df, columna_nueva)

            # añadir la columna indice
            comando = 'alter table {} add column indice serial'.format(nombre_tabla)
            self.ejecutar(comando)

            # retirar las filas que calzan con la de los valores repetidos
            for ind in ind_duplicados:
                comando_base = 'delete from {} where indice = {}'.format(nombre_tabla, ind)
                self.ejecutar(comando_base)

            # volvemos a generar la nueva columna (pero ahora corregida)
            comando = 'select * from {}'.format(nombre_tabla)
            df = self.mostrar_tabla(comando)

            # restablecemos la columna nueva
            columna_nueva = self.generar_columna(df, columnas_generadoras)

            # verificar condicion de valores duplicados
            duplicados = self.valores_duplicados(columna_nueva)
            if duplicados == 0:
                comando = 'alter table {} add primary key ({})'.format(nombre_tabla, nombre_columna)
                self.ejecutar(comando)

            ## eliminar la columna indice
            comando = 'alter table {} drop column indice'.format(nombre_tabla)
            self.ejecutar(comando)

    def foreign_key_st(self):
        self.todas_las_tablas(show=False)
        lista_tablas = list(self.df_tables['Tablas'])
        co1, co2 = st.columns(2)
        Tabla1 = co1.selectbox('Tabla1', options=lista_tablas, key='tabla1')
        Tabla2 = co2.selectbox('Tabla2', options=lista_tablas, key='tabla2')


        if Tabla1 != '' and Tabla2 != '':
            comando1 = f'select * from {str(Tabla1)}'
            df1 = self.mostrar_tabla(comando1, show=False)
            columnas1 = list(df1.columns)
            nombre_columna1 = co1.selectbox('columna', options=columnas1, key='col1')

            comando2 = f'select * from {str(Tabla2)}'
            df2 = self.mostrar_tabla(comando2, show=False)
            columnas2 = list(df2.columns)
            nombre_columna2 = co2.selectbox('columna', options=columnas2, key='col2')

            def destacar(df, nombre_col):
                ind = df == nombre_col
                return ['background-color: yellow' if ind.any() else '' for i in ind]

            df_show1 = pd.DataFrame(columnas1, columns=[Tabla1])
            co1.dataframe(df_show1.style.apply(destacar, nombre_col=nombre_columna1, axis=1))

            df_show2 = pd.DataFrame(columnas2, columns=[Tabla2])
            co2.dataframe(df_show2.style.apply(destacar, nombre_col=nombre_columna2, axis=1))

            c1, c2, c3 = st.columns([3, 2, 3])
            generar_foreign_key = c2.button('Generar Foreign Key')
            if generar_foreign_key: self.foreign_key(Tabla1, nombre_columna1, Tabla2, nombre_columna2)

            st.write('''
            **Notas**:
            - Antes de utilizar este metodo se recomienda estrablacer los primary key
            de ambas tablas.
            - Tambien se recomienda fijar la tabla 2 como aquella que contiene
            todos los valores posibles de la columna.
            ''')

    def foreign_key(self, tabla1, columna1, tabla2, columna2):
        comando = '''alter table {}
                     add constraint FK{}
                     foreign key({})
                     references {} ({})'''.format(tabla1, columna1 + '_' + columna2 ,columna1, tabla2, columna2)

        self.ejecutar(comando)
