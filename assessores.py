import pandas as pd
import streamlit as st
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color
from reportlab.platypus import SimpleDocTemplate, Image, Table, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


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
renda_variavel = renda_variavel[renda_variavel['Ativo'].notnull()].rename(columns={'Ativo':'Descricao','Status':'Situacao','Direção':'Operacao'})
arquivo_final = pd.concat([assesores_e_controle,renda_variavel]).rename(columns={'Data/Hora':'Data'}).drop(columns=['Requisitante','Produto'])
arquivo_final['Data'] = dia_e_hora.strftime('%d/%m/%Y')


df = arquivo_final[arquivo_final['UF']=='DF']
go = arquivo_final[arquivo_final['UF']=='GO']
sul = arquivo_final[arquivo_final['UF']=='SUL']


seletor_assessor_df = st.sidebar.selectbox('Selecione o Assessor DF',options=df['Assessor'].unique(),key='Assessor df')
seletor_assessor_go = st.sidebar.selectbox('Selecione o Assessor GO',options=go['Assessor'].unique(),key='Assessor go')
seletor_assessor_sul = st.sidebar.selectbox('Selecione o Assessor Sul',options=sul['Assessor'].unique(),key='Assessor sul')


df = df[df['Assessor']==seletor_assessor_df]
sul = sul[sul['Assessor']==seletor_assessor_sul]
go = go[go['Assessor']==seletor_assessor_go]


# def gerando_pdf(asssssor,data_dia,tabela):
        
#         c = canvas.Canvas(filename='relatorio.pdf',pagesize=letter)

#         img1 = ImageReader("LOGO_BLUEMETRIX_VERTICAL jpg.jpg")
#         c.drawImage(img1, 150, 600, width=250, height=200,mask='auto')

#         # Configurações de fonte
#         c.setFont('Times-Roman', 15)  # Fonte em negrito, tamanho 16
#         c.setFillColor('black')
#         c.drawString(230, 450, "Assessor")

#         c.setFont('Helvetica-Bold', 20)  # Fonte em negrito, tamanho 16
#         c.setFillColor('black')
#         c.drawString(190, 600, f'{asssssor}')

#         c.setFont('Times-Roman', 5)  # Fonte em negrito, tamanho 16
#         c.setFillColor('black')
#         c.drawString(190, 550, f'{data_dia}')

#         data = [tabela.columns.values.tolist()] + tabela.values.tolist()
#         t = Table(data)
#         t.wrapOn(c, 50, 0)
#         t.drawOn(c, 30, 150)
    

#         c.save()
        

#         return c
def gerando_pdf(asssssor, data_dia, tabela):
    filename = 'relatorio.pdf'

    # Cria um objeto SimpleDocTemplate para gerar o PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
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

    # Adiciona a tabela ao PDF
    data = [tabela.columns.values.tolist()] + tabela.values.tolist()
    t = Table(data)

    # Define o estilo da tabela
    style = [('GRID', (0, 0), (-1, -1), 1, 'BLACK')]
    t.setStyle(style)

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
        gerar_pdf = gerando_pdf(sul['Assessor'].iloc[-1],dia_e_hora,sul)