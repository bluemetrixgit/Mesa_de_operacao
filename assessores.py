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



dia_e_hora = datetime.datetime.now()-datetime.timedelta(days=1)

class Comercial():
    def __init__(self):
        print('hello world')


    def tratando_dados(self,ordens,acompanhamentos_de_assessores,controle,controle_co_admin):

        if ordens is None or acompanhamentos_de_assessores is None or controle is None or controle_co_admin is None:
            return None   

        ordens['Valor'] = round(ordens['Qt. Executada']*ordens['Preço Médio'],2).astype(str).apply(lambda x: f'R$ {x}')

        ordens = ordens.iloc[:,[1,2,3,4,5,27,0]].rename(columns={'Data/Hora':'Solicitada'})
        ordens['Solicitada'] = ordens['Solicitada'].astype(str).str[:-9]
      
        controle = controle.iloc[:-5,[1,2,4,5,7]]

        controle_co_admin = controle_co_admin.iloc[:-5,[1,2,4,5]]
        controle_e_co_admin = pd.concat([controle,controle_co_admin])

        renda_variavel = pd.merge(ordens,controle_e_co_admin,on='Conta',how='outer')
        assesores_e_controle = pd.merge(controle_e_co_admin,acompanhamentos_de_assessores,on='Conta',how='outer')
        assesores_e_controle= assesores_e_controle[assesores_e_controle['Produto'].notnull()]

        renda_variavel = renda_variavel[renda_variavel['Ativo'].notnull()].rename(columns={'Ativo':'Descricao','Status':'Situacao','Direção':'Operacao'})
        renda_variavel = renda_variavel.rename(columns={'Status_x':'Situacao','Status_y':'Status'})

        arquivo_final = pd.concat([assesores_e_controle,renda_variavel]).drop(columns=['Requisitante','Produto'])

        arquivo_final = arquivo_final.drop(columns='Cliente_x').rename(columns={'Cliente_y':'Cliente'})
        arquivo_final['Conta'] = arquivo_final['Conta'].astype(str).str[:-2].apply(lambda x: '00'+x)
        arquivo_final['Cliente'] = arquivo_final['Cliente'].str.slice(stop=16)
        arquivo_final['Descricao'] = arquivo_final['Descricao'].str.slice(stop=50)

   
        return arquivo_final
    
    def truncar_descricao(self,tabela,coluna,n_de_palvras):
        if 'Descricao' in tabela.columns:
            for indice, linha in tabela.iterrows():
                    tabela.at[indice, coluna] = linha[coluna][:n_de_palvras]
        return tabela


    def gerando_pdf(self,asssssor, data_dia, tabela):
        filename = f'relatorio__{asssssor}__.pdf'


        doc = SimpleDocTemplate(filename, pagesize=letter,topMargin=25)
        story = []


        img_path = "LOGO_BLUEMETRIX_VERTICAL jpg.jpg"
        img = Image(img_path, width=250, height=200)
        story.append(img)


        styles = getSampleStyleSheet()
        assessor_text = f'<b>Assessor:</b> {asssssor}'
        data_text = f'<b>Data:</b> {data_dia}'
        story.append(Paragraph(assessor_text, styles["Normal"]))
        story.append(Paragraph(data_text, styles["Normal"]))


        table_style = [('GRID', (0, 0), (-1, -1), 1, 'grey'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 4.5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('WORDWRAP', (0, 0), (-1, -1)),
                ('COLWIDTHS', (0, 0), (-1, -1), [1.2*inch, 1.2*inch, 2.4*inch, 1.2*inch, 0.5*inch, 1.2*inch, 1.2*inch]),
        ]


        data = [tabela.columns.values.tolist()] + tabela.values.tolist()
        t = Table(data, style=table_style) 


        story.append(t)


        w, h = t.wrap(doc.width, doc.height)


        if h < doc.height:
            story.append(PageBreak())


        doc.build(story)

        return filename



    def enviar_email(self,nome_assessor,nome_do_arquivo_pdf,dia_e_hora_pdf):
        lista_email_assessores = {#'Theo Ramos Moutinho':'laurotfl@gmail.com',
         'Theo Ramos Moutinho':'theo.moutinho@bluemetrix.com.br',
  'Vivian':'vivianpinheiro@bluemetrix.com.br',
    'Bruno Henrique':'bruno.borges@bluemetrix.com.br',
      'Thiago Canabrava':'thiagocanabrava99@gmail.com',
          'Matheus Vilar':'matheusmvilar@gmail.com',
            'Gustavo Amorim':'gustavo.amorim@bluemetrix.com.br',
  'Guilherme Marques':'guilherme.marques@grupovoga.com',
    'Rodrigo Milanez':'rodrigo.milanez@bluemetrix.com.br',
      'Lucas Zambrin':'lucas.zambrin@bluemetrix.com.br',
    'Yasmin Maia Muniz Xavier':'yasmin.muniz@grupovoga.com',
      'Hugo Motta':'hugo.motta@bluemetrix.com.br',
          'Felipe Rios':'felipe.rios@bluemetrix.com.br',
            'Rafael Vilela':'rafael.vilela@bluemetrix.com.br',
      'Alexandre Moraes Xavier':'alexandre.xavier@grupovoga.com',
        'Luca Bueno':'lucadiasbueno@gmail.com',
          'Norton Fritzsche':'norton@bluemetrix.com.br',
            'Fabrício Bonfim':'fabricio.bonfim@bluemetrix.com.br',
              'Pedro Vinicius Pereira De Andrade':'pedro.andrade@grupovoga.com',
        'Breno Lemes':'breno.lemes@bluemetrix.com.br',
            'Guilherme Rios Guercio':'guilherme.rios@bluemetrix.com.br',
                'Guilherme dos Santos':'guilherme.santos@bluemetrix.com.br',
                  'Eduardo Leopoldino':'',
            'Leandro Soares Lemos De Sousa':'',
                'Bruno Ribeiro':'bruno@ligadosinvestimentos.com.br',
                  'Victor Caldeira':'victor.caldeira@bluemetrix.com.br',
                'Caroline Facó Ehlers':'caroline.faco@bluemetrix.com.br',
                  'Augusto Sampaio':'augusto.correia@bluemetrix.com.br',
                    'Alexandre Teixeira Campos':'alexandre.campos@grupovoga.com',
                     'Joney Alves ':'joney.alves@bluemetrix.com.br',
                     'Acompanhamento de operações':'operacional@bluemetrix.com.br',
                     'Acompanhamento de operações.':'guilherme@bluemetrix.com.br',
                     }
        
        email_assessor = lista_email_assessores.get(nome_assessor)
        corpo_do_email = """
        Operações
        """
        msg = MIMEMultipart()
        msg['Subject'] = f'Operações Clientes - {nome_assessor} - {dia_e_hora_pdf}'
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


