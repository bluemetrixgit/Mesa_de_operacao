import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf
from numpy import linalg as LA
from plotly import graph_objects as go

st.set_page_config(layout='wide')
st.set_option('deprecation.showPyplotGlobalUse', False)

class Risco():
    def __init__(self):
        print('Hello world')

    def var_historico(self,periodo_inicial,period_final):


        lista_acoes = ['ARZZ3.SA','ASAI3.SA','BBSE3.SA','BOVA11.SA','CPFE3.SA','EGIE3.SA','HYPE3.SA','KEPL3.SA','LEVE3.SA','PRIO3.SA','PSSA3.SA','SBSP3.SA','SLCE3.SA','VALE3.SA','VIVT3.SA']
        pesos_carteira = [0.05,0.06,0.05,0.10,0.05,0.05,0.08,0.08,0.05,0.08,0.02,0.04,0.07,0.10,0.05]


        carteira = yf.download(lista_acoes,start=periodo_inicial,end=period_final)['Adj Close']
        retornos = carteira.pct_change()
        retorno_da_carteira = (retornos*pesos_carteira).sum(axis=1)

        self.retorno_portfolio = pd.DataFrame()
        self.retorno_portfolio['Retornos'] = retorno_da_carteira
        var_95 = round((np.nanpercentile(self.retorno_portfolio,5))*100, 2) 
        st.write('O VAR pelo metodo historico da carteira para o período selecionado e :')
        st.warning(var_95)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=self.retorno_portfolio['Retornos']))
        fig.update_layout(title ='Distribuição dos Retornos Carteira')

        retorno_acumulado = round((((1+self.retorno_portfolio['Retornos']).cumprod())-1)*100,2)
        grafico_de_linha = go.Figure()
        grafico_de_linha.add_trace(go.Scatter(x=self.retorno_portfolio.index,y=retorno_acumulado,mode='lines',name= 'Retorno Acumulado'))
        grafico_de_linha.update_traces(line=dict(color='#ADFF2F'))
        grafico_de_linha.update_layout(title='Retorno Acumulado ao Longo do Tempo')
       
     

        st.plotly_chart(grafico_de_linha)        
       
        return st.plotly_chart(fig)



    '''Monte carlo'''

    def monte_carlo(self,dias):
            
        lista_acoes = ['ARZZ3','ASAI3','BBSE3','BOVA11','CPFE3','EGIE3','HYPE3','KEPL3','LEVE3','PRIO3','PSSA3','SBSP3','SLCE3','VALE3','VIVT3']
        lista_acoes = [acao + ".SA" for acao in lista_acoes]

        data_final = dt.datetime.now()
        data_inicial = data_final - dt.timedelta(days=300)

        precos = yf.download(lista_acoes, data_inicial, data_final)['Adj Close']

        #calculando retornos pegando matriz de covariância 

        retornos = precos.pct_change().dropna()
        media_retornos = retornos.mean()
        matriz_covariancia = retornos.cov()
        pesos_carteira = [0.05,0.06,0.05,0.10,0.05,0.05,0.08,0.08,0.05,0.08,0.02,0.04,0.07,0.10,0.05]
        numero_acoes = len(lista_acoes)


        numero_simulacoes = 10000
        dias_projetados = dias 
        capital_inicial = 100000


        retorno_medio = retornos.mean(axis = 0).to_numpy() 
        matriz_retorno_medio = retorno_medio * np.ones(shape = (dias_projetados, numero_acoes))

        L = LA.cholesky(matriz_covariancia)
        


        self.retornos_carteira = np.zeros([dias_projetados, numero_simulacoes]) #cada coluna é uma simulação
        montante_final = np.zeros(numero_simulacoes)

        for s in range(numero_simulacoes):

            Rpdf = np.random.normal(size=(dias_projetados, numero_acoes)) 
            
            retornos_sintéticos = matriz_retorno_medio + np.inner(Rpdf, L) #unica coisa random é o Rpdf
            
            self.retornos_carteira[:, s] = np.cumprod(np.inner(pesos_carteira, 
                                                        retornos_sintéticos) + 1) * capital_inicial
            montante_final[s] = self.retornos_carteira[-1, s]
            
        montante_99 = str(round(np.percentile(montante_final, 1),2))
        montante_95 = str(round(np.percentile(montante_final, 5),2))
        montante_mediano = str(round(np.percentile(montante_final, 50),2))
        cenarios_com_lucro = str((len(montante_final[montante_final > 100000])/
                                        len(montante_final)) * 100) + "%"


        st.text(f"Ao investir R$ 100.000,00 na carteira, podemos esperar esses resultados para os próximo período,")
        st.text("utilizando o método de Monte Carlo com 10 mil simulações:")

        st.caption(f':green[Com 50% de probabilidade, o montante será maior que R$ {montante_mediano}.]') 

        st.caption(f':red[Com 95% de probabilidade, o montante será maior que R$ {montante_95}.]')

        st.caption(f":red[Com 99% de probabilidade, o montante será maior que R$ {montante_99}.]")

        st.caption(f':green[Em {cenarios_com_lucro} dos cenários, foi possível obter lucro no período.]')

        plt.plot(self.retornos_carteira, linewidth=1)
        plt.ylabel('Dinheiro')
        plt.xlabel('Dias')

        st.pyplot()




        config = dict(histtype = "stepfilled", alpha = 0.8, density = False, bins = 150)
        fig, ax = plt.subplots()
        ax.hist(montante_final, **config)
        ax.xaxis.set_major_formatter('R${x:.0f}')
        distribuicao_monte = plt.title('Distribuição montantes finais com simulação MC')
        distribuicao_monte = plt.xlabel('Montante final (R$)')
        distribuicao_monte = plt.ylabel("Frequência")

        return st.pyplot(fig)
    

    def nova_carteira_monte_carlo(self,lista_de_acoes,dias,pesos):
        

        data_final = dt.datetime.now()
        data_inicial = data_final - dt.timedelta(days=300)

        precos = yf.download(lista_de_acoes, data_inicial, data_final)['Adj Close']

        #calculando retornos pegando matriz de covariância 

        retornos = precos.pct_change().dropna()
        media_retornos = retornos.mean()
        matriz_covariancia = retornos.cov()
        pesos_carteira = [pesos]
        numero_acoes = len(lista_de_acoes)


        numero_simulacoes = 10000
        dias_projetados = dias 
        capital_inicial = 100000


        retorno_medio = retornos.mean(axis = 0).to_numpy() 
        matriz_retorno_medio = retorno_medio * np.ones(shape = (dias_projetados, numero_acoes))

        L = LA.cholesky(matriz_covariancia)
        


        self.retornos_carteira = np.zeros([dias_projetados, numero_simulacoes]) #cada coluna é uma simulação
        montante_final = np.zeros(numero_simulacoes)

        for s in range(numero_simulacoes):

            Rpdf = np.random.normal(size=(dias_projetados, numero_acoes)) 
            
            retornos_sintéticos = matriz_retorno_medio + np.inner(Rpdf, L) #unica coisa random é o Rpdf
            
            self.retornos_carteira[:, s] = np.cumprod(np.inner(pesos_carteira, 
                                                        retornos_sintéticos) + 1) * capital_inicial
            montante_final[s] = self.retornos_carteira[-1, s]
            
        montante_99 = str(round(np.percentile(montante_final, 1),2))
        montante_95 = str(round(np.percentile(montante_final, 5),2))
        montante_mediano = str(round(np.percentile(montante_final, 50),2))
        cenarios_com_lucro = str((len(montante_final[montante_final > 100000])/
                                        len(montante_final)) * 100) + "%"


        st.text(f"Ao investir R$ 100.000,00 na carteira, podemos esperar esses resultados para os próximo período,")
        st.text("utilizando o método de Monte Carlo com 10 mil simulações:")

        st.caption(f':green[Com 50% de probabilidade, o montante será maior que R$ {montante_mediano}.]') 

        st.caption(f':red[Com 95% de probabilidade, o montante será maior que R$ {montante_95}.]')

        st.caption(f":red[Com 99% de probabilidade, o montante será maior que R$ {montante_99}.]")

        st.caption(f':green[Em {cenarios_com_lucro} dos cenários, foi possível obter lucro no período.]')

        plt.plot(self.retornos_carteira, linewidth=1)
        plt.ylabel('Dinheiro')
        plt.xlabel('Dias')

        st.pyplot()




        config = dict(histtype = "stepfilled", alpha = 0.8, density = False, bins = 150)
        fig, ax = plt.subplots()
        ax.hist(montante_final, **config)
        ax.xaxis.set_major_formatter('R${x:.0f}')
        distribuicao_monte = plt.title('Distribuição montantes finais com simulação MC')
        distribuicao_monte = plt.xlabel('Montante final (R$)')
        distribuicao_monte = plt.ylabel("Frequência")

        return st.pyplot(fig)



