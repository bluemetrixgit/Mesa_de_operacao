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
import smtplib
import email.message
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import base64



dia_e_hora = datetime.datetime.now()

class Comercial():
    def __init__(self):
        print('hello world')


    def tratando_dados(self,ordens,acompanhamentos_de_assessores,controle):



       # Certifique-se de que ordens, acompanhamentos_de_assessores e controle não sejam None
        if ordens is None or acompanhamentos_de_assessores is None or controle is None:
            return None   

        acompanhamentos_de_assessores = acompanhamentos_de_assessores.rename(columns={'Solicitada':'Data/Hora'})
        ordens['Valor'] = round(ordens['Qt. Executada']*ordens['Preço Médio'],2).astype(str).apply(lambda x: f'R$ {x}')
        print(ordens.info())
        ordens = ordens.iloc[:,[1,2,3,4,5,27]]

        controle = controle.iloc[:-5,[1,2,4,5]]

        renda_variavel = pd.merge(ordens,controle,on='Conta',how='outer')
        assesores_e_controle = pd.merge(controle,acompanhamentos_de_assessores,on='Conta',how='outer')
        assesores_e_controle= assesores_e_controle[assesores_e_controle['Produto'].notnull()]
        renda_variavel = renda_variavel[renda_variavel['Ativo'].notnull()].rename(columns={'Ativo':'Descricao','Status':'Situacao','Direção':'Operacao'})
        arquivo_final = pd.concat([assesores_e_controle,renda_variavel]).rename(columns={'Data/Hora':'Data'}).drop(columns=['Requisitante','Produto'])
        arquivo_final['Data'] = dia_e_hora.strftime('%d/%m/%Y')
        arquivo_final = arquivo_final.drop(columns=['Cliente_x','Conta']).rename(columns={'Cliente_y':'Cliente'})
        return arquivo_final
    
    def truncar_descricao(self,tabela,coluna,n_de_palvras):
        if 'Descricao' in tabela.columns:
            for indice, linha in tabela.iterrows():
                    tabela.at[indice, coluna] = linha[coluna][:n_de_palvras]
        return tabela


    def gerando_pdf(self,asssssor, data_dia, tabela):
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



    def enviar_email(self,nome_assessor,nome_do_arquivo_pdf):
        email_assessor = lista_email_assessores.get(nome_assessor)
        corpo_do_email = """
        Operações
        """
        msg = MIMEMultipart()
        msg['Subject'] = f'Operações Clientes - {nome_assessor} - {dia_e_hora}'
        msg['From'] = 'lauro.bluemetrix@gmail.com'
        msg['To'] = email_assessor
        password = 'dlthvrayjsecacbt'
        msg.add_header('Content-Type', 'text/html')

        msg.attach(MIMEText(corpo_do_email, 'plain'))

        with open(nome_do_arquivo_pdf, 'rb') as f:
            arquivo_pdf = f.read()
            arquivo_anexado = MIMEApplication(arquivo_pdf, _subtype="pdf")
            arquivo_anexado.add_header('content-disposition', 'attachment', filename=nome_do_arquivo_pdf)
            msg.attach(arquivo_anexado)

        s=smtplib.SMTP('smtp.gmail.com: 587')
        s.starttls()

        s.login(msg['From'],password)
        s.sendmail(msg['From'],msg['To'],msg.as_string().encode('utf-8'))
        print('email enviado')


