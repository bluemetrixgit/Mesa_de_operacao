import pandas as pd
import numpy as np
import streamlit as st


class RentabilidadeMedia():
    def __init__(self):
        print('hello world')

    def compilando_arquivos(self):
        rentabilidade = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Rentabilidade 05 2024.xlsx',skiprows=1)
        rentabilidade['Rentabilidade'] = rentabilidade['Rentabilidade']*100
        rentabilidade = rentabilidade[(rentabilidade['Rentabilidade']>0)|(rentabilidade['Rentabilidade']<0)]    
        controle = pd.read_excel(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos.xlsx',2,skiprows=1).iloc[:-5,[2,12,-2]]
        controle['Conta'] = controle['Conta'].astype(str).str[:-2].apply(lambda x: '00'+x)

        st.dataframe(rentabilidade)
        st.dataframe(controle)
        
        arquivo_final = pd.merge(controle,rentabilidade,on='Conta',how='outer')
        arquivo_final_agr = round(arquivo_final.groupby('Carteira')['Rentabilidade'].mean().reset_index(),2)
        arquivo_final_agr['Rentabilidade'] = arquivo_final_agr['Rentabilidade'].apply(lambda x: f'{x:.2f}')
        arquivo_final_agr = arquivo_final_agr.rename(columns={"Rentabilidade":'Rentabilidade  05/2024'})
        return arquivo_final_agr



if __name__=='__main__':

    rent = RentabilidadeMedia()

    arquivos = rent.compilando_arquivos()
    st.table(arquivos)





