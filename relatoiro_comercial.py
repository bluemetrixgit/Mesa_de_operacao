import pandas as pd
import streamlit as st
import datetime

dia = datetime.datetime.now().strftime('%d/%m/%Y')


class Relatorio_Comercial():
    def __init__(self):
        print('hello world')

    def compilando_controle(self,controle,co_admin,pl_d_2,btg_pl_d1):

        btg_pl_d2 = pd.read_excel(pl_d_2).iloc[:,[0,2]]
        btg_pl_d1 = pd.read_excel(btg_pl_d1).iloc[:,[0,2]].rename(columns={"Valor":"D-1"})
 
        controle_ = pd.read_excel(controle,2,skiprows=1).iloc[:-5,[2,5,12,10,7,13]]
        co_admin = pd.read_excel(co_admin,1,skiprows=1).iloc[:-5,[2,5,12,10,7,13]]

        controle_ = pd.concat([controle_,co_admin]).reset_index(drop='index')

        controle_['Conta'] = controle_['Conta'].astype(str).str[:-2].apply(lambda  x: '00'+x)
        controle_ = controle_.merge(btg_pl_d2,on='Conta',how='outer').merge(btg_pl_d1,on='Conta',how='outer')
        

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
        controle_agregado = controle_.groupby('Assessor')[['D-1','D-2']].sum().reset_index()

        controle_agregado['Retorno'] = (controle_agregado['D-1']-controle_agregado['D-2'])/controle_agregado['D-1']

        

        return controle_agregado





    def mensal_compilando_controle(self,controle,co_admin,pl_d_2,btg_pl_d1):
    
        btg_pl_d2 = pd.read_excel(pl_d_2).iloc[:,[0,2]]
        btg_pl_d1 = pd.read_excel(btg_pl_d1).iloc[:,[0,2]].rename(columns={"Valor":"D-1"})
 
        controle_ = pd.read_excel(controle,2,skiprows=1).iloc[:-5,[2,5,12,10,7,13]]
        co_admin = pd.read_excel(co_admin,1,skiprows=1).iloc[:-5,[2,5,12,10,7,13]]

        controle_ = pd.concat([controle_,co_admin]).reset_index(drop='index')

        controle_['Conta'] = controle_['Conta'].astype(str).str[:-2].apply(lambda  x: '00'+x)
        controle_ = controle_.merge(btg_pl_d2,on='Conta',how='outer').merge(btg_pl_d1,on='Conta',how='outer')
        

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
        controle_agregado = controle_.groupby('Assessor')[['D-1','D-2']].sum().reset_index()

        controle_agregado['Retorno'] = (controle_agregado['D-1']-controle_agregado['D-2'])/controle_agregado['D-1']
        controle_agregado = controle_agregado.rename(columns={'D-1':'Maio','D-2':'Abril'}).iloc[:,[0,2,1,3]]

        

        return controle_agregado
    

    def mesclando_mensal_diario(self,planilha,mensal_planilha):
        mensal_planilha = mensal_planilha.merge(planilha,on='Assessor',how='outer')
        mensal_planilha = mensal_planilha.rename(columns={"Retorno_x":'Variação Mensal','Retorno_y':'Variação D-2 D-1'})

        return mensal_planilha


if __name__=='__main__':
    
    rlt = Relatorio_Comercial()    

    planilha = rlt.compilando_controle(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos.xlsx',
                                       r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos - Carteiras Co-Administradas.xlsx',
                                       r'C:\Users\lauro.telles\Desktop\Dados comercial\PL Diario\PL Total 24 06 2024.xlsx',
                                       r'C:\Users\lauro.telles\Desktop\Dados comercial\PL Diario\PL Total 21 06 2024.xlsx')
    
    st.subheader('Arquivo Final')
    st.dataframe(planilha)
    #planilha.to_excel(r'C:\Users\lauro.telles\Desktop\Dados comercial\10-06-2024 Dados comercial.xlsx')

    mensal_planilha = rlt.mensal_compilando_controle(r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos.xlsx',
                                       r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\Controle de Contratos - Carteiras Co-Administradas.xlsx',
                                       r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\pl_mensal\PL Total Maio.xlsx',
                                       r'C:\Users\lauro.telles\Desktop\Mesa_app_3\app_mesa_de_opera-es_corrigido\pl_mensal\PL Total Abril.xlsx')
    st.subheader('Variação Mensal Arquivo Final')
    st.dataframe(mensal_planilha)
    #planilha.to_excel(r'C:\Users\lauro.telles\Desktop\Dados comercial\Mensal\Mensal Abril-Maio.xlsx')

    planilha_mesclada = rlt.mesclando_mensal_diario(planilha,mensal_planilha)
    st.subheader('Planilhas mescladas')
    st.dataframe(planilha_mesclada)

    planilha_mesclada.to_excel(r'C:\Users\lauro.telles\Desktop\Dados comercial\Dados Comercial 24 06 2024.xlsx')







