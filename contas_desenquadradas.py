import pandas as pd
import numpy as np
import streamlit as st
from functools import reduce




equities = {'Renda Variável': 81,'Pós-fixado':19}
income = {'Pós-fixado':32,'Inflação':32,'Pré-fixado':35,'FundoDI':1}
conservadora = {'Pós-fixado':26.70,'Inflação':27.20,'Pré-fixado':29.75,'FundoDI':0.85, 'Renda Variável':15}
moderada = {'Pós-fixado':22.40,'Inflação':22.40,'Pré-fixado':24.50,'FundoDI':0.70, 'Renda Variável':30}
arrojada = {'Pós-fixado':16,'Inflação':16,'Pré-fixado':17.50,'FundoDI':0.50, 'Renda Variável':50}

class Contas_desenquadradas():
    def __init__(self):
        print('hello world')

    def lendo_e_tratando_arquivos(self,controle,posicao):

        controle = controle.iloc[:,[1,2,12,6,7,8,16,17,18,9]]
        controle['Conta'] = controle['Conta'].astype(str).apply(lambda x: '00'+x).str[:-2]



        self.posicao = posicao
        self.posicao = self.posicao.loc[~((self.posicao['Produto'].str.contains('PREV'))|(self.posicao['Produto']=='COE'))]

        self.posicao = self.posicao.groupby(['Conta','Estratégia'])['Valor Líquido'].sum().reset_index()
        pl_das_contas = self.posicao.groupby('Conta')['Valor Líquido'].sum().reset_index()
        self.posicao = self.posicao.merge(pl_das_contas,on='Conta',how='outer').merge(controle,on='Conta',how='outer')
        self.posicao['Posicao Porcentagem'] = round((self.posicao['Valor Líquido_x']/self.posicao['Valor Líquido_y'])*100,2)

        return self.posicao
    def criando_dfs_e_checando_enquadramento(self,posicao,variacao):

        def criando_carteiras(carteira,proporcao_e_ativos):
            
            carteira = pd.DataFrame(list(proporcao_e_ativos.items()),columns=[f'Ativo','Proporção'])
            # carteira[f'Proporção__{carteira}'] = carteira['Proporção']
            # carteira = carteira.drop(columns='Proporção')
            return carteira


        carteira_equity = criando_carteiras('Carteira_equity',equities)
        carteira_income = criando_carteiras('Carteira Income',income)
        carteira_conservadora = criando_carteiras('Carteira CON',conservadora)
        carteira_moderada = criando_carteiras('Carteira MOD', moderada)
        carteira_arrojada = criando_carteiras('Carteira ARR',arrojada)



        posicao_income = posicao[posicao['Carteira']=='INC']
        posicao_con = posicao[posicao['Carteira']=='CON']
        posicao_mod = posicao[posicao['Carteira']=='MOD']
        posicao_arr = posicao[posicao['Carteira']=='ARR']
        posicao_eqt = posicao[posicao['Carteira']=='EQT']

        posicao_income = posicao_income.merge(carteira_income,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Income'})
        posicao_con = posicao_con.merge(carteira_conservadora,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Con'})
        posicao_mod = posicao_mod.merge(carteira_moderada,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Mod'})
        posicao_arr = posicao_arr.merge(carteira_arrojada,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Arr'})
        posicao_eqt = posicao_eqt.merge(carteira_equity,left_on='Estratégia',right_on='Ativo').rename(columns={'Ativo':'Ativo_Eqt'})

        dfs_checar_enquadramento = [posicao_income,posicao_con,posicao_mod,posicao_arr,posicao_eqt]
        for dataframe in dfs_checar_enquadramento:
            dataframe['Enquadramento'] = dataframe['Posicao Porcentagem']-dataframe['Proporção']

        self.arquivo_final = pd.concat(dfs_checar_enquadramento)

        self.arquivo_final = self.arquivo_final[(self.arquivo_final['Enquadramento']>variacao)|(self.arquivo_final['Enquadramento']<-variacao)].reset_index().drop(columns='index').iloc[:,:-4]

        return self.arquivo_final


    def intermediacao_lendo_e_tratando_arquivos(self,controle,posicao):
        from datetime import datetime,timedelta
        
        data_limite = datetime.now()+timedelta(days=180)


        controle = controle.iloc[:,[1,2,12,6,7,8,16,17,18,9]]
        controle['Conta'] = controle['Conta'].astype(str).apply(lambda x: '00'+x).str[:-2]

        self.posicao = posicao
        self.posicao = self.posicao[self.posicao['Vencimento']>data_limite]

        
        # self.posicao = self.posicao.loc[~(
        #     (self.posicao['Produto'].str.contains('PREV'))|(
        #         self.posicao['Produto']=='COE')|(
        #             self.posicao['Estratégia'].str.contains('Renda Variável'))|(
        #                 self.posicao['Produto'].str.contains('BLUEMETRIX RF ATIVO FI RF'))|(
        #                     self.posicao['Produto'].str.contains('CDB')&self.posicao['Emissor'].str.contains('BANCO BTG PACTUAL S A'))|(
        #                 self.posicao['Produto'].str.contains('TESOURO DIRETO'))|(
        #                     self.posicao['Produto'].str.contains('NTN'))|(
        #                         self.posicao['Produto'].str.contains('NTNB'))|(
        #                             self.posicao['Produto'].str.contains('FII'))|(
        #                                 self.posicao['Produto'].str.contains('FI'))|(
        #                                     self.posicao['Produto'].str.contains('LTN'))|(
        #                                         self.posicao['Produto'].str.contains('LF'))
        #                     )]

        self.posicao = self.posicao.groupby(['Conta','Estratégia','Produto'])['Valor Líquido'].sum().reset_index()
        pl_das_contas = self.posicao.groupby('Conta')['Valor Líquido'].sum().reset_index()
        self.posicao = self.posicao.merge(pl_das_contas,on='Conta',how='outer').merge(controle,on='Conta',how='outer')
        self.posicao['Posicao Porcentagem'] = round((self.posicao['Valor Líquido_x']/self.posicao['Valor Líquido_y'])*100,2)
        st.dataframe(self.posicao)

    def rem_cri_cra_intermediacao_lendo_e_tratando_arquivos(self,controle,posicao):
        from datetime import datetime,timedelta
        
        data_limite = datetime.now()+timedelta(days=180)


        controle = controle.iloc[:,[1,2,12,6,7,8,16,17,18,9]]
        controle['Conta'] = controle['Conta'].astype(str).apply(lambda x: '00'+x).str[:-2]
        
        self.posicao = posicao

        self.posicao = self.posicao[self.posicao['Vencimento']>data_limite]

        
        self.posicao = self.posicao.loc[~(
            (self.posicao['Produto'].str.contains('PREV'))|(
                self.posicao['Produto']=='COE')|(
                    self.posicao['Estratégia'].str.contains('Renda Variável'))|(
                        self.posicao['Produto'].str.contains('BLUEMETRIX RF ATIVO FI RF'))|(
                            self.posicao['Produto'].str.contains('CDB')&self.posicao['Emissor'].str.contains('BANCO BTG PACTUAL S A'))|(
                        self.posicao['Produto'].str.contains('TESOURO DIRETO'))|(
                            self.posicao['Produto'].str.contains('NTN'))|(
                                self.posicao['Produto'].str.contains('NTNB'))|(
                                    self.posicao['Produto'].str.contains('FII'))|(
                                        self.posicao['Produto'].str.contains('FI'))|(
                                            self.posicao['Produto'].str.contains('LTN'))|(
                                                self.posicao['Produto'].str.contains('LF'))|(
                                                    self.posicao['Produto'].str.contains('CRI'))|(
                                                        self.posicao['Produto'].str.contains('CRA'))|(
                                                            self.posicao['Produto'].str.contains('Deb'))
                            )]

        self.posicao = self.posicao.groupby(['Conta','Estratégia'])['Valor Líquido'].sum().reset_index()
        pl_das_contas = self.posicao.groupby('Conta')['Valor Líquido'].sum().reset_index()
        self.posicao = self.posicao.merge(pl_das_contas,on='Conta',how='outer').merge(controle,on='Conta',how='outer')
        self.posicao['Posicao Porcentagem'] = round((self.posicao['Valor Líquido_x']/self.posicao['Valor Líquido_y'])*100,2)

        return self.posicao
    