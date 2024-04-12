

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


colors_dark_rainbow = ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00',
                       '#FF7F00', '#FF0000']
colors_dark_brewers = ['#2c7bb6', '#abd9e9', '#ffffbf', '#fdae61', '#d7191c']


from ativos_e_proporcoes import Ativos_e_proporcoes as ap
carteira = ap()

equities = carteira.equities()

income = carteira.income()

small_caps = carteira.small_caps()

dividendos = carteira.dividendos()

fii = carteira.fii()

lista_acoes_em_caixa = carteira.acoes_em_caixa()

class Basket_geral():
    def __init__(self):
        print("O programa iniciou")



    def criando_carteiras(self,carteira,proporcao_e_ativos):
        
        self.carteira = pd.DataFrame(list(proporcao_e_ativos.items()),columns=['Ativo','Proporção'])
        self.carteira['Proporção'] = self.carteira['Proporção']/100

        return self.carteira
    
    def criando_carteiras_hibridas(self,carteira,proporcao_variavel,proporcao_fixa):
        base_de_distribuicao = {ativo:proporcao_fixa*income.get(ativo,0)+proporcao_variavel*equities.get(ativo,0) for ativo in set(income)|set(equities)}
        self.carteira = pd.DataFrame(list(base_de_distribuicao.items()),columns=['Ativo','Proporção'])
        self.carteira['Proporção'] = self.carteira['Proporção']/100
        return self.carteira
    
    def valor_de_coe_e_prev(self,posicao_base):
        planilha_posicao =posicao_base.iloc[:-2,[0,4,13,14]]
        planilha_posicao = planilha_posicao.loc[(planilha_posicao['Produto'].str.contains('PREV'))|(planilha_posicao['Produto']=='COE')]
        posicao = planilha_posicao.groupby('Conta')['Valor Líquido'].sum().reset_index()
        return posicao
         
         
    def trantamento_de_dados_posicao(self,posicao):
        planilha_posicao = pd.read_excel(posicao).iloc[:-2,[0,4,13,14]]
        planilha_posicao = planilha_posicao.loc[~(planilha_posicao['Produto'].str.contains('PREV'))|(planilha_posicao['Produto']=='COE')]
        posicao = planilha_posicao.groupby(['Conta','Produto','Produto'])['Valor Líquido'].sum().reset_index()
        return posicao
    
    def tratamento_de_dados_controle(self,planilha_controle):
        planilha_controle =planilha_controle.iloc[:-5,[1,2,6,7,12,16,17,18]]
        planilha_controle['Conta'] = planilha_controle['Conta'].astype(str).apply(lambda x: '00'+ x).str[:-2]
        return planilha_controle
    
    def juntando_arqeuivos(self,controle,posicao):
        planilha_controle = controle.iloc[:-5,[1,2,6,7,12,16,17,18]]
        planilha_controle['Conta'] = planilha_controle['Conta'].astype(str).apply(lambda x: '00'+ x).str[:-2]
        planilha_posicao = posicao.iloc[:-2,[0,4,13,14]]
        planilha_posicao['Estratégia'] = planilha_posicao['Estratégia'].fillna('Outras')
        posicao = planilha_posicao.groupby(['Conta','Produto','Estratégia'])['Valor Líquido'].sum().reset_index()
        arquivo_final = pd.merge(planilha_controle,posicao,on='Conta',how='outer')
        return arquivo_final
    
    def selecionando_modelo_de_carteira(self,arquivo_final, carteira_arrojada, carteira_conservadora, 
                                        carteira_moderada, carteira_income, carteira_equity,
                                          carteira_small, carteira_dividendos,carteira_fii):
        carteira_coluna = arquivo_final['Carteira'].iloc[0]

        carteiras = {
            'CON':carteira_conservadora,
            'ARR':carteira_arrojada,
            'MOD':carteira_moderada,
            'INC':carteira_income,
            'EQT':carteira_equity,
            'SMLL':carteira_small,
            'DIV':carteira_dividendos,
            'FII':carteira_fii
        }
        carteira_utilizada = carteiras.get(carteira_coluna,None)
        if carteira_utilizada is None:
            print('A carteira nao foi reconhecida')                      
        return carteira_utilizada
    
    
    def basket_geral(self,dados_finais,pl_original,carteira,carteira_modelo,coe_prev,operador):

        pl_original= pl_original.merge(coe_prev,on='Conta',how='outer')
        pl_original['Valor Líquido'] = pl_original['Valor Líquido'].fillna(0)
        pl_original['PL Real'] = pl_original['Valor']-pl_original['Valor Líquido']
        pl_original = pl_original.iloc[:,[0,1,4]].rename(columns={'PL Real':'Valor'})

        arquivo_com_pl = pd.merge(dados_finais,pl_original,on='Conta',how='outer')

        basket_geral_con = arquivo_com_pl[(arquivo_com_pl['Carteira']==carteira)&(arquivo_com_pl['Estratégia']=='Renda Variável')&(arquivo_com_pl['Operador']==operador)]
        basket_geral_con = basket_geral_con.merge(carteira_modelo,left_on='Produto',right_on='Ativo',how='outer')
        basket_geral_con['Porcentagem da carteira'] = basket_geral_con['Valor Líquido']/basket_geral_con['Valor']
        basket_geral_con['Valor R$ Ideal'] = round(basket_geral_con['Proporção']*basket_geral_con['Valor'],2)
        basket_geral_con['Valor R$ da carteira'] = basket_geral_con['Porcentagem da carteira']*basket_geral_con['Valor']
        basket_geral_con['Diferença VI X VC'] = basket_geral_con['Valor R$ Ideal']-basket_geral_con['Valor R$ da carteira']
        basket_geral_con = basket_geral_con[basket_geral_con['Status']=='Ativo']

        basket_geral_con = basket_geral_con.iloc[:,[0,1,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,2]]
        basket_geral_con['BOVA11'] = (0.015*basket_geral_con['Valor']).drop_duplicates()
        ativo_novo = basket_geral_con.iloc[:,[0,1,3,4,5,6,7,8,9,10,11,12,13,15,16,17,18]].rename(columns={'BOVA11':'Valor R$ Ideal'})
        ativo_novo['Valor R$ Ideal'] = ativo_novo['Valor R$ Ideal'].fillna(0.00)
        ativo_novo = ativo_novo[ativo_novo['Valor R$ Ideal']!=0.00]
        ativo_novo['Produto'] = 'BOVA11'
        ativo_novo['Proporção'] = 'BOVA11'
        ativo_novo[['Porcentagem da carteira','Valor R$ da carteira']] = ''
        ativo_novo['Diferença VI X VC'] = ativo_novo['Valor R$ Ideal']


        basket_geral_con = pd.concat([basket_geral_con,ativo_novo]).drop(columns='BOVA11')


        precos_de_mercado = []
        for ativo in lista_acoes_em_caixa:
                    ticker = yf.Ticker(ativo +'.SA')
                    preco_atual = ticker.history(period='2m')['Close'].iloc[-1]
                
                    precos_de_mercado.append([ativo,preco_atual])

        cotacoes_momento = pd.DataFrame(precos_de_mercado,columns =['Ativo','Cotação atual'])   
        basket = basket_geral_con.merge(cotacoes_momento,left_on='Produto',right_on='Ativo',how='outer').fillna(0)
        basket['Quantidade'] = round(basket['Diferença VI X VC']/basket['Cotação atual'],0).abs()
        basket['C/V'] = np.where(basket['Diferença VI X VC']>0,'C','V')
        basket['Validade']='DIA'
        basket = basket.rename(columns={'Cotação atual':'Preço'}).iloc[:-6,[7,20,19,18,1,21,4,5,6,16,-6]].dropna().rename(columns={'Produto':'Ativo'})
        return basket
    
    def basket_geral_por_operador(self,dados_finais,pl_original,carteira,carteira_modelo,coe_prev,operador):

        pl_original= pl_original.merge(coe_prev,on='Conta',how='outer')
        pl_original['Valor Líquido'] = pl_original['Valor Líquido'].fillna(0)
        pl_original['PL Real'] = pl_original['Valor']-pl_original['Valor Líquido']
        pl_original = pl_original.iloc[:,[0,1,4]].rename(columns={'PL Real':'Valor'})

        arquivo_com_pl = pd.merge(dados_finais,pl_original,on='Conta',how='outer')

        basket_geral_con = arquivo_com_pl[(arquivo_com_pl['Carteira']==carteira)&(arquivo_com_pl['Estratégia']=='Renda Variável')&(arquivo_com_pl['Operador']==operador)]
        basket_geral_con = basket_geral_con.merge(carteira_modelo,left_on='Produto',right_on='Ativo',how='outer')
        basket_geral_con['Porcentagem da carteira'] = basket_geral_con['Valor Líquido']/basket_geral_con['Valor']
        basket_geral_con['Valor R$ Ideal'] = round(basket_geral_con['Proporção']*basket_geral_con['Valor'],2)
        basket_geral_con['Valor R$ da carteira'] = basket_geral_con['Porcentagem da carteira']*basket_geral_con['Valor']
        basket_geral_con['Diferença VI X VC'] = basket_geral_con['Valor R$ Ideal']-basket_geral_con['Valor R$ da carteira']
        basket_geral_con = basket_geral_con[basket_geral_con['Status']=='Ativo']

        basket_geral_con = basket_geral_con.iloc[:,[0,1,3,4,5,6,7,8,9,10,12,13,14,15,16,17,18,2]]
        basket_geral_con['BOVA11'] = (0.015*basket_geral_con['Valor']).drop_duplicates()
        ativo_novo = basket_geral_con.iloc[:,[0,1,3,4,5,6,7,8,9,10,11,12,13,15,16,17,18]].rename(columns={'BOVA11':'Valor R$ Ideal'})
        ativo_novo['Valor R$ Ideal'] = ativo_novo['Valor R$ Ideal'].fillna(0.00)
        ativo_novo = ativo_novo[ativo_novo['Valor R$ Ideal']!=0.00]
        ativo_novo['Produto'] = 'BOVA11'
        ativo_novo['Proporção'] = 'BOVA11'
        ativo_novo[['Porcentagem da carteira','Valor R$ da carteira']] = ''
        ativo_novo['Diferença VI X VC'] = ativo_novo['Valor R$ Ideal']


        basket_geral_con = pd.concat([basket_geral_con,ativo_novo]).drop(columns='BOVA11')


        precos_de_mercado = []
        for ativo in lista_acoes_em_caixa:
                    ticker = yf.Ticker(ativo +'.SA')
                    preco_atual = ticker.history(period='2m')['Close'].iloc[-1]
                
                    precos_de_mercado.append([ativo,preco_atual])

        cotacoes_momento = pd.DataFrame(precos_de_mercado,columns =['Ativo','Cotação atual'])   
        basket = basket_geral_con.merge(cotacoes_momento,left_on='Produto',right_on='Ativo',how='outer').fillna(0)
        basket['Quantidade'] = round(basket['Diferença VI X VC']/basket['Cotação atual'],0).abs()
        basket['C/V'] = np.where(basket['Diferença VI X VC']>0,'C','V')
        basket['Validade']='DIA'
        basket = basket.rename(columns={'Cotação atual':'Preço'}).iloc[:-6,[7,20,19,18,1,21,4,5,6,16,-6]].dropna().rename(columns={'Produto':'Ativo'})
        return basket


    




