import pandas as pd
import streamlit as st
import datetime

dia = datetime.datetime.now().strftime('%d/%m/%Y')


class Relatorio_Comercial():
    def __init__(self):
        print('hello world')

    def compilando_controle(self,controle,co_admin,pl_d_2):
        def alterando_nome_ultima_col(df):
            col = df.columns[-1]
            df  = df.rename(columns={col:'D-1'})
            return df

        btg_pl_d2 = pd.read_excel(pl_d_2).iloc[:,[0,2]]

        st.dataframe(btg_pl_d2)
        
        controle_ = pd.read_excel(controle,2,skiprows=1).iloc[:-5,[2,5,12,10,7,13,-1]]

       
        guide = pd.read_excel(controle,3,skiprows=1).iloc[:-5,[2,5,12,10,7,13,-1]]
        agora = pd.read_excel(controle,4,skiprows=1).iloc[:-5,[2,5,12,10,7,13,-1]]
        co_admin = pd.read_excel(co_admin,1,skiprows=1).iloc[:-5,[2,5,12,10,7,13,-1]]

        controle_ = alterando_nome_ultima_col(controle_)
        guide = alterando_nome_ultima_col(guide)
        agora = alterando_nome_ultima_col(agora)
        co_admin = alterando_nome_ultima_col(co_admin)


        controle_ = pd.concat([controle_,controle_,guide,agora,co_admin]).reset_index(drop='index')

        controle_['Conta'] = controle_['Conta'].astype(str).str[:-2].apply(lambda  x: '00'+x)
        controle_ = controle_.merge(btg_pl_d2,on='Conta',how='outer')
        controle_['Retorno'] = ((controle_['D-1']-controle_['Valor'])/controle_['D-1'])
        

        assssores_theo =['Theo Ramos Moutinho', 'Bruno Henrique' 'Rejane Machado Souza',
                        'Matheus Vilar', 'Gustavo Amorim','Caroline Facó Ehlers', 
                        'Yasmin Maia Muniz Xavier',  'Luca Bueno','Alexandre Teixeira Campos',  'Pedro Vinicius Pereira De Andrade',
                        'Breno Lemes',  'Guilherme dos Santos','Cecilia Arcoverde Bezerra Pires','Gabriel Bicalho Fontes Raydan',
                        'Leandro Soares Lemos De Sousa', 'Bruno Ribeiro','Bruno De Carvalho Borges',
                        'Antonio Carlos Dos Santos', 'Augusto Sampaio', 'Rogerio Magalhaes Coelho','Neyla Mara De Sousa Abrantes Pereira']


        controle_ = controle_[controle_['Assessor'].isin(assssores_theo)].reset_index()
        controle_=controle_.rename(columns ={
                                             'Valor':'D-2',
                                             })
        controle_agregado = controle_.groupby('Assessor')[['D-1','D-2','Retorno']].sum()
        

        return controle_agregado
    

if __name__=='__main__':
    
    rlt = Relatorio_Comercial()    

    planilha = rlt.compilando_controle(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos.xlsx',
                                       r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos - Carteiras Co-Administradas.xlsx',
                                       r'C:\Users\lauro.telles\Desktop\Dados comercial\PL Diario\PL Total 03 06 2024.xlsx')
    
    st.subheader('Arquivo Final')
    st.dataframe(planilha)
    planilha.to_excel(r'C:\Users\lauro.telles\Desktop\Dados comercial\04-06-2024 Dados comercial.xlsx')








