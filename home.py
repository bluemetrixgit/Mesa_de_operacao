
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import io
import openpyxl as op
import xlsxwriter
from xlsxwriter import Workbook
import base64
from io import BytesIO
import io
import xlsxwriter as xlsxwriter
import datetime
import time
import pytz
import divisao_de_operadores
from divisao_de_operadores import Divisao_de_contas
from divisao_guide import Guide_Divisao_contas
from basket_geral import  Basket_geral
from ativos_e_proporcoes import Ativos_e_proporcoes as ap
import streamlit_authenticator as stauth
import yaml
from streamlit_authenticator import Authenticate
from assessores import Comercial
from yaml.loader import SafeLoader

dia_e_hora = datetime.datetime.now()
t0 = time.perf_counter()

st.set_page_config(layout='wide')
background_image = "LOGO_BLUEMETRIX_VERTICAL_TOTAL_BLACK jpg.jpg"
st.markdown(
    f"""
    <iframe src="data:image/jpg;base64,{base64.b64encode(open(background_image, 'rb').read()).decode(

    )}" style="width:4000px;height:4000px;position: absolute;top:-50vh;left:-1050px;opacity: 0.2;background-size: cover;background-position: center;"></iframe>
    """,
    unsafe_allow_html=True
)

paginas = 'Home','Carteiras','Produtos','Divisão de operadores','Analitico','Risco','Basket geral','Carteiras Desenquadradas','Comercial'
selecionar = st.sidebar.radio('Selecione uma opção', paginas)


#---------------------------------- 
# Variaveis globais
@st.cache_data(ttl='2m')     
def le_excel(x,page,row):
    df = pd.read_excel(x,page,skiprows=row)
    return df
def le_csv(caminho,enc):
    df = pd.read_csv(caminho,encoding=enc)
    return df


pl_original = le_excel('PL Total.xlsx',0,0)
controle_original = le_excel('controle.xlsx',0,0)
saldo_original = le_excel('Saldo.xlsx',0,0)
posicao_original = le_excel('Posição.xlsx',0,0)
produtos_original = le_excel('Produtos.xlsx',0,0)
cura_original = le_excel('Curva_comdinheiro.xlsx',0,0)
curva_de_inflacao = le_excel('Curva_inflação.xlsx',0,0)
posicao_btg1 = le_excel('Posição.xlsx',0,0)
planilha_controle1 = le_excel('controle.xlsx',0,0)
co_admin = le_excel('Controle de Contratos - Carteiras Co-Administradas.xlsx',1,1)
controle_psicao = le_excel('Controle de Contratos.xlsx',2,1)
rentabilidade = le_excel('Rentabilidade (1).xlsx',0,0)
bancos = le_excel('Limite Bancos 06_23.xlsx',0,1)

ordens =le_csv('ordens.csv','latin-1')
acompanhamentos_de_assessores = le_csv('acompanhamento_de_operacoes.csv',None)


pl = pl_original.copy()
controle = controle_original.copy()
saldo = saldo_original.copy()
arquivo1 = posicao_original.copy()
produtos = produtos_original.copy()
curva_base = cura_original.copy()
curva_inflacao_copia = curva_de_inflacao.copy()
posicao_btg = posicao_btg1.copy()
planilha_controle = planilha_controle1.copy()
controle_co_admin = co_admin.copy()



colors_dark_rainbow = ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00',
                       '#FF7F00', '#FF0000']
colors_dark_brewers = ['#2c7bb6', '#abd9e9', '#ffffbf', '#fdae61', '#d7191c']
carteira = ap()

equities = carteira.equities()

income = carteira.income()

small_caps = carteira.small_caps()

dividendos = carteira.dividendos()

fii = carteira.fii()

lista_acoes_em_caixa = carteira.acoes_em_caixa()



