import pandas as pd
import streamlit as st
import datetime
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color
from reportlab.platypus import SimpleDocTemplate, Image, Table, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from textwrap import wrap

st.set_page_config(layout='wide')

dia_e_hora = datetime.datetime.now()
ordens = pd.read_csv(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\ordens.csv',encoding='latin-1')
acompanhamentos_de_assessores = pd.read_csv(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\acompanhamento_de_operacoes.csv').rename(
    columns={'Solicitada':'Data/Hora'})
controle = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos.xlsx',2,skiprows=1)
ordens['Valor'] = round(ordens['Qt. Executada']*ordens['Preço Médio'],2).astype(str).apply(lambda x: f'R$ {x}')
print(ordens.info())
ordens = ordens.iloc[:,[1,2,3,4,5,27]]
st.dataframe(ordens)
controle = controle.iloc[:-5,[1,2,4,5]]

renda_variavel = pd.merge(ordens,controle,on='Conta',how='outer')
assesores_e_controle = pd.merge(controle,acompanhamentos_de_assessores,on='Conta',how='outer')
assesores_e_controle= assesores_e_controle[assesores_e_controle['Produto'].notnull()]
renda_variavel = renda_variavel[renda_variavel['Ativo'].notnull()].rename(columns={'Ativo':'Descricao','Status':'Situacao','Direção':'Operacao'})
arquivo_final = pd.concat([assesores_e_controle,renda_variavel]).rename(columns={'Data/Hora':'Data'}).drop(columns=['Requisitante','Produto'])
arquivo_final['Data'] = dia_e_hora.strftime('%d/%m/%Y')
arquivo_final = arquivo_final.drop(columns=['Cliente_x','Conta']).rename(columns={'Cliente_y':'Cliente'})
def truncar_descricao(tabela,coluna,n_de_palvras):

    if 'Descricao' in tabela.columns:
        for indice, linha in tabela.iterrows():
            tabela.at[indice, coluna] = linha[coluna][:n_de_palvras]
    return tabela

arquivo_final_truncado = truncar_descricao(arquivo_final,'Descricao',100)
arquivo_final_truncado = truncar_descricao(arquivo_final,'Cliente',24)

df = arquivo_final_truncado[arquivo_final_truncado['UF']=='DF']
go = arquivo_final_truncado[arquivo_final_truncado['UF']=='GO']
sul = arquivo_final_truncado[arquivo_final_truncado['UF']=='SUL']


seletor_assessor_df = st.sidebar.selectbox('Selecione o Assessor DF',options=df['Assessor'].unique(),key='Assessor df')
seletor_assessor_go = st.sidebar.selectbox('Selecione o Assessor GO',options=go['Assessor'].unique(),key='Assessor go')
seletor_assessor_sul = st.sidebar.selectbox('Selecione o Assessor Sul',options=sul['Assessor'].unique(),key='Assessor sul')

assessores_sul = list(sul['Assessor'].unique())

df = df[df['Assessor']==seletor_assessor_df].reset_index(drop='index')
sul = sul[sul['Assessor']==seletor_assessor_sul].reset_index(drop='index')
go = go[go['Assessor']==seletor_assessor_go].reset_index(drop='index')
sul = sul.drop(columns='UF')
go = go.drop(columns='UF')
df = df.drop(columns='UF')


def gerando_pdf(asssssor, data_dia, tabela):
    filename = f'relatorio__{assessor}__.pdf'

    # Cria um objeto SimpleDocTemplate para gerar o PDF
    doc = SimpleDocTemplate(filename, pagesize=letter,topMargin=25)
    story = []

    # Adiciona a imagem ao início do PDF
    img_path = "LOGO_BLUEMETRIX_VERTICAL jpg.jpg"
    img = Image(img_path, width=250, height=200)
    story.append(img)

    # Adiciona o assessor e a data ao início do PDF
    styles = getSampleStyleSheet()
    assessor_text = f'<b>Assessor:</b> {asssssor}'
    data_text = f'<b>Data:</b> {data_dia}'
    story.append(Paragraph(assessor_text, styles["Normal"]))
    story.append(Paragraph(data_text, styles["Normal"]))

    # # Define o estilo da tabela
    table_style = [('GRID', (0, 0), (-1, -1), 1, 'grey'),
               ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
               ('FONTSIZE', (0, 0), (-1, -1), 4.5),
               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
               ('WORDWRAP', (0, 0), (-1, -1)),
               ('COLWIDTHS', (0, 0), (-1, -1), [1.2*inch, 1.2*inch, 2.4*inch, 1.2*inch, 0.5*inch, 1.2*inch, 1.2*inch]),
    ]

    #t.setStyle(style)
    data = [tabela.columns.values.tolist()] + tabela.values.tolist()
    t = Table(data, style=table_style) 

    # Adiciona a tabela à história do PDF
    story.append(t)

    # Verifica se a tabela cabe em uma única página
    w, h = t.wrap(doc.width, doc.height)

    # Se a tabela não couber em uma única página, adiciona uma quebra de página
    if h < doc.height:
        story.append(PageBreak())

    # Constrói o PDF com a história gerada
    doc.build(story)

    return filename


st.dataframe(df)
st.dataframe(go)
st.dataframe(sul)

if st.button('Gerar Relatorio '):
    for assessor in assessores_sul:
            tabela_assessor = arquivo_final_truncado[arquivo_final_truncado['Assessor']==assessor]
            gerar_pdf = gerando_pdf(assessor,dia_e_hora,tabela_assessor)