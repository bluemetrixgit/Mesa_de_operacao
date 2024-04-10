import pandas as pd
import numpy as np
import streamlit as st

class Carteiras_co_admin():
    
    def __init__(self):
        print('Hello world')

    def juntando_planilhas(self,pl,controle_co_admin,saldo):
        self.pl = pl
        self.controle_co = controle_co_admin
        self.saldo = saldo
        arquivo_final = pd.merge(self.pl,self.saldo, on='Conta',how='outer')  
        controle_co_admin['Conta'] = self.controle_co['Conta'].astype(str).str[:-2].apply(lambda x: '00'+ x)
        controle_co_admin_df = pd.DataFrame(controle_co_admin)
        arquivo_final_completo = pd.merge(arquivo_final,controle_co_admin_df,on
                                            ='Conta',how='right').iloc[:-5,[0,2,4,6,10,16,11,20,21,22,-1]].rename(columns={'Valor':'PL'})
        coluna_final = arquivo_final_completo.columns[-1]

        arquivo_final_completo = arquivo_final_completo.rename(columns={coluna_final:'PL Planilha Controle'}).iloc[:,[0,2,3,5,6,7,8,1,4,9,10]]
        arquivo_final_completo = arquivo_final_completo[(arquivo_final_completo['Saldo']>1000)|(arquivo_final_completo['Saldo']<0)].sort_values(by='Saldo',ascending=False)
        return arquivo_final_completo

if __name__=='__main__':

    ler_arquivos = Carteiras_co_admin()            
    dados_agregados = ler_arquivos.juntando_planilhas()
    print(dados_agregados)
    st.dataframe(dados_agregados)