if __name__ == '__main__':


    st.title('Equities')
    col1, col2 = st.columns(2)

    rc = Risco()
    with col1:
        st.subheader('VAR Metodo historico ')
        st.text('')
        st.text('')
        st.text('')
        data_inicial = st.date_input('Selecione a data inicial')
        data_final = st.date_input('Selecione o periodo final')
        #try:   
        var_historico = rc.var_historico(data_inicial,data_final)
        #except:
        #    pass
    
    with col2:
        st.subheader('Simulção Monte Carlo')
        dias_uteis = float(st.text_input('Coloque o número de dias úteis:', value=1))
        try:
            if st.button('Rodar Simulação Equities'):
                monte_carlo = rc.monte_carlo(int(dias_uteis))
            else:
                pass
        except:
            pass


        lista_b3 = ['PRIO3.SA','WEGE3.SA','CSNA3.SA']    

        lista_de_acoes = st.multiselect('Coloque os ativos para simulação:',options=lista_b3)
        lista_de_pesos = []

        for ativo in lista_de_acoes:
            peso = int(st.text_input(f'Coloque o peso para o {ativo}'))
            lista_de_pesos.append(peso)
        print(lista_de_pesos)    

        dias_uteis_nova_simulacao = int(float(st.text_input('Coloque o número de dias úteis:', value=125)))

        if st.button('Rodar Simulação'):
            monte_carlo_nova_carteira = rc.nova_carteira_monte_carlo(lista_de_acoes, dias_uteis_nova_simulacao, lista_de_pesos)