with open('password.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)




if selecionar == 'Comercial':
    cl = Comercial()
    arquivo_final = cl.tratando_dados(ordens,acompanhamentos_de_assessores,controle_psicao,controle_co_admin)



    arquivo_final_truncado = cl.truncar_descricao(arquivo_final,'Descricao',60)
    arquivo_final_truncado = cl.truncar_descricao(arquivo_final,'Cliente',24)
    compilado_de_operacoes = arquivo_final_truncado.drop(columns='UF').sort_values(by='Conta')
    

    seletor_assessor_uf = st.sidebar.selectbox('Selecione a região ',options=arquivo_final_truncado['UF'].unique(),key='UF')
    tabela_estado = arquivo_final_truncado[arquivo_final_truncado['UF']==seletor_assessor_uf]
    seletor_assessor = st.sidebar.selectbox('Selecione o Assessor',options=tabela_estado['Assessor'].unique(),key='Assessor go')
    tabela_de_visualização = arquivo_final_truncado[(arquivo_final_truncado['UF']==seletor_assessor_uf)&(arquivo_final_truncado['Assessor']==seletor_assessor)].reset_index(drop='index')

    st.dataframe(tabela_de_visualização,use_container_width=True,)

    assessores_lista_nomes = list(arquivo_final_truncado['Assessor'].unique())

    lista_email_assessores = {#'Theo Ramos Moutinho':'laurotfl@gmail.com',
         'Theo Ramos Moutinho':'theo.moutinho@bluemetrix.com.br',
  'Vivian':'vivianpinheiro@bluemetrix.com.br',
    'Bruno Henrique':'bruno.borges@bluemetrix.com.br',
      'Thiago Canabrava':'thiago.canabrava@bluemetrix.com.br',
          'Matheus Vilar':'matheus.vilar@bluemetrix.com.br',
            'Gustavo Amorim':'gustavo.amorim@bluemetrix.com.br',
  'Guilherme Marques':'guilherme.marques@grupovoga.com',
    'Rodrigo Milanez':'rodrigo.milanez@bluemetrix.com.br',
      'Lucas Zambrin':'lucas.zambrin@bluemetrix.com.br',
    'Yasmin Maia Muniz Xavier':'yasmin.muniz@grupovoga.com',
      'Hugo Motta':'hugo.motta@bluemetrix.com.br',
          'Felipe Rios':'felipe.rios@bluemetrix.com.br',
            'Rafael Vilela':'rafael.vilela@bluemetrix.com.br',
      'Alexandre Moraes Xavier':'alexandre.xavier@grupovoga.com',
        'Luca Bueno':'luca.bueno@bluemetrix.com.br',
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
                'Caroline Facó Ehlers':'caroline.ehlers@grupovoga.com',
                  'Augusto Sampaio':'augusto.correia@bluemetrix.com.br',
                    'Alexandre Teixeira Campos':'alexandre.campos@grupovoga.com',
                     'Joney Alves ':'joney.alves@bluemetrix.com.br',
                     'Acompanhamento de operações':'operacional@bluemetrix.com.br'
                     }
    
    dia_e_hora_pdf = datetime.datetime.now()-datetime.timedelta(days=1)
    
    if st.button('Gerar Relatorio '):
        for assessor in assessores_lista_nomes:
                tabela_assessor = arquivo_final_truncado[arquivo_final_truncado['Assessor']==assessor]
                gerar_pdf = cl.gerando_pdf(assessor,arquivo_final_truncado['Solicitada'].iloc[0],tabela_assessor)
                email_assessor = lista_email_assessores.get(assessor)
                if email_assessor:  
                    cl.enviar_email(assessor, gerar_pdf)
                else:
                    st.warning(f'E-mail do assessor {assessor} não encontrado.')

        pdf_comp = cl.gerando_pdf('Acompanhamento de operações',arquivo_final_truncado['Solicitada'].iloc[0],compilado_de_operacoes)
        email_assessor_comp = lista_email_assessores.get('Acompanhamento de operações')
        if email_assessor_comp:  
                    cl.enviar_email('Acompanhamento de operações', pdf_comp)

             

elif authenticator.login():

    if st.session_state["authentication_status"]:


        if selecionar == 'Carteiras':
            from carteiras_indiv import Basket_enquadramento_carteiras

            if __name__=='__main__':
                dia_e_hora = datetime.datetime.now()
                inciando_programa = Basket_enquadramento_carteiras()
                try:
                    carteira_equity = inciando_programa.criando_carteiras('Carteira_equity',equities)
                    carteira_income = inciando_programa.criando_carteiras('Carteira Income',income)
                    carteira_small = inciando_programa.criando_carteiras('Carteira Small',small_caps)
                    carteira_dividendos = inciando_programa.criando_carteiras('Carteira Dividendos',dividendos)
                    carteira_fii = inciando_programa.criando_carteiras('Carteira FII', fii)
                    carteira_conservadora = inciando_programa.criando_carteiras_hibridas('Carteira Conservadora',0.15,0.85)
                    carteira_moderada = inciando_programa.criando_carteiras_hibridas('Carteira Moderada',0.30,0.70)
                    carteira_arrojada = inciando_programa.criando_carteiras_hibridas('Carteira Arrojada',0.50,0.50)

                    dados_finais = inciando_programa.juntando_arqeuivos(controle=controle_psicao,posicao=posicao_btg1)
                    trantrando_dados_controle = inciando_programa.tratamento_de_dados_controle(controle_psicao)

                    input_conta = st.sidebar.text_input('Escreva o número da conta : ')
                    
                    dados_finais = dados_finais.loc[dados_finais['Conta']==input_conta].iloc[:,[8,9,10]]

                    patrimono_liquido_da_conta = dados_finais["Valor Líquido"].sum()

                    trantrando_dados_controle = trantrando_dados_controle.loc[trantrando_dados_controle['Conta']==input_conta]

                    carteira_modelo = inciando_programa.selecionando_modelo_de_carteira(trantrando_dados_controle,
                                                                                        carteira_arrojada,carteira_conservadora,carteira_moderada,
                                                                                        carteira_income,carteira_equity,carteira_small,carteira_dividendos,carteira_fii)
                    
                    
                    pl_manual = st.sidebar.number_input('Escolher valor de PL',key='Adicionar pl manual',value= patrimono_liquido_da_conta,format="%.2f")

                    if pl_manual is None:
                        carteira_modelo['Valor R$'] = carteira_modelo['Proporção']*patrimono_liquido_da_conta
                    else:    
                        carteira_modelo['Valor R$'] = carteira_modelo['Proporção']*pl_manual
                    
                    carteira_modelo['Proporção'] = carteira_modelo['Proporção'].map(lambda x: f"{x * 100:,.2f}  %")

                    try:
                        basket_ = inciando_programa.criacao_basket(carteira_modelo=carteira_modelo,dados_finais=dados_finais,input_conta=input_conta)
                    except:
                        pass

                    st.text(f'Patrimônio Líquido da carteira :   {dados_finais["Valor Líquido"].sum():,.2f}')
                            
                    try:        
                        output4 = io.BytesIO()
                        with pd.ExcelWriter(output4, engine='xlsxwriter') as writer:basket_.to_excel(writer,sheet_name=f'Basket__{input_conta}___',index=False)
                        output4.seek(0)
                        st.download_button(type='primary',label="Basket Download",data=output4,file_name=f'basket_{input_conta}__{dia_e_hora}.xlsx',key='download_button')
                    except:
                        pass    
                    
                    col1,col2 = st.columns(2)
                    with col1:
                        if st.toggle('Enquadramento da carteira'):
                            grafico_estrategia = inciando_programa.checando_estrategia(dados_finais)
                        else:                    
                            posicao_atual_grafico = inciando_programa.criando_graficos_posicao_atual(dados_finais)

                        st.dataframe(dados_finais.sort_values(by='Produto'),use_container_width=True)
                        st.dataframe(trantrando_dados_controle.unstack(),use_container_width=True)
                        basket_compra = basket_[basket_['C/V']=='C']
                        basket_compra['Valor'] = basket_compra['Quantidade']*basket_compra['Preço']
                        basket_venda = basket_[basket_['C/V']=='V']
                        basket_venda['Valor'] = basket_venda['Quantidade']*basket_venda['Preço']
                        st.warning(f' O saldo Nescessario para Compra : {basket_compra["Valor"].sum():,.2f}')
                        st.warning(f' O saldo Gerado pela Venda : {basket_venda["Valor"].sum():,.2f}')
                        st.dataframe(basket_)

                    with col2:

                        grafico_posicao_ideal = inciando_programa.criando_graficos_posicao_ideal(carteira_modelo=carteira_modelo)
                        st.text("")
                        st.text("")
                        st.text("")
                        st.dataframe(carteira_modelo.sort_values(by='Ativo'),use_container_width=True)

                        grafico_rentabilidade = inciando_programa.grafico_rentabilidade(rentabilidade,input_conta)
                except:
                    st.write('Conta nâo encontrada')


        if selecionar == 'Produtos':

            produtos = pd.read_excel('Produtos.xlsx')
            produtos = produtos[[
            'PRODUTO', 'PRAZO/VENCIMENTO', 'TAXA','TAXA EQ. CDB']]
            
            produtos['PRODUTO'] = produtos['PRODUTO'].fillna(0)
            produtos = produtos[produtos['PRODUTO'] !=0]


            bancos_que_podem_ser_utilizados = [
            'Banco ABC',
            'Banco Agibak',
            'Banco Alfa',
            'Banco BBC S.A',
            'Banco BMG',
            'Banco Bocom',
            'Banco Bradesco',
            'Banco BS2',
            'Banco BTG Pactual',
            'Banco C6 Consignado',
            'Banco da China',
            'Banco Daycoval',
            'Banco de Brasilia',
            'Banco Digimais',
            'Banco do Brasil',
            'Banco Factor',
            'Banco Fibra',
            'Banco Fidis',
            'Banco Haitong',
            'Banco ICBC',
            'Banco Industrial',
            'Banco Inter',
            'Banco Itau',
            'Banco Master',
            'Banco Mercantil',
            'Banco NBC',
            'Banco Original',
            'Banco Ourinvest',
            'Banco Paulista',
            'Banco Pine',
            'Banco Randon',
            'Banco Rendimento',
            'Banco Rodobens',
            'Banco Safra',
            'Banco Santander',
            'Banco Semear',
            'Banco Sicoob',
            'Banco Topazio',
            'Banco Triangulo',
            'Banco Volkswagen',
            'Banco Votorantim',
            'Banco XCMG',
            'Banco Br Partners',
            'Caixa econômica',
            'Banco Caruana',
            'Banco Citibank',
            'Banco CNH Capital',
            'Banco Omni CFI',
            'Banco Paraná Banco',
            'Banco RaboBank',
            'Banco Sicred',
            'Banco Via Certa']



            radio = ['CDB','LCA','LCI','LC','Inflação','Inflação Implícita']
            lc =st.sidebar.radio('selecione o tipo de produto',radio)


            if lc =='CDB':
                pre_pos =st.radio('',['PRÉ','PÓS'])
                produtos = produtos[(produtos['PRODUTO'].str.slice(0,3) == 'CDB')&(produtos['TAXA'].str.slice(0,4) != 'IPCA')&(produtos['TAXA'].str.slice(0,3) != 'CDI')]
                if pre_pos == 'PRÉ':
                    produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'CDB - PRÉ']

                elif pre_pos == 'PÓS':
                    produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'CDB - PÓS']  
                    

            elif lc == 'LCI':
                pre_pos =st.radio('',['PRÉ','PÓS'])
                produtos = produtos[(produtos['PRODUTO'].str.slice(0,3) == 'LCI')&(produtos['TAXA'].str.slice(0,4) != 'IPCA')&(produtos['TAXA'].str.slice(0,3) != 'CDI')]
                if pre_pos == 'PRÉ':
                    produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCI - PRÉ']
                elif pre_pos == 'PÓS':
                    produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCI - PÓS']  
            
            elif lc == 'LC':
                pre_pos =st.radio('',['PRÉ','PÓS'])
                produtos = produtos[(produtos['PRODUTO'].str.slice(0,2) == 'LC')&(produtos['TAXA'].str.slice(0,4) != 'IPCA')&(produtos['TAXA'].str.slice(0,3) != 'CDI')]
                if pre_pos == 'PRÉ':
                    produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'LC - PRÉ']
                elif pre_pos == 'PÓS':
                    produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'LC - PÓS']          

            elif lc == 'LCA':
                pre_pos =st.radio('',['PRÉ','PÓS'])
                produtos = produtos[(produtos['PRODUTO'].str.slice(0,3) == 'LCA')&(produtos['TAXA'].str.slice(0,4) != 'IPCA')&(produtos['TAXA'].str.slice(0,3) != 'CDI')]
                if pre_pos == 'PRÉ':
                    produtos = produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCA - PRÉ']
                elif pre_pos == 'PÓS':
                    produtos=produtos[produtos['PRODUTO'].str.slice(0,9) == 'LCA - PÓS']


            elif lc =='Inflação':
                produtos = produtos[produtos['PRODUTO'].str.slice(17,23) =='ÍNDICE']
                if lc=='Inflação':
                    cdi_ipca = st.radio('',['CDI','IPCA'])
                    if cdi_ipca == 'CDI':
                        produtos=produtos[produtos['TAXA'].str.slice(0,3) == 'CDI']
                    else:
                        produtos=produtos[produtos['TAXA'].str.slice(0,4) == 'IPCA']

            elif lc == 'Infração Implícita':
                ''
                

            if lc in ['CDB','LCA' ,'LCI','LC']:
                produtos['PRE_POS'] = pre_pos
                produtos['PRODUTO'] = pd.Categorical(produtos['PRODUTO'], categories=produtos['PRODUTO'].unique(),ordered=True)
                produtos['PRE_POS'] = pd.Categorical(produtos['PRE_POS'],categories=['PRÉ','PÓS'],ordered=True)

            #----------------------------------
            # Retirando letras

            produtos['PRAZO/VENCIMENTO'] = produtos['PRAZO/VENCIMENTO'].str.extract('(\d+)').astype(float)
            produtos['TAXA EQ. CDB'] = produtos['TAXA EQ. CDB'].astype(str).str.extract('([\d,]+)')
            produtos['TAXA EQ. CDB'] = produtos['TAXA EQ. CDB'].str.replace(',','.').astype(float)

            if lc == 'Inflação' and cdi_ipca == 'CDI':
                produtos['TAXA']=produtos['TAXA'].str.slice(4,9)
                produtos['TAXA'] = produtos['TAXA'].str.replace(',','.')

            elif lc in 'Inflação' and cdi_ipca in 'IPCA':
                produtos['TAXA'] =produtos['TAXA'].str.slice(5,10)
                produtos['TAXA'] = produtos['TAXA'].str.replace(',','.')

            produtos['PRAZO/VENCIMENTO'] = produtos['PRAZO/VENCIMENTO'].sort_values(ascending=True)
            produtos['TAXA EQ. CDB'] = produtos['TAXA EQ. CDB'].sort_values(ascending=True)

            produtos['PRODUTO'] =produtos['PRODUTO'].str[:-13]
            produtos['PRODUTO'] =produtos['PRODUTO'].str[16:]
            if lc in 'Inflação':
                produtos['PRODUTO'] =produtos['PRODUTO'].str[7:]
            produtos = produtos[produtos['PRODUTO'].isin(bancos_que_podem_ser_utilizados)]    

            produtos['Vencimento'] = datetime.datetime.now() + pd.to_timedelta(produtos['PRAZO/VENCIMENTO'],unit='D')
            produtos['Vencimento'] = produtos['Vencimento'].dt.strftime('%Y-%m-%d')
            curva_inflacao_copia = curva_inflacao_copia.iloc[:15,:]
            curva_inflacao_copia['Vertices'] = pd.to_numeric(curva_inflacao_copia['Vertices'],errors='coerce')
            curva_inflacao_copia['ETTJ'] = pd.to_numeric(curva_inflacao_copia['Vertices'],errors='coerce')
            

            print(curva_inflacao_copia.info())
            curva_inflacao_copia['Vencimento'] = datetime.datetime.now() + pd.to_timedelta(curva_inflacao_copia['Vertices'],unit='D')
            curva_inflacao_copia['Vencimento'] = curva_inflacao_copia['Vencimento'].dt.strftime('%Y-%m-%d')                                                               
            #----------------------------------
            #Calculando a curva 
            hover_template = (
                "O prazo de vencimento é em: %{x}<br>"
                "A Taxa do produto é: %{y}%<br>"
                "O Banco emissor: %{text}<br>")
            
            fig2=go.Figure()
            fig2.add_traces(go.Scatter(x=curva_base['Data'],y=curva_base['Taxa Spot'],mode='lines',name='PREF',line=dict(color='white',width = 6),
                                
                                ))
            curva_do_ipca=go.Figure()
            curva_do_ipca.add_traces(go.Scatter(x=curva_inflacao_copia['Vencimento'],y=curva_inflacao_copia['ETTJ IPCA'],mode='lines',name='PREF',line=dict(color='#DC143C')))      


            produtos.sort_values(by='Vencimento',inplace=True)
            produtos_com_curva = go.Figure()
            for produto, dados in produtos.groupby('PRODUTO'):
                produtos_com_curva.add_trace(go.Scatter(x=dados['Vencimento'],y=dados['TAXA EQ. CDB'],mode='lines+markers',name=produto,text=produtos,
                                                        hovertemplate=hover_template))
                produtos_com_curva.update_layout(
                title=dict(text='Evolução PL dos Assessores ao longo do tempo', font=dict(size=20), x=0.1, y=0.9),showlegend=True,height=600,width = 1500,   xaxis=dict(
                showticklabels=True,))
                produtos_com_curva.update_yaxes(range=[9,12.5])      

            #----------------------------------
            #Scatter graph com curva:


            fig = go.Figure()
            if  lc in ['CDB','LCA' ,'LCI','LC'] and  pre_pos == 'PRÉ':    
                fig.add_trace(
                    go.Scatter(x=produtos['Vencimento'],y=produtos['TAXA EQ. CDB'],mode='markers',marker=dict(size = 8,color = 'grey'     ),text=produtos,
                            hovertemplate=hover_template))

            elif lc in ['CDB','LCA' ,'LCI','LC'] and pre_pos  =='PÓS':
                fig.add_trace(
                    go.Scatter( x=produtos['Vencimento'], y=produtos['TAXA EQ. CDB'], mode='markers', marker=dict( size = 8, color = 'grey'      ),text=produtos,
                            hovertemplate=hover_template))
            
            elif lc  == 'Inflação':
                fig_inflacao = go.Figure()
                fig_inflacao.add_trace(
                    go.Scatter( x=produtos['Vencimento'], y=produtos['TAXA'], mode='markers', marker=dict( size = 8, color = 'grey'),
                            text=produtos,
                            hovertemplate=hover_template))


            figura_inflacao_implicita = go.Figure()
            figura_inflacao_implicita.add_trace(
                go.Line(x=curva_inflacao_copia['Vertices'],y=curva_inflacao_copia['Inflação Implícita'],marker=dict(size = 8,color = 'red'),))
            figura_inflacao_implicita.update_yaxes(range=[3,6])
            figura_inflacao_implicita.update_xaxes(range=[0,2700])  


            fig.update_layout(
                showlegend= False,
                title = 'Produtos ofertadors',
                shapes =[dict(
                    type='line',
                    y0=100,y1=100,x0=0,x1=1,xref='paper',yref='y',line=dict(color='#FF8C00',width=2,dash='dash'))])
            
            if lc in ['CDB','LCA' ,'LCI','LC']  and pre_pos =='PRÉ':
                fig.update_yaxes(range=[8,13])

            elif lc in ['CDB','LCA' ,'LCI','LC'] and pre_pos =='PÓS' :
                fig.update_yaxes(range=[95,125])

            if lc in 'Inflação' and cdi_ipca in 'CDI':
                fig_inflacao.update_yaxes(range=[0,1.5])

            elif lc in'Inflação' and cdi_ipca in 'IPCA' :
                fig_inflacao.update_yaxes(range=[3,7])
        
        

            fig.update_xaxes(showticklabels = False)

            fig3 = go.Figure(data=produtos_com_curva.data+fig2.data)



            if lc in ['CDB','LCA' ,'LCI','LC'] and  pre_pos == 'PRÉ':
                st.plotly_chart(fig3,use_container_width=True)
                
            elif lc in ['CDB','LCA' ,'LCI','LC'] and pre_pos =='PÓS':
                st.plotly_chart(fig,use_container_width=True)

            elif lc  in 'Inflação' and cdi_ipca in 'CDI':
                st.plotly_chart(fig_inflacao,use_container_width=True)

            elif lc  in 'Inflação' and cdi_ipca in 'IPCA':
                inflação_e_produtos =go.Figure(data=fig_inflacao.data+curva_do_ipca.data)
                inflação_e_produtos.update_yaxes(range=[3,7])
                st.plotly_chart(inflação_e_produtos)

            elif lc in 'Inflação Implícita':    
                st.plotly_chart(figura_inflacao_implicita)  
            
            col1,col2 = st.columns(2)
            produtos = produtos.drop(columns=['PRAZO/VENCIMENTO','TAXA EQ. CDB'])
            with col1:
                bancos =    bancos.iloc[:,:6]
                bancos['Risco'] = round(bancos['Risco'],2)
                seletor_bancos = st.text_input('')

                if seletor_bancos.strip():
                    bancos = bancos[bancos['Emissores'].str.contains(seletor_bancos,case=False)]
                else:
                    bancos = bancos    
                st.dataframe(bancos)    
            with col2 :
                st.dataframe(produtos)




        if selecionar == 'Divisão de operadores':
            from co_admin import Carteiras_co_admin
            corretora = st.radio('',['BTG','Guide'])
            if corretora == 'BTG':
                controle_novas = le_excel('Controle de Contratos.xlsx',1,0)    
                saldo_original1 = le_excel('Saldo.xlsx',0,0)
                pl_original1 = le_excel('PL Total.xlsx',0,0)
                controle_2 = le_excel('Controle de Contratos.xlsx',2,1)

                arquivo1 = Divisao_de_contas()
                arquivo_compilado = arquivo1.limpando_dados(controle=controle_2,saldo=saldo_original1,pl=pl_original1)
                arquivo_novas_contas = arquivo1.novas_contas(controle_novas=controle_novas,saldo=saldo,pl=pl)

                filtrando_saldo_1 = arquivo1.filtrando_dados_e_separando_operadores(arquivo_compilado=arquivo_compilado,co_admin=co_admin)
                ler_arquivos = Carteiras_co_admin()            
                dados_agregados = ler_arquivos.juntando_planilhas(pl,controle_co_admin,saldo)
                dados_agregados = dados_agregados.iloc[:,[0,2,1,4,3,5,6,9,7,8]].rename(columns={'PL':'Valor'})
                
                filtrando_saldo = pd.concat([filtrando_saldo_1,dados_agregados]).reset_index(drop='index')
                contando_operadores = arquivo1.contando_oepradores(arquivo_compilado=arquivo_compilado)

                col1,col2 = st.columns(2)
                st.text(f"{filtrando_saldo['Operador'].value_counts().to_string()}")
                with col1:
                    seletor_operador = st.selectbox('Operadores',options=filtrando_saldo['Operador'].unique())
                    filtrando_saldo = filtrando_saldo.loc[filtrando_saldo['Operador']==seletor_operador] 



                cores = {'Inativo':'background-color: yellow',
                        'Ativo':'background-color: green',
                        'Pode Operar':'background-color: green',
                        'Checar conta':'background-color: red',
                        np.nan:'background-color: #B8860B'}
                    
                st.dataframe(filtrando_saldo.style.applymap(lambda x: cores[x], subset=['Status']),use_container_width=True)

                contas_faltantes = arquivo1.contas_nao_encontradas(arquivo_compilado=arquivo_compilado,controle_novas=controle_novas)
                st.subheader('Novas Contas ')
                st.dataframe(arquivo_novas_contas)
                st.text(f" Contagem Total de clientes por {contando_operadores['Operador'].value_counts().to_string()}")
                if contas_faltantes is not None:
                    st.subheader('Checar Contas')
                    st.dataframe(contas_faltantes)
                else:
                    ''


            if corretora == 'Guide':

                controle_g = le_excel('Controle de Contratos.xlsx',3,1)
                pl = le_excel('Bluemetrix.xlsx',0,0)
                saldo = le_excel('Saldo_guide.xlsx',0,0)


                iniciando = Guide_Divisao_contas()
                arquivo_final = iniciando.trabalhando_dados(controle_g=controle_g,pl=pl,saldo=saldo)
                dividindo_operadores = iniciando.dividindo_contas(arquivo_final=arquivo_final)
                contas_nao_contradas = iniciando.contas_nao_encontradas(arquivo_compilado=arquivo_final)
                contando_operadoress = iniciando.contando_oepradores(arquivo_final)
                print(arquivo_final.info())
                col1,col2 = st.columns(2)
                st.text(f"{dividindo_operadores['Operador'].value_counts().to_string()}")
                
                #'''Separação das contas a se operar por operados, requisição para retirar a funcionalidade, porém mantive o codigo caso voltem atrás na decisaão'''
                # with col1:
                #     seletor_operador = st.selectbox('Operadores',options=dividindo_operadores['Operador'].unique())
                #     dividindo_operadores = dividindo_operadores.loc[dividindo_operadores['Operador']==seletor_operador] 



                cores = {'Inativo':'background-color: yellow',
                        'Ativo':'background-color: green',
                        'Pode Operar':'background-color: green',
                        'Checar conta':'background-color: red',
                        'Encerrado':'background-color: #A0522D',
                        np.nan:'background-color: #A0522D',
                        'Pode operar':'background-color: green'}
                    
                
                st.dataframe(dividindo_operadores.style.applymap(lambda x: cores[x], subset=['Status']),use_container_width=True)
                st.subheader('Checar contas')
                st.dataframe(contas_nao_contradas)
                st.text(f" Contagem Total de clientes por {contando_operadoress['Operador'].value_counts().to_string()}")


        if selecionar == 'Analitico':



            posicao_btg = posicao_original.iloc[:,[0,4,10]].fillna(0)
            planilha_controle = controle.iloc[:,[2,12,]]
            #posicao_btg = posicao_btg.rename(columns={'CONTA':'Conta','PRODUTO':'Produto','ATIVO':'Ativo','VALOR BRUTO':'Valor Bruto','QUANTIDADE':'Quantidade'})
            posicao_btg = posicao_btg[~((posicao_btg['Produto'].str.contains('PREV'))|(posicao_btg['Produto']=='COE'))]

            planilha_controle = planilha_controle.drop(0)
            planilha_controle['Unnamed: 2'] =planilha_controle['Unnamed: 2'].map((lambda x: '00'+str(x))) 
            planilha_final = pd.merge(posicao_btg,planilha_controle,left_on='Conta',right_on='Unnamed: 2',how='outer').reset_index()


            soma_dos_ativos_por_carteira = planilha_final.groupby(['Unnamed: 12','Produto'])['Valor Bruto'].sum().reset_index()
            
        



            def criando_df_para_grafico(perfil_do_cliente):
                df = soma_dos_ativos_por_carteira[soma_dos_ativos_por_carteira['Unnamed: 12'] == perfil_do_cliente]
                return df
            
            carteira_inc = criando_df_para_grafico('INC')
            carteira_con = criando_df_para_grafico('CON')
            carteira_mod = criando_df_para_grafico('MOD')
            carteira_arr = criando_df_para_grafico('ARR')
            carteira_equity = criando_df_para_grafico('EQT')
            carteira_FII = criando_df_para_grafico('FII')
            carteira_small = criando_df_para_grafico('SMLL')
            carteira_dividendos = criando_df_para_grafico('DIV')
            carteira_MOD_PREV_MOD = criando_df_para_grafico('MOD/ PREV MOD')
            carteira_INC_PREV_MOD = criando_df_para_grafico('INC/ PREV MOD')
        
            lista_para_incluir_coluna_de_porcentagem = [
                carteira_inc,
                carteira_con,
                carteira_mod,
                carteira_arr,
                carteira_equity,
                carteira_FII,
                carteira_small,
                carteira_dividendos,
                carteira_MOD_PREV_MOD,
                carteira_INC_PREV_MOD]
            
            lista_remover_excecoes = [
                carteira_inc,
                carteira_mod,
                carteira_arr,
                carteira_equity,
                carteira_FII,
                carteira_small,
                carteira_dividendos,
                carteira_MOD_PREV_MOD,
                carteira_INC_PREV_MOD]

            carteira_inc['Porcentagem'] = (carteira_inc['Valor Bruto']/carteira_inc['Valor Bruto'].sum())*100

            for dfs in lista_para_incluir_coluna_de_porcentagem:
                dfs['Porcentagem'] = (dfs['Valor Bruto']/dfs['Valor Bruto'].sum())*100
            for dfs in lista_remover_excecoes:
                dfs.drop(dfs[dfs['Porcentagem']<1].index, inplace=True) 

            carteira_con = carteira_con.drop(carteira_con[carteira_con['Porcentagem']<0.2].index)

            padronizacao_dos_graficos = dict(hole=0.4,
                                            textinfo='label+percent',
                                            insidetextorientation='radial',
                                            textposition='inside')
            night_colors = ['rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)',
                        'rgb(36, 55, 57)', 'rgb(6, 4, 4)']
            sunflowers_colors = ['rgb(177, 127, 38)', 'rgb(205, 152, 36)', 'rgb(99, 79, 37)',
                            'rgb(129, 180, 179)', 'rgb(124, 103, 37)']
            irises_colors = ['rgb(33, 75, 99)', 'rgb(79, 129, 102)', 'rgb(151, 179, 100)',
                        'rgb(175, 49, 35)', 'rgb(36, 73, 147)']
            cafe_colors =  ['rgb(146, 123, 21)', 'rgb(177, 180, 34)', 'rgb(206, 206, 40)',
                        'rgb(175, 51, 21)', 'rgb(35, 36, 21)']
            colors_dark24 = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                        '#5254a3', '#ff6f61', '#6b6b6b', '#738595', '#e71d36',
                        '#ff9f1c', '#f4d35e', '#6a4c93', '#374649', '#8aaabb',
                        '#f9f7f5', '#f9f7f5', '#f9f7f5', '#f9f7f5']
            colors_dark_rainbow = ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00',
                            '#FF7F00', '#FF0000']
            colors_dark_brewers = ['#2c7bb6', '#abd9e9', '#ffffbf', '#fdae61', '#d7191c']
            colors_dark10 = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
            
            lista_acoes_em_caixa = carteira.acoes_em_caixa()
            caixa = [
                'BTG PACTUAL TESOURO SELIC FI RF REF DI',
                'TESOURO DIRETO - LFT']
            
            small_caps = ['BPAC11','ENEV3','HBSA3','IFCM3','JALL3','KEPL3',
            'MYPK3','PRIO3','SIMH3','TASA4','TUPY3','WIZC3']


            #dividendos = ['TAEE11','VIVT3','BBSE3','ABCB4','VBBR3','CPLE6','TRPL4',]
            dividendos = ['CDB','BTG PACTUAL TESOURO SELIC FI RF REF DI']
                
            
            def criando_graficos_rf_rv (df,title,color):
                df['Renda Variavel'] = df.loc[df['Produto'].isin(lista_acoes_em_caixa),'Valor Bruto'].sum()
                df['Renda Fixa'] = df.loc[~df['Produto'].isin(lista_acoes_em_caixa),'Valor Bruto'].sum()
                df['Total RV RF'] = df['Renda Variavel'] + df['Renda Fixa']
                labels = ['Renda Variavel', 'Renda Fixa']
                values = [df['Renda Variavel'].sum(), df['Renda Fixa'].sum()]
                colors = cafe_colors
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=color))])
                fig.update_layout(title_text=title,
                                    title_x=0.2,
                                    title_font_size = 23,
                                    uniformtext_minsize=14,
                                    paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig,use_container_width=True)

                return df
            def criando_graficos_caixa (df,title,color):
                df['Caixa'] = df.loc[df['Produto'].isin(caixa),'Valor Bruto'].sum()
                df['Ativos'] = df.loc[~df['Produto'].isin(caixa),'Valor Bruto'].sum()
                df['Total Caixa Ativos'] = df['Caixa'] + df['Ativos']
                labels = ['Caixa', 'Ativos']
                values = [df['Caixa'].sum(), df['Ativos'].sum()]
                colors = cafe_colors
                fig2 = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=color))])
                fig2.update_layout(title_text=title,
                                    title_x=0.2,
                                    title_font_size = 23,
                                    uniformtext_minsize=14,
                                    paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2,use_container_width=True)

                return df
            def criando_graficos_caixa_div (df,title,color):
                df['Caixa'] = df.loc[df['Produto'].isin(dividendos),'Valor Bruto'].sum()
                df['Ativos'] = df.loc[~df['Produto'].isin(dividendos),'Valor Bruto'].sum()
                df['Total Caixa Ativos'] = df['Caixa'] + df['Ativos']
                labels = ['Caixa', 'Ativos']
                values = [df['Caixa'].sum(), df['Ativos'].sum()]
                colors = cafe_colors
                fig2 = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=color))])
                fig2.update_layout(title_text=title,
                                    title_x=0.2,
                                    title_font_size = 23,
                                    uniformtext_minsize=14,
                                    paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2,use_container_width=True)

                return df
            


            mostrar_rv_x_rf = st.toggle('Ver Proporção Renda Fixa vs Renda Variável e caixa')
            col1,col2 = st.columns(2)
        

            if mostrar_rv_x_rf:
                st.warning("Para caixa foram considerados: BTG PACT TESOURO SELIC PREV FI RF REF DI e TESOURO DIRETO - LFT")
                with col1:
                    carteira_con_media_rv_rf = criando_graficos_rf_rv(carteira_con,'Conservadora',irises_colors)
                    carteira_arr_media_rv_rf = criando_graficos_rf_rv(carteira_arr,'Arrojada',colors_dark10)
                    carteira_inc_prevC_media_caixa = criando_graficos_caixa(carteira_INC_PREV_MOD,'Income Prev',colors_dark24)
                    carteira_dividendos_caixa = criando_graficos_caixa_div(carteira_dividendos,'Dividendos',night_colors)
                    carteira_smll_caixa = criando_graficos_caixa_div(carteira_small,'Small',colors_dark24)
                with col2:
                    carteira_mod_media_rv_rf = criando_graficos_rf_rv(carteira_mod,'Moderada',colors_dark_rainbow)
                    carteira_eqt_media_rv_rf = criando_graficos_rf_rv(carteira_equity,'Equity',cafe_colors)
                    carteira_INC_media_caixa = criando_graficos_caixa(carteira_inc,'Income',colors_dark_rainbow)
                    carteira_mod_prevC_media_caixa = criando_graficos_caixa(carteira_MOD_PREV_MOD,'Moderara Prev',colors_dark_brewers)


            def criando_graficos(carteira,padronizacao,titulo):

                figura = go.Figure(data=[go.Pie(
                    labels=carteira['Produto'],
                    values=carteira['Valor Bruto'],
                    marker_colors=sunflowers_colors,
                    scalegroup='one'

                    
                                )])
                figura.update_traces(**padronizacao)
                figura.update_layout(title_text = titulo,
                                    title_x=0.2,
                                    title_font_size = 23,
                                    uniformtext_minsize=14,
                                    paper_bgcolor='rgba(0,0,0,0)'
                                    #uniformtext_mode='hide'
                                    )

                return figura
                


            figura_carteira_inc = criando_graficos(carteira_inc,padronizacao_dos_graficos,'Carteira Income')
            figura_carteira_con = criando_graficos(carteira_con,padronizacao_dos_graficos,'Carteira Conservadora')
            figura_carteira_mod = criando_graficos(carteira_mod,padronizacao_dos_graficos,'Carteira Moderada')
            figura_carteira_arr = criando_graficos(carteira_arr,padronizacao_dos_graficos,'Carteira Arrojada')
            figura_carteira_equity = criando_graficos(carteira_equity,padronizacao_dos_graficos,'Carteira Equity')
            figura_carteira_FII = criando_graficos(carteira_FII,padronizacao_dos_graficos,'Carteira FII')
            figura_carteira_small = criando_graficos(carteira_small,padronizacao_dos_graficos,'Carteira Small Caps')
            figura_carteira_dividendos = criando_graficos(carteira_dividendos,padronizacao_dos_graficos,'Carteira Dividendos')
            figura_carteira_MOD_PREV_MOD = criando_graficos(carteira_MOD_PREV_MOD,padronizacao_dos_graficos,'Carteira Moderada - Previdencia - Moderada')
            figura_carteira_INC_PREV_MOD = criando_graficos(carteira_INC_PREV_MOD,padronizacao_dos_graficos,'Carteira Income - Previdencia - Moderada')

            
            with col1: 
                carteira_income = st.toggle('Income',key='ver_income')
                carteira_conse = st.toggle('Conservadora',key='ver_conservadora')
                carteira_moderada_tog = st.toggle('Moderada',key='ver_mdoerada')
                carteira_Arr = st.toggle('Arrojada',key='ver_arrojada')
                carteira_Eqt = st.toggle('Equity',key='ver_eqt') 
                st.markdown("<br>",unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)
            with col2:  
                carteira_fii_tg = st.toggle('FII',key='ver_fiis')
                carteira_sml = st.toggle('Small',key='ver_smlss')
                carteira_dividendos_tg = st.toggle('Dividendos',key='ver_dividendos')
                carteira_mod_prev = st.toggle('Moderada Previdencia',key='ver_mod_prev')
                carteira_inc_prev = st.toggle('Income Previdencia',key='ver_inc')
                st.markdown("<br>",unsafe_allow_html=True)
                st.markdown("<br>",unsafe_allow_html=True)

            ajustas_coluna_de_porcentagem = [
                carteira_inc  , carteira_con,carteira_mod,
                carteira_arr,carteira_equity,
                carteira_FII,carteira_small,carteira_dividendos,
                carteira_MOD_PREV_MOD,carteira_INC_PREV_MOD
                    ]
            for dfs in ajustas_coluna_de_porcentagem:
                dfs['Porcentagem'] = dfs['Porcentagem'].apply(lambda x: f'{x:.2f}%' )


            if carteira_income:
                with col1:st.plotly_chart(figura_carteira_inc,use_container_width=True)
                with col2:st.dataframe(carteira_inc)

            elif carteira_conse:
                with col1:st.plotly_chart(figura_carteira_con,use_container_width=True)
                with col2:st.dataframe(carteira_con)

            elif carteira_moderada_tog:
                with col1:st.plotly_chart(figura_carteira_mod,use_container_width=True)
                with col2:st.dataframe(carteira_mod)

            elif carteira_Arr:
                with col1:st.plotly_chart(figura_carteira_arr,use_container_width=True)
                with col2:st.dataframe(carteira_arr)

            elif carteira_Eqt:
                with col1:st.plotly_chart(figura_carteira_equity,use_container_width=True)
                with col2:st.dataframe(carteira_equity)

            elif carteira_fii_tg:
                with col1:st.plotly_chart(figura_carteira_FII,use_container_width=True)
                with col2:st.dataframe(carteira_FII)

            elif carteira_sml:
                with col1:st.plotly_chart(figura_carteira_small,use_container_width=True)
                with col2:st.dataframe(carteira_small)

            elif carteira_dividendos_tg:
                with col1:st.plotly_chart(figura_carteira_dividendos,use_container_width=True)
                with col2:st.dataframe(carteira_dividendos)

            elif carteira_inc_prev:
                with col1:st.plotly_chart(figura_carteira_INC_PREV_MOD,use_container_width=True)
                with col2:st.dataframe(carteira_INC_PREV_MOD)

            elif carteira_mod_prev:
                with col1:st.plotly_chart(figura_carteira_MOD_PREV_MOD,use_container_width=True)
                with col2:st.dataframe(carteira_MOD_PREV_MOD)

        if selecionar == 'Risco':
                        
            from risco import Risco
            st.set_option('deprecation.showPyplotGlobalUse', False)
            
            lista_ativos_b3 = ['BHIA3.SA', 'RZAT11.SA', 'GRWA11.SA', 'CRAA11.SA', 'ZAMP3.SA', 'HGAG11.SA', 'BBGO11.SA', 'AGRX11.SA', 'PLCA11.SA', 'RURA11.SA', 'SNAG11.SA', 'GCRA11.SA', 'VCRA11.SA', 'KNCA11.SA', 'NCRA11.SA', 'CPTR11.SA', 'FGAA11.SA', 'EGAF11.SA', 'VGIA11.SA', 'LSAG11.SA', 'N2ET34.SA', 'M1TA34.SA', 'FOOD11.SA', 'AERI3F.SA', 'AERI3.SA', 'ICBR3.SA', 'DOTZ3F.SA', 'DOTZ3.SA', 'GOLL3.SA', 'VIIA3F.SA', 'ARML3.SA', 'MLAS3.SA', 'CBAV3.SA', 'TTEN3.SA', 'BRBI11.SA', 'NINJ3.SA', 'ATEA3.SA', 'MODL4.SA', 'MODL11.SA', 'MODL3.SA', 'VITT3.SA', 'KRSA3.SA', 
                            '.SA', 'CXSE3.SA', 'RIOS3.SA', 'HCAR3.SA', 'GGPS3.SA', 'MATD3.SA', 'ALLD3.SA', 'BLAU3.SA', 'ATMP3.SA', 'ASAI3.SA', 'JSLG3.SA', 'CMIN3.SA', 'ELMD3.SA', 'ORVR3.SA', 'OPCT3.SA', 'WEST3.SA', 'CSED3.SA', 'BMOB3.SA', 'JALL3.SA', 'MBLY3.SA', 'ESPA3.SA', 'VAMO3.SA', 'INTB3.SA', 'CJCT11.SA', 'BMLC11.SA', 'RECR11.SA', 'URPR11.SA', 'DEVA11.SA', 'MFAI11.SA', 'NGRD3.SA', 'AVLL3.SA', 'RRRP3.SA', 'ENJU3.SA', 'CASH3.SA', 'TFCO4.SA', 'CONX3.SA', 'GMAT3.SA', 'SEQL3.SA', 'PASS3.SA', 'BOAS3.SA', 'MELK3.SA', 'HBSA3.SA', 'SIMH3F.SA', 'CURY3.SA', 'PLPL3.SA', 'PETZ3.SA', 'PGMN3.SA', 'LAVV3.SA', 'LJQQ3.SA', 'DMVF3.SA', 'SOMA3.SA', 'RIVA3.SA', 'AMBP3.SA', 'ALPK3.SA', 'MTRE3.SA', 'MDNE3.SA', 'BDLL4F.SA', 'BDLL3F.SA', 'ALOS3.SA', 'VIIA3.SA', 'CEDO4F.SA', 'CEDO3F.SA', 'CEDO4.SA', 'CEDO3.SA', 'NFLX34F.SA', 'NFLX34.SA', 'NIKE34F.SA', 'NIKE34.SA', 'MCDC34F.SA', 'MCDC34.SA', 'HOME34F.SA', 'HOME34.SA', 'FDMO34F.SA', 'FDMO34.SA', 'CMCS34F.SA', 'CMCS34.SA', 'AMZO34F.SA', 'RDNI3F.SA', 'RDNI3.SA', 'SLED4F.SA', 'SLED3F.SA', 'SLED3.SA', 'RSID3F.SA', 'RSID3.SA', 'MNDL3F.SA', 'MNDL3.SA', 'LEVE3F.SA', 'LEVE3.SA', 'CTKA4F.SA', 'CTKA3F.SA', 'CTKA4.SA', 'CTKA3.SA', 'MYPK3F.SA', 'MYPK3.SA', 'GRND3F.SA', 'GRND3.SA', 'LCAM3F.SA', 'LCAM3.SA', 'CEAB3.SA', 'VSTE3F.SA', 'VSTE3.SA', 'CGRA3F.SA', 'CGRA4F.SA', 'CGRA4.SA', 'CGRA3.SA', 'ESTR4F.SA', 'ESTR3F.SA', 'ESTR4.SA', 'ESTR3.SA', 'DIRR3F.SA', 'DIRR3.SA', 'CTNM3F.SA', 'CTNM4F.SA', 'CTNM4.SA', 'CTNM3.SA', 'ANIM3F.SA', 'EVEN3F.SA', 'EVEN3.SA', 'AMAR3F.SA', 'AMAR3.SA', 'MOVI3F.SA', 'MOVI3.SA', 'JHSF3F.SA', 'JHSF3.SA', 'HBOR3F.SA', 'HBOR3.SA', 'PDGR3F.SA', 'PDGR3.SA', 'ARZZ3F.SA', 'EZTC3F.SA', 'EZTC3.SA', 'ALPA3F.SA', 'ALPA4F.SA', 'RENT3F.SA', 'RENT3.SA', 'MRVE3F.SA', 'MRVE3.SA', 'MGLU3F.SA', 'MGLU3.SA', 'LREN3F.SA', 'LREN3.SA', 'COGN3F.SA', 'COGN3.SA', 'WHRL4.SA', 'WHRL3.SA', 'TCSA3.SA', 'SBUB34.SA', 'SMLS3.SA', 'SEER3.SA', 'SLED4.SA', 'HOOT4.SA', 'GFSA3.SA', 'GFSA3F.SA', 'YDUQ3.SA', 'CYRE3.SA', 'CVCB3.SA', 'SBFG3F.SA', 'SBFG3.SA', 'PRVA3.SA', 'WALM34F.SA', 'WALM34.SA', 'SBUB34F.SA', 'PGCO34F.SA', 'PEPB34F.SA', 'PEPB34.SA', 'COLG34F.SA', 'COLG34.SA', 'COCA34F.SA', 'COCA34.SA', 'AVON34F.SA', 'AVON34.SA', 'SMTO3F.SA', 'SMTO3.SA', 'MDIA3F.SA', 'MDIA3.SA', 'CAML3F.SA', 'CAML3.SA', 'AGRO3F.SA', 'AGRO3.SA', 'BEEF3F.SA', 'BEEF3.SA', 'BEEF11.SA', 'VIVA3.SA', 'CRFB3F.SA', 'CRFB3.SA', 'PCAR3F.SA', 'PCAR4F.SA', 'PCAR4.SA', 'PCAR3.SA', 'NTCO3F.SA', 'NTCO3.SA', 'MRFG3F.SA', 'MRFG3.SA', 'JBSS3F.SA', 'JBSS3.SA', 'PGCO34.SA', 'BRFS3.SA', 'NDIV11.SA', 'CSUD3.SA', 'INBR31.SA', 'BIDI3.SA', 'BIDI11.SA', 'BIDI4.SA', 'STOC31.SA', 'NUBR33.SA', 'IGTI11.SA', 'IGTI3.SA', 'XPBR31.SA', 'TRAD3.SA', 'BSLI4F.SA', 'BSLI3F.SA', 'BSLI4.SA', 'BSLI3.SA', 'BTTL3F.SA', 'BTTL3.SA', 'BPAR3F.SA', 'BPAR3.SA', 'WFCO34F.SA', 'WFCO34.SA', 'VISA34F.SA', 'VISA34.SA', 'MSBR34F.SA', 'MSBR34.SA', 'MSCD34F.SA', 'MSCD34.SA', 'JPMC34F.SA', 'JPMC34.SA', 'HONB34F.SA', 'HONB34.SA', 'GEOO34F.SA', 'GEOO34.SA', 'GSGI34F.SA', 'GSGI34.SA', 'CTGP34F.SA', 'CTGP34.SA', 'BOAC34F.SA', 'BOAC34.SA', 'MMMC34F.SA', 'SCAR3F.SA', 'SCAR3.SA', 'LPSB3F.SA', 'LPSB3.SA', 'BMGB11.SA', 'BMGB4.SA', 'IGBR3F.SA', 'IGBR3.SA', 'GSHP3F.SA', 'GSHP3.SA', 'PSSA3F.SA', 'PSSA3.SA', 'CARD3F.SA', 'CARD3.SA', 'BBRK3F.SA', 'BBRK3.SA', 'BRPR3F.SA', 'BRPR3.SA', 'BRSR6F.SA', 'BRSR5F.SA', 'BRSR3F.SA', 'BRSR6.SA', 'BRSR5.SA', 'BRSR3.SA', 'SANB4F.SA', 'SANB3F.SA', 'SANB11F.SA', 'SANB4.SA', 'SANB3.SA', 'SANB11.SA', 'MULT3F.SA', 'MULT3.SA', 'ITUB3F.SA', 'ITUB4.SA', 'ITUB3.SA', 'ITUB4F.SA', 'ALSO3.SA', 'BMIN3.SA', 'MERC4.SA', 'LOGG3.SA', 'ITSA4F.SA', 'ITSA4.SA', 'ITSA3F.SA', 'IRBR3.SA', 'PDTC3.SA', 'SYNE3.SA', 'BBDC4F.SA', 'BBDC4.SA', 'BBDC3.SA', 'BRML3.SA', 'APER3F.SA', 'APER3.SA', 'BBSE3.SA', 'BPAN4.SA', 'BBAS3F.SA', 'BBAS3.SA', 'BBAS12.SA', 'BBAS11.SA', 'AXPB34.SA', 'LAND3.SA', 'DEXP4.SA', 'DEXP3.SA', 'RANI3F.SA', 'FCXO34F.SA', 'FCXO34.SA', 'PMAM3F.SA', 'PMAM3.SA', 'FESA4F.SA', 'FESA3F.SA', 'FESA4.SA', 'FESA3.SA', 'EUCA3F.SA', 'EUCA4.SA', 'EUCA3.SA', 'SUZB3F.SA', 'SUZB3.SA', 'KLBN4F.SA', 'KLBN3F.SA', 'KLBN11F.SA', 'KLBN4.SA', 'KLBN3.SA', 'KLBN11.SA', 'VALE5.SA', 'UNIP6F.SA', 'UNIP6.SA', 'UNIP5F.SA', 
                            'UNIP5.SA', 'UNIP3.SA', 'NEMO6.SA', 'NEMO5.SA', 'NEMO3.SA', 'MMXM3.SA', 'MMXM11.SA', 'GOAU4.SA', 'DXCO3.SA', 'CSNA3F.SA', 'CSNA3.SA', 'BRKM6.SA', 'BRKM5F.SA', 'BRKM5.SA', 'BRKM3.SA', 'BRAP4F.SA', 'BRAP4.SA', 'BRAP3F.SA', 'BRAP3.SA', 'ARMT34.SA', 'RBIV11.SA', 'CPLE11F.SA', 'CPLE11.SA', 'GTLG11.SA', 'PPLA11.SA', 'BTLT39.SA', 'BSHY39.SA', 'BSHV39.SA', 'BIEI39.SA', 'BIYT39.SA', 'BGOV39.SA', 'ALUG11.SA', 'WRLD11.SA', 'CXAG11.SA', 'ROOF11.SA', 'JGPX11.SA', 'PURB11.SA', 'BIME11.SA', 'JSAF11.SA', 'TELD11.SA', 'MORC11.SA', 'HUSI11.SA', 'CYCR11.SA', 'EQIR11.SA', 'CACR11.SA', 'RZAG11.SA', 'PORT3.SA', 'GETT11.SA', 'GETT4.SA', 'GETT3.SA', 'BIYE39.SA', 'BSCZ39.SA', 'BUSA39.SA', 'BERU39.SA', 'BSOX39.SA', 'BFCG39.SA', 'BFXH39.SA', 'BFTA39.SA', 'BKYY39.SA', 'BQTC39.SA', 'BFDN39.SA', 'BFDA39.SA', 'BFPI39.SA', 'BQQW39.SA', 'BFPX39.SA', 'BCIR39.SA', 'BFDL39.SA', 'BFBI39.SA', 'BOEF39.SA', 'BURT39.SA', 'BICL39.SA', 'BIXG39.SA', 'C2OI34.SA', 'S2TO34.SA', 'MILA.SA', 'CSMO.SA', 'YDRO11.SA', 'SPXB11.SA', 'SMAB11.SA', 'W2ST34.SA', 'S2QS34.SA', 'P2AT34.SA', 'G2DD34.SA', 'D2AS34.SA', 'C2PT34.SA', 'BIVW39.SA', 'BIVE39.SA', 'BCWV39.SA', 'A2VL34.SA', 'A2MC34.SA', 'AFHI11.SA', 'HSRE11.SA', 'VSEC11.SA', 'GRAO3.SA', 'USTK11.SA', 'AGXY3.SA', 'CRPG6.SA', 'CRPG5.SA', 'CRPG3.SA', 'SMFT3.SA', 'SOJA3.SA', 'Z2NG34.SA', 'T2TD34.SA', 'T2DH34.SA', 'S2UI34.SA', 'S2QU34.SA', 'S2NW34.SA', 'S2HO34.SA', 'C2ZR34.SA', 'U2ST34.SA', 'S2EA34.SA', 
                            'P2EN34.SA', 'M2PW34.SA', 'K2CG34.SA', 'D2KN34.SA', 'C2ON34.SA', 'C2HD34.SA', 'B2YN34.SA', 'ENMT4.SA', 'ENMT3.SA', 'SRNA3.SA', 'VBBR3.SA', 'RAIZ4.SA', 'RECV3.SA', 'SLBG34F.SA', 
                            'SLBG34.SA', 'HALI34F.SA', 'HALI34.SA', 'COPH34.SA', 'COPH34.SA', 'CHVX34F.SA', 'CHVX34.SA', 'PRIO3F.SA', 'PRIO3.SA', 'OSXB3F.SA', 'OSXB3.SA', 'DMMO11.SA', 'DMMO3F.SA', 'DMMO3.SA', 'RPMG3F.SA', 'RPMG3.SA', 'UGPA3.SA', 'UGPA3F.SA', 'PETR4F.SA', 'PETR4.SA', 'PETR3F.SA', 'PETR3.SA', 'EXXO34.SA', 'ENAT3.SA', 'ONCO3.SA', 'VVEO3.SA', 'PARD3.SA', 'BIOM3F.SA', 'BIOM3.SA', 'BALM3F.SA', 'BALM4F.SA', 'BALM4.SA', 'BALM3.SA', 'PFIZ34F.SA', 'PFIZ34.SA', 'MRCK34F.SA', 'MRCK34.SA', 'GBIO33F.SA', 'GBIO33.SA', 'PNVL3F.SA', 'PNVL3.SA', 'AALR3F.SA', 'AALR3.SA', 'ODPV3F.SA', 'ODPV3.SA', 'RADL3F.SA', 'RADL3.SA', 'QUAL3F.SA', 'QUAL3.SA', 'OFSA3.SA', 'JNJB34.SA', 'HYPE3.SA', 'FLRY3.SA', 'BMYB34.SA', 'ABTT34.SA', 'CLSA3.SA', 'LVTC3.SA', 'G2DI33.SA', 'IFCM3.SA', 'GOGL35.SA', 'LWSA3.SA', 'TOTS3F.SA', 'TOTS3.SA', 'XRXB34F.SA', 'XRXB34.SA', 'QCOM34F.SA', 'QCOM34.SA', 'ORCL34F.SA', 'ORCL34.SA', 'MSFT34F.SA', 'MSFT34.SA', 'IBMB34F.SA', 'IBMB34.SA', 'ITLC34F.SA', 'ITLC34.SA', 'HPQB34F.SA', 'HPQB34.SA', 'EBAY34F.SA', 'CSCO34F.SA', 'CSCO34.SA', 'ATTB34F.SA', 'AAPL34F.SA', 'AAPL34.SA', 'LINX3F.SA', 'LINX3.SA', 'POSI3F.SA', 'POSI3.SA', 'EBAY34.SA', 'BRIT3.SA', 'FIQE3.SA', 'DESK3.SA', 'VERZ34F.SA', 'VERZ34.SA', 'OIBR4F.SA', 'OIBR4.SA', 'OIBR.SA', 'TIMS3F.SA', 'TIMS3.SA', 'VIVT3F.SA', 'VIVT3.SA', 'TELB4F.SA', 'TELB4.SA', 'TELB3F.SA', 'TELB3.SA', 'ATTB34.SA', 'AURE3.SA', 'MEGA3.SA', 'CEPE6F.SA', 'CEPE5F.SA', 'CEPE3F.SA', 'CEPE6.SA', 'CEPE5.SA', 'CEPE3.SA', 'CEED3F.SA', 'CEED4F.SA', 'CEED4.SA', 'CEED3.SA', 'EEEL4F.SA', 'EEEL3F.SA', 'EEEL4.SA', 'EEEL3.SA', 'CASN4F.SA', 'CASN3F.SA', 'CASN4.SA', 'CASN3.SA', 'CEGR3F.SA', 'CEGR3.SA', 'CEBR3F.SA', 'CEBR6F.SA', 'CEBR5F.SA', 'CEBR6.SA', 'CEBR5.SA', 'CEBR3.SA', 'RNEW11F.SA', 'RNEW11F.SA', 'RNEW4F.SA', 'RNEW4.SA', 'RNEW3.SA', 'COCE6F.SA', 
                            'COCE5F.SA', 'COCE3F.SA', 'COCE6.SA', 'COCE5.SA', 'COCE3.SA', 'CLSC4F.SA', 'CLSC3F.SA', 'CLSC4.SA', 'CLSC3.SA', 'ALUP4F.SA', 'ALUP3F.SA', 'ALUP11F.SA', 'ALUP4.SA', 'ALUP3.SA', 'ALUP11.SA', 'SAPR11F.SA', 'SAPR4F.SA', 'SAPR3F.SA', 'SAPR4.SA', 'SAPR3.SA', 'SAPR11.SA', 'CPRE3F.SA', 'CPRE3.SA', 'CPLE5F.SA', 'CPLE6F.SA', 'CPLE6.SA', 'CPLE5.SA', 'CPLE3F.SA', 
                            'CPLE3.SA', 'CPFE3F.SA', 'CPFE3.SA', 'CGAS3F.SA', 'CGAS5F.SA', 'CGAS5.SA', 'CGAS3.SA', 'AESB3F.SA', 'AESB3.SA', 'NEOE3.SA', 'TRPL4F.SA', 'TRPL4.SA', 'TRPL3F.SA', 'TRPL3.SA', 'EGIE3.SA', 'TAEE4.SA', 'TAEE3.SA', 'TAEE11.SA', 'SBSP3F.SA', 'SBSP3.SA', 'RNEW11.SA', 'GEPA4.SA', 'GEPA3.SA', 'CESP6.SA',
                            'CESP5.SA', 'CESP3F.SA', 'CESP3.SA', 'CMIG4.SA', 'CMIG3F.SA', 'CMIG3.SA', 'AFLT3.SA','VALE3.SA']
                                

            col1, col2 = st.columns(2)

            rc = Risco()
            with col1:
                st.subheader('VAR Metodo historico Equities')
                st.text('')
                st.text('')
                st.text('')
                data_inicial = st.date_input('Selecione a data inicial')
                data_final = st.date_input('Selecione o periodo final')
                try:
                    if st.button('Rodar VAR Equities'):   
                        var_historico = rc.var_historico(data_inicial,data_final)
                except:
                    pass
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.subheader(' Simular VAR Metodo historico ')
                st.text('')
                data_inicial_var_simulacao = st.date_input('Selecione a data inicial',key='simulacao_var')
                data_final_var_simulacao = st.date_input('Selecione o periodo final',key='simulacao_var_data_final')
                lista_de_acoes_var = st.multiselect('Coloque os ativos para simulação:',options=lista_ativos_b3,key='Simulacao_var')
                lista_de_pesos_var = []
                try:
                    for ativo in lista_de_acoes_var:
                        peso = int(float(st.text_input(f'Coloque o peso para o {ativo}')))
                        lista_de_pesos_var.append(peso)
                except:st.write('Preencha todos os campos de pesos')                

            
                if st.button('Rodar VAR'):   
                    var_historico = rc.var_historico_simulacao(data_inicial_var_simulacao,data_final_var_simulacao,lista_de_acoes_var,lista_de_pesos_var)
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.subheader('Markovitz')
                lista_de_acoes_mark = st.multiselect('Coloque os ativos para simulação:',options=lista_ativos_b3,key='Simulacao_mark')
                lista_de_pesos_mark = []
                try:
                    for ativo in lista_de_acoes_mark:
                        peso = int(float(st.text_input(f'Coloque o peso para o {ativo}')))
                        lista_de_pesos_mark.append(peso)
                except:st.write('Preencha todos os campos de pesos')
                if st.button('Markovitz nova carteira'):
                    simulacao_mark = rc.markovitz_simulando_carteira(lista_de_acoes_mark,lista_de_pesos_mark)    

            
            with col2:


                st.subheader('Simulação Monte Carlo Equities')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                dias_uteis = float(st.text_input('Coloque o número de dias úteis:', value=1))
                try:
                    if st.button('Rodar Simulação Equities'):
                        monte_carlo = rc.monte_carlo(int(dias_uteis))
                    else:
                        pass
                except:
                    pass
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.subheader('Simular Monte Carlo')
                st.text('')
                st.text('')
                st.text('')
                lista_de_acoes = st.multiselect('Coloque os ativos para simulação:',options=lista_ativos_b3)
                lista_de_pesos = []
                try:
                    for ativo in lista_de_acoes:
                        peso = int(st.text_input(f'Coloque o peso para o {ativo}'))
                        lista_de_pesos.append(peso)    
                except:st.write('Preencha todos os campos de pesos')
                    
                dias_uteis_nova_simulacao = int(float(st.text_input('Coloque o número de dias úteis:', value=125)))

                if st.button('Rodar Simulação'):
                    monte_carlo_nova_carteira = rc.nova_carteira_monte_carlo(lista_de_acoes, dias_uteis_nova_simulacao, lista_de_pesos)
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.text('')
                st.subheader('Markovitz Equities')
                st.text('')
                if st.button('Markovitz'):
                    markovitz = rc.markovitz_equities()


        if selecionar == 'Carteiras Co Admin':


            class Carteiras_co_admin():
                def __init__(self,pl,controle_co_admin,saldo):
                    self.pl = pl
                    self.controle_co = controle_co_admin
                    self.saldo = saldo

                def juntando_planilhas(self):
                    arquivo_final = pd.merge(self.pl,self.saldo, on='Conta',how='outer')  
                    controle_co_admin['Conta'] = self.controle_co['Conta'].astype(str).str[:-2].apply(lambda x: '00'+ x)
                    controle_co_admin_df = pd.DataFrame(controle_co_admin)
                    arquivo_final_completo = pd.merge(arquivo_final,controle_co_admin_df,on
                                                    ='Conta',how='right').iloc[:-5,[0,2,4,6,10,16,11,20,21,22,-1]].rename(columns={'Valor':'PL'})
                    coluna_final = arquivo_final_completo.columns[-1]

                    arquivo_final_completo = arquivo_final_completo.rename(columns={coluna_final:'PL Planilha Controle'}).iloc[:,[0,2,3,5,6,7,8,1,4,9,10]]
                    
                    return arquivo_final_completo

            if __name__=='__main__':
            
                ler_arquivos = Carteiras_co_admin(pl,controle_co_admin,saldo)            
                dados_agregados = ler_arquivos.juntando_planilhas()
                print(dados_agregados)
                st.dataframe(dados_agregados)


        if selecionar == 'Basket geral':
            if __name__=='__main__':
                dia_e_hora = datetime.datetime.now().strftime("%d %m %Y")
                inciando_programa = Basket_geral()
                
                carteira_equity = inciando_programa.criando_carteiras('Carteira_equity',equities)
                carteira_income = inciando_programa.criando_carteiras('Carteira Income',income)
                carteira_small = inciando_programa.criando_carteiras('Carteira Small',small_caps)
                carteira_dividendos = inciando_programa.criando_carteiras('Carteira Dividendos',dividendos)
                carteira_fii = inciando_programa.criando_carteiras('Carteira FII', fii)
                carteira_conservadora = inciando_programa.criando_carteiras_hibridas('Carteira Conservadora',0.15,0.85)
                carteira_moderada = inciando_programa.criando_carteiras_hibridas('Carteira Moderada',0.30,0.70)
                carteira_arrojada = inciando_programa.criando_carteiras_hibridas('Carteira Arrojada',0.50,0.50)

                dados_finais_1 = inciando_programa.juntando_arqeuivos(controle=controle_psicao,posicao=posicao_btg1)
                trantrando_dados_controle = inciando_programa.tratamento_de_dados_controle(controle_psicao)
                coe_e_prev = inciando_programa.valor_de_coe_e_prev(posicao_base=posicao_btg1)

                tipos_de_carteira = ['INC','CON','MOD','ARR','EQT']
                carteiras_escolhidas_possiveis = [carteira_income,carteira_conservadora,carteira_moderada,carteira_arrojada,carteira_equity]
                carteiras_ou_operador = st.sidebar.radio('',['Operadores','Carteiras'])
                operadores = st.sidebar.radio('',['Breno','Bruno','Augusto'])

                
                if carteiras_ou_operador == 'Carteiras':
                    carteira_escolhida = st.sidebar.radio('Selecione a carteire',['INC','CON','MOD','ARR','EQT'])

                    if carteira_escolhida == 'INC':
                        carteira_modelo = carteira_income
                    elif carteira_escolhida == 'CON':
                        carteira_modelo = carteira_conservadora
                    elif carteira_escolhida == 'MOD':
                        carteira_modelo = carteira_moderada
                    elif carteira_escolhida == 'ARR':
                        carteira_modelo = carteira_arrojada
                    elif carteira_escolhida == 'EQT':
                        carteira_modelo = carteira_equity   

                    basket_geral = inciando_programa.basket_geral(dados_finais=dados_finais_1,pl_original=pl_original,
                                                                carteira=carteira_escolhida,carteira_modelo=carteira_modelo,coe_prev=coe_e_prev,operador=operadores)
                    st.dataframe(basket_geral)
                    
                    output8 = io.BytesIO()
                    with pd.ExcelWriter(output8, engine='xlsxwriter') as writer:basket_geral.to_excel(writer,sheet_name=f'Basket__{carteira_escolhida}__{dia_e_hora}',index=False)
                    output8.seek(0)
                    st.download_button(type='primary',label="Basket Download",data=output8,file_name=f'Basket___{carteira_escolhida}__{dia_e_hora}.xlsx',key='download_button')


                elif carteiras_ou_operador == 'Operadores':
                    todas_as_carteiras = []
                    for carteira_,carteira_escolhida in zip(tipos_de_carteira,carteiras_escolhidas_possiveis):
                        gerando_arquivos = inciando_programa.basket_geral(dados_finais=dados_finais_1,pl_original=pl_original,
                                                                    carteira=carteira_,carteira_modelo=carteira_escolhida,coe_prev=coe_e_prev,operador=operadores)
                        todas_as_carteiras.append(gerando_arquivos)

                    arquivo_com_todas_as_carteiras_basket_final = pd.concat(todas_as_carteiras)
                    st.dataframe(arquivo_com_todas_as_carteiras_basket_final)

                    output9 = io.BytesIO()
                    with pd.ExcelWriter(output9, engine='xlsxwriter') as writer:arquivo_com_todas_as_carteiras_basket_final.to_excel(writer,sheet_name=f'Basket__{operadores}',index=False)
                    output9.seek(0)
                    st.download_button(type='primary',label="Basket Download",data=output9,file_name=f'Basket_____{operadores}.xlsx',key='download_button')


        if selecionar == 'Carteiras Desenquadradas':

            from contas_desenquadradas import Contas_desenquadradas

            inciando_programa = Contas_desenquadradas()
            dados = inciando_programa.lendo_e_tratando_arquivos(controle_psicao,posicao_original)
            encontrando_contas_desenquadradas = inciando_programa.criando_dfs_e_checando_enquadramento(dados,10)
            contas_desen_tabela_geral = inciando_programa.criando_dfs_e_checando_enquadramento(dados,10)

            seletor_operados = st.sidebar.selectbox("Operador :",options=encontrando_contas_desenquadradas['Operador'].unique())
            seletor_carteiras = st.sidebar.selectbox("Estratégia :",options=encontrando_contas_desenquadradas['Estratégia'].unique())

            st.subheader('Contas para intermediação')
            if st.toggle('Remover CRI, CRA, Debenture',key='Remv_cri'):
                intermediacao = inciando_programa.rem_cri_cra_intermediacao_lendo_e_tratando_arquivos(controle_psicao,posicao_original)
            else:
                intermediacao = inciando_programa.intermediacao_lendo_e_tratando_arquivos(controle_psicao,posicao_original)    

            intermediacao_estrategia = inciando_programa.criando_dfs_e_checando_enquadramento(intermediacao,10)
            st.subheader('TESTE')
            st.dataframe(intermediacao_estrategia)
            intermediacao_estrategia = intermediacao_estrategia.rename(columns={'Valor Líquido_x'   :'Valor da posição na carteira',
                                                    'Valor Líquido_y'    :  'PL Total',
                                                    'Posicao Porcentagem':'% da Posição na Carteira',
                                                    'Proporção'          :'% Ideal da Posição',
                                                    'Enquadramento'      :'Variação %'}).drop(columns='Ativo_Income').iloc[:,
                                                                                                                            [ 0,1,14,15,13,11,2,3,8,9,10,4,12]]
            
            intermediacao_estrategia['Diferença R$ da carteira e valor ideal'] = ((intermediacao_estrategia['% Ideal da Posição']/100)*intermediacao_estrategia['PL Total'])-intermediacao_estrategia['Valor da posição na carteira']
            intermediacao_estrategia = intermediacao_estrategia.iloc[:,[0,1,2,3,4,13,6,7,8,5,9,10,11,12]]

            intermediacao_estrategia=intermediacao_estrategia[intermediacao_estrategia['Estratégia']==seletor_carteiras]
            st.dataframe(intermediacao_estrategia)

            st.text('')
            st.text('')
            st.text('')

            if st.toggle('Ver Tabela sem filtros:'):
                st.dataframe(contas_desen_tabela_geral)
            if st.toggle('Remover contas "Exeção"'):
                encontrando_contas_desenquadradas=encontrando_contas_desenquadradas[encontrando_contas_desenquadradas['Exceção']!='Sim']

            st.write('Não contém COE ou Previdência na contagem')
            st.warning(f"Total de contas : {encontrando_contas_desenquadradas['Conta'].shape[0]}")     
        
            status = st.sidebar.selectbox("Status :",options=encontrando_contas_desenquadradas['Status'].unique())
            encontrando_contas_desenquadradas = encontrando_contas_desenquadradas[(encontrando_contas_desenquadradas['Operador']==seletor_operados)&(encontrando_contas_desenquadradas['Estratégia']==seletor_carteiras)&(encontrando_contas_desenquadradas['Status']==status)]




        
            encontrando_contas_desenquadradas = encontrando_contas_desenquadradas.rename(columns={'Valor Líquido_x':'Valor da posição na carteira',
                                                                                                'Valor Líquido_y':'PL Total',
                                                                                                'Posicao Porcentagem':'% da Posição na Carteira',
                                                                                                'Proporção':'% Ideal da Posição',
                                                                                                'Enquadramento':'Variação %'}).drop(columns='Ativo_Income').iloc[:,
                                                                                                    [ 0,1,14,15,13,11,2,3,8,9,10,4,12]]
            
            encontrando_contas_desenquadradas['Diferença R$ da carteira e valor ideal'] = ((encontrando_contas_desenquadradas['% Ideal da Posição']/100)*encontrando_contas_desenquadradas['PL Total'])-encontrando_contas_desenquadradas['Valor da posição na carteira']
            encontrando_contas_desenquadradas = encontrando_contas_desenquadradas.iloc[:,[0,1,2,3,4,13,6,7,8,5,9,10,11,12]]

            st.dataframe(encontrando_contas_desenquadradas,use_container_width=True)




            t1 = time.perf_counter()

            print(t1-t0)


elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')


    