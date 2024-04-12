import pandas as pd
import streamlit as st
import datetime
st.set_page_config(layout='wide')

dia_e_hora = datetime.datetime.now()
ordens = pd.read_csv(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\ordens.csv',encoding='latin-1')
acompanhamentos_de_assessores = pd.read_csv(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\acompanhamento_de_operacoes.csv').rename(
    columns={'Solicitada':'Data/Hora'})
controle = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos.xlsx',2,skiprows=1)

ordens = ordens.iloc[:,:6]
controle = controle.iloc[:-5,[1,2,4,5]]

renda_variavel = pd.merge(ordens,controle,on='Conta',how='outer')
assesores_e_controle = pd.merge(controle,acompanhamentos_de_assessores,on='Conta',how='outer')
assesores_e_controle= assesores_e_controle[assesores_e_controle['Produto'].notnull()]
renda_variavel = renda_variavel[renda_variavel['Ativo'].notnull()]

arquivo_final = pd.concat([assesores_e_controle,controle])
st.dataframe(assesores_e_controle)




df = arquivo_final[arquivo_final['UF']=='DF']
go = arquivo_final[arquivo_final['UF']=='GO']
sul = arquivo_final[arquivo_final['UF']=='SUL']


seletor_assessor_df = st.sidebar.selectbox('Selecione o Assessor',options=df['Assessor'].unique(),key='Assessor df')
seletor_assessor_go = st.sidebar.selectbox('Selecione o Assessor',options=go['Assessor'].unique(),key='Assessor go')
seletor_assessor_sul = st.sidebar.selectbox('Selecione o Assessor',options=sul['Assessor'].unique(),key='Assessor sul')


df = df[df['Assessor']==seletor_assessor_df]
sul = sul[sul['Assessor']==seletor_assessor_sul]
go = go[go['Assessor']==seletor_assessor_go]

st.dataframe(df)
st.dataframe(go)
st.dataframe(sul)