'BHIA3'
'RZAT11'
'GRWA11'
'CRAA11'
'ZAMP3'
'HGAG11'
'BBGO11'
'AGRX11'
'PLCA11'
'RURA11'
'SNAG11'
'GCRA11'
'VCRA11'
'KNCA11'
'NCRA11'
'CPTR11'
'FGAA11'
'EGAF11'
'VGIA11'
'LSAG11'
'N2ET34'
'M1TA34'
'FOOD11'
'AERI3F'	
'AERI3'
'ICBR3'
'DOTZ3F'	
'DOTZ3'
'OLL3'
'VIIA3F'
'ARML3'
'MLAS3'
'BAV3'
'TTEN3'
'BRBI11'
'NINJ3'
'ATEA3'
'MODL4'
'MODL11'
'MODL3'
'VITT3'
'KRSA3'	
'CXSE3'
'RIOS3'
'HCAR3'
'GGPS3'
'MATD3'
'ALLD3'
'BLAU3'
'ATMP3'
'ASAI3'
'JSLG3'
'CMIN3'
'ELMD3'
'ORVR3'
'OPCT3'
'WEST3'
'CSED3'
'BMOB3'
'JALL3'
'MBLY3'
'ESPA3'
'VAMO3'
'INTB3'
'CJCT11'
'BMLC11'
'RECR11'
'URPR11'
'DEVA11'
'MFAI11'
'iNGRD3'
'AVLL3'
'RRRP3'
'ENJU3'
'CASH3'
'TFCO4'
'CONX3'
'GMAT3'
'SEQL3'
'PASS3'
'SCPC'
'BOAS3'
'MELK3'
'HBSA3'
'SIMH3F'
'CURY3'
'PLPL3'
'PETZ3'
'PGMN3'
'LAVV3'
'LJQQ3'
'DMVF3'
'SOMA3'
'RIVA3'
'aAMBP3'
'rALPK3'
'MTRE3'
'MDNE3'
'BDLL4F'	
'BDLL3F'
      




