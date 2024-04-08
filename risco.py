import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as dt
import yfinance as yf
from numpy import linalg as LA
from plotly import graph_objects as go
from bs4 import BeautifulSoup
import requests





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
    

    def var_historico_simulacao(self,periodo_inicial,period_final,acoes,pesos):


        lista_acoes = acoes
        pesos_carteira = pesos


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
    
        retorno_acumulado = round(((self.retorno_portfolio['Retornos']+1).cumprod()-1)*100,2)

        grafico_de_linha = go.Figure()
        grafico_de_linha.add_trace(go.Scatter(x=self.retorno_portfolio.index,y=retorno_acumulado,mode='lines',name= 'Retorno Acumulado'))
        grafico_de_linha.update_traces(line=dict(color='#1E90FF'))
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



# if __name__ == '__main__':
            
    # url =  'https://www.infomoney.com.br/cotacoes/empresas-b3/' 
    # response = requests.get(url)

    # soup = BeautifulSoup(response.text, 'html.parser')

    # lista_de_ativos = soup.find_all('td')


    # lista_de_ativos_texto = []

    # for ativo in lista_de_ativos:
    #     nome_ativo = ativo.find_all('a')

    #     for nome in nome_ativo:
    #         lista_de_ativos_texto.append(nome.text.strip())


    # data_frame = pd.DataFrame(lista_de_ativos_texto,columns=['Ativo'])
    # data_frame['Ativo']=data_frame['Ativo'].apply(lambda x: f"{x}.SA")
    

    # lista_ativos_b = data_frame['Ativo'].to_list()  
    
    
    
    # lista_ativos_b3 = ['BHIA3.SA', 'RZAT11.SA', 'GRWA11.SA', 'CRAA11.SA', 'ZAMP3.SA', 'HGAG11.SA', 'BBGO11.SA', 'AGRX11.SA', 'PLCA11.SA', 'RURA11.SA', 'SNAG11.SA', 'GCRA11.SA', 'VCRA11.SA', 'KNCA11.SA', 'NCRA11.SA', 'CPTR11.SA', 'FGAA11.SA', 'EGAF11.SA', 'VGIA11.SA', 'LSAG11.SA', 'N2ET34.SA', 'M1TA34.SA', 'FOOD11.SA', 'AERI3F.SA', 'AERI3.SA', 'ICBR3.SA', 'DOTZ3F.SA', 'DOTZ3.SA', 'GOLL3.SA', 'VIIA3F.SA', 'ARML3.SA', 'MLAS3.SA', 'CBAV3.SA', 'TTEN3.SA', 'BRBI11.SA', 'NINJ3.SA', 'ATEA3.SA', 'MODL4.SA', 'MODL11.SA', 'MODL3.SA', 'VITT3.SA', 'KRSA3.SA', 
    #                 '.SA', 'CXSE3.SA', 'RIOS3.SA', 'HCAR3.SA', 'GGPS3.SA', 'MATD3.SA', 'ALLD3.SA', 'BLAU3.SA', 'ATMP3.SA', 'ASAI3.SA', 'JSLG3.SA', 'CMIN3.SA', 'ELMD3.SA', 'ORVR3.SA', 'OPCT3.SA', 'WEST3.SA', 'CSED3.SA', 'BMOB3.SA', 'JALL3.SA', 'MBLY3.SA', 'ESPA3.SA', 'VAMO3.SA', 'INTB3.SA', 'CJCT11.SA', 'BMLC11.SA', 'RECR11.SA', 'URPR11.SA', 'DEVA11.SA', 'MFAI11.SA', 'NGRD3.SA', 'AVLL3.SA', 'RRRP3.SA', 'ENJU3.SA', 'CASH3.SA', 'TFCO4.SA', 'CONX3.SA', 'GMAT3.SA', 'SEQL3.SA', 'PASS3.SA', 'BOAS3.SA', 'MELK3.SA', 'HBSA3.SA', 'SIMH3F.SA', 'CURY3.SA', 'PLPL3.SA', 'PETZ3.SA', 'PGMN3.SA', 'LAVV3.SA', 'LJQQ3.SA', 'DMVF3.SA', 'SOMA3.SA', 'RIVA3.SA', 'AMBP3.SA', 'ALPK3.SA', 'MTRE3.SA', 'MDNE3.SA', 'BDLL4F.SA', 'BDLL3F.SA', 'ALOS3.SA', 'VIIA3.SA', 'CEDO4F.SA', 'CEDO3F.SA', 'CEDO4.SA', 'CEDO3.SA', 'NFLX34F.SA', 'NFLX34.SA', 'NIKE34F.SA', 'NIKE34.SA', 'MCDC34F.SA', 'MCDC34.SA', 'HOME34F.SA', 'HOME34.SA', 'FDMO34F.SA', 'FDMO34.SA', 'CMCS34F.SA', 'CMCS34.SA', 'AMZO34F.SA', 'RDNI3F.SA', 'RDNI3.SA', 'SLED4F.SA', 'SLED3F.SA', 'SLED3.SA', 'RSID3F.SA', 'RSID3.SA', 'MNDL3F.SA', 'MNDL3.SA', 'LEVE3F.SA', 'LEVE3.SA', 'CTKA4F.SA', 'CTKA3F.SA', 'CTKA4.SA', 'CTKA3.SA', 'MYPK3F.SA', 'MYPK3.SA', 'GRND3F.SA', 'GRND3.SA', 'LCAM3F.SA', 'LCAM3.SA', 'CEAB3.SA', 'VSTE3F.SA', 'VSTE3.SA', 'CGRA3F.SA', 'CGRA4F.SA', 'CGRA4.SA', 'CGRA3.SA', 'ESTR4F.SA', 'ESTR3F.SA', 'ESTR4.SA', 'ESTR3.SA', 'DIRR3F.SA', 'DIRR3.SA', 'CTNM3F.SA', 'CTNM4F.SA', 'CTNM4.SA', 'CTNM3.SA', 'ANIM3F.SA', 'EVEN3F.SA', 'EVEN3.SA', 'AMAR3F.SA', 'AMAR3.SA', 'MOVI3F.SA', 'MOVI3.SA', 'JHSF3F.SA', 'JHSF3.SA', 'HBOR3F.SA', 'HBOR3.SA', 'PDGR3F.SA', 'PDGR3.SA', 'ARZZ3F.SA', 'EZTC3F.SA', 'EZTC3.SA', 'ALPA3F.SA', 'ALPA4F.SA', 'RENT3F.SA', 'RENT3.SA', 'MRVE3F.SA', 'MRVE3.SA', 'MGLU3F.SA', 'MGLU3.SA', 'LREN3F.SA', 'LREN3.SA', 'COGN3F.SA', 'COGN3.SA', 'WHRL4.SA', 'WHRL3.SA', 'TCSA3.SA', 'SBUB34.SA', 'SMLS3.SA', 'SEER3.SA', 'SLED4.SA', 'HOOT4.SA', 'GFSA3.SA', 'GFSA3F.SA', 'YDUQ3.SA', 'CYRE3.SA', 'CVCB3.SA', 'SBFG3F.SA', 'SBFG3.SA', 'PRVA3.SA', 'WALM34F.SA', 'WALM34.SA', 'SBUB34F.SA', 'PGCO34F.SA', 'PEPB34F.SA', 'PEPB34.SA', 'COLG34F.SA', 'COLG34.SA', 'COCA34F.SA', 'COCA34.SA', 'AVON34F.SA', 'AVON34.SA', 'SMTO3F.SA', 'SMTO3.SA', 'MDIA3F.SA', 'MDIA3.SA', 'CAML3F.SA', 'CAML3.SA', 'AGRO3F.SA', 'AGRO3.SA', 'BEEF3F.SA', 'BEEF3.SA', 'BEEF11.SA', 'VIVA3.SA', 'CRFB3F.SA', 'CRFB3.SA', 'PCAR3F.SA', 'PCAR4F.SA', 'PCAR4.SA', 'PCAR3.SA', 'NTCO3F.SA', 'NTCO3.SA', 'MRFG3F.SA', 'MRFG3.SA', 'JBSS3F.SA', 'JBSS3.SA', 'PGCO34.SA', 'BRFS3.SA', 'NDIV11.SA', 'CSUD3.SA', 'INBR31.SA', 'BIDI3.SA', 'BIDI11.SA', 'BIDI4.SA', 'STOC31.SA', 'NUBR33.SA', 'IGTI11.SA', 'IGTI3.SA', 'XPBR31.SA', 'TRAD3.SA', 'BSLI4F.SA', 'BSLI3F.SA', 'BSLI4.SA', 'BSLI3.SA', 'BTTL3F.SA', 'BTTL3.SA', 'BPAR3F.SA', 'BPAR3.SA', 'WFCO34F.SA', 'WFCO34.SA', 'VISA34F.SA', 'VISA34.SA', 'MSBR34F.SA', 'MSBR34.SA', 'MSCD34F.SA', 'MSCD34.SA', 'JPMC34F.SA', 'JPMC34.SA', 'HONB34F.SA', 'HONB34.SA', 'GEOO34F.SA', 'GEOO34.SA', 'GSGI34F.SA', 'GSGI34.SA', 'CTGP34F.SA', 'CTGP34.SA', 'BOAC34F.SA', 'BOAC34.SA', 'MMMC34F.SA', 'SCAR3F.SA', 'SCAR3.SA', 'LPSB3F.SA', 'LPSB3.SA', 'BMGB11.SA', 'BMGB4.SA', 'IGBR3F.SA', 'IGBR3.SA', 'GSHP3F.SA', 'GSHP3.SA', 'PSSA3F.SA', 'PSSA3.SA', 'CARD3F.SA', 'CARD3.SA', 'BBRK3F.SA', 'BBRK3.SA', 'BRPR3F.SA', 'BRPR3.SA', 'BRSR6F.SA', 'BRSR5F.SA', 'BRSR3F.SA', 'BRSR6.SA', 'BRSR5.SA', 'BRSR3.SA', 'SANB4F.SA', 'SANB3F.SA', 'SANB11F.SA', 'SANB4.SA', 'SANB3.SA', 'SANB11.SA', 'MULT3F.SA', 'MULT3.SA', 'ITUB3F.SA', 'ITUB4.SA', 'ITUB3.SA', 'ITUB4F.SA', 'ALSO3.SA', 'BMIN3.SA', 'MERC4.SA', 'LOGG3.SA', 'ITSA4F.SA', 'ITSA4.SA', 'ITSA3F.SA', 'IRBR3.SA', 'PDTC3.SA', 'SYNE3.SA', 'BBDC4F.SA', 'BBDC4.SA', 'BBDC3.SA', 'BRML3.SA', 'APER3F.SA', 'APER3.SA', 'BBSE3.SA', 'BPAN4.SA', 'BBAS3F.SA', 'BBAS3.SA', 'BBAS12.SA', 'BBAS11.SA', 'AXPB34.SA', 'LAND3.SA', 'DEXP4.SA', 'DEXP3.SA', 'RANI3F.SA', 'FCXO34F.SA', 'FCXO34.SA', 'PMAM3F.SA', 'PMAM3.SA', 'FESA4F.SA', 'FESA3F.SA', 'FESA4.SA', 'FESA3.SA', 'EUCA3F.SA', 'EUCA4.SA', 'EUCA3.SA', 'SUZB3F.SA', 'SUZB3.SA', 'KLBN4F.SA', 'KLBN3F.SA', 'KLBN11F.SA', 'KLBN4.SA', 'KLBN3.SA', 'KLBN11.SA', 'VALE5.SA', 'UNIP6F.SA', 'UNIP6.SA', 'UNIP5F.SA', 
    #                 'UNIP5.SA', 'UNIP3.SA', 'NEMO6.SA', 'NEMO5.SA', 'NEMO3.SA', 'MMXM3.SA', 'MMXM11.SA', 'GOAU4.SA', 'DXCO3.SA', 'CSNA3F.SA', 'CSNA3.SA', 'BRKM6.SA', 'BRKM5F.SA', 'BRKM5.SA', 'BRKM3.SA', 'BRAP4F.SA', 'BRAP4.SA', 'BRAP3F.SA', 'BRAP3.SA', 'ARMT34.SA', 'RBIV11.SA', 'CPLE11F.SA', 'CPLE11.SA', 'GTLG11.SA', 'PPLA11.SA', 'BTLT39.SA', 'BSHY39.SA', 'BSHV39.SA', 'BIEI39.SA', 'BIYT39.SA', 'BGOV39.SA', 'ALUG11.SA', 'WRLD11.SA', 'CXAG11.SA', 'ROOF11.SA', 'JGPX11.SA', 'PURB11.SA', 'BIME11.SA', 'JSAF11.SA', 'TELD11.SA', 'MORC11.SA', 'HUSI11.SA', 'CYCR11.SA', 'EQIR11.SA', 'CACR11.SA', 'RZAG11.SA', 'PORT3.SA', 'GETT11.SA', 'GETT4.SA', 'GETT3.SA', 'BIYE39.SA', 'BSCZ39.SA', 'BUSA39.SA', 'BERU39.SA', 'BSOX39.SA', 'BFCG39.SA', 'BFXH39.SA', 'BFTA39.SA', 'BKYY39.SA', 'BQTC39.SA', 'BFDN39.SA', 'BFDA39.SA', 'BFPI39.SA', 'BQQW39.SA', 'BFPX39.SA', 'BCIR39.SA', 'BFDL39.SA', 'BFBI39.SA', 'BOEF39.SA', 'BURT39.SA', 'BICL39.SA', 'BIXG39.SA', 'C2OI34.SA', 'S2TO34.SA', 'MILA.SA', 'CSMO.SA', 'YDRO11.SA', 'SPXB11.SA', 'SMAB11.SA', 'W2ST34.SA', 'S2QS34.SA', 'P2AT34.SA', 'G2DD34.SA', 'D2AS34.SA', 'C2PT34.SA', 'BIVW39.SA', 'BIVE39.SA', 'BCWV39.SA', 'A2VL34.SA', 'A2MC34.SA', 'AFHI11.SA', 'HSRE11.SA', 'VSEC11.SA', 'GRAO3.SA', 'USTK11.SA', 'AGXY3.SA', 'CRPG6.SA', 'CRPG5.SA', 'CRPG3.SA', 'SMFT3.SA', 'SOJA3.SA', 'Z2NG34.SA', 'T2TD34.SA', 'T2DH34.SA', 'S2UI34.SA', 'S2QU34.SA', 'S2NW34.SA', 'S2HO34.SA', 'C2ZR34.SA', 'U2ST34.SA', 'S2EA34.SA', 
    #                 'P2EN34.SA', 'M2PW34.SA', 'K2CG34.SA', 'D2KN34.SA', 'C2ON34.SA', 'C2HD34.SA', 'B2YN34.SA', 'ENMT4.SA', 'ENMT3.SA', 'SRNA3.SA', 'VBBR3.SA', 'RAIZ4.SA', 'RECV3.SA', 'SLBG34F.SA', 
    #                 'SLBG34.SA', 'HALI34F.SA', 'HALI34.SA', 'COPH34.SA', 'COPH34.SA', 'CHVX34F.SA', 'CHVX34.SA', 'PRIO3F.SA', 'PRIO3.SA', 'OSXB3F.SA', 'OSXB3.SA', 'DMMO11.SA', 'DMMO3F.SA', 'DMMO3.SA', 'RPMG3F.SA', 'RPMG3.SA', 'UGPA3.SA', 'UGPA3F.SA', 'PETR4F.SA', 'PETR4.SA', 'PETR3F.SA', 'PETR3.SA', 'EXXO34.SA', 'ENAT3.SA', 'ONCO3.SA', 'VVEO3.SA', 'PARD3.SA', 'BIOM3F.SA', 'BIOM3.SA', 'BALM3F.SA', 'BALM4F.SA', 'BALM4.SA', 'BALM3.SA', 'PFIZ34F.SA', 'PFIZ34.SA', 'MRCK34F.SA', 'MRCK34.SA', 'GBIO33F.SA', 'GBIO33.SA', 'PNVL3F.SA', 'PNVL3.SA', 'AALR3F.SA', 'AALR3.SA', 'ODPV3F.SA', 'ODPV3.SA', 'RADL3F.SA', 'RADL3.SA', 'QUAL3F.SA', 'QUAL3.SA', 'OFSA3.SA', 'JNJB34.SA', 'HYPE3.SA', 'FLRY3.SA', 'BMYB34.SA', 'ABTT34.SA', 'CLSA3.SA', 'LVTC3.SA', 'G2DI33.SA', 'IFCM3.SA', 'GOGL35.SA', 'LWSA3.SA', 'TOTS3F.SA', 'TOTS3.SA', 'XRXB34F.SA', 'XRXB34.SA', 'QCOM34F.SA', 'QCOM34.SA', 'ORCL34F.SA', 'ORCL34.SA', 'MSFT34F.SA', 'MSFT34.SA', 'IBMB34F.SA', 'IBMB34.SA', 'ITLC34F.SA', 'ITLC34.SA', 'HPQB34F.SA', 'HPQB34.SA', 'EBAY34F.SA', 'CSCO34F.SA', 'CSCO34.SA', 'ATTB34F.SA', 'AAPL34F.SA', 'AAPL34.SA', 'LINX3F.SA', 'LINX3.SA', 'POSI3F.SA', 'POSI3.SA', 'EBAY34.SA', 'BRIT3.SA', 'FIQE3.SA', 'DESK3.SA', 'VERZ34F.SA', 'VERZ34.SA', 'OIBR4F.SA', 'OIBR4.SA', 'OIBR.SA', 'TIMS3F.SA', 'TIMS3.SA', 'VIVT3F.SA', 'VIVT3.SA', 'TELB4F.SA', 'TELB4.SA', 'TELB3F.SA', 'TELB3.SA', 'ATTB34.SA', 'AURE3.SA', 'MEGA3.SA', 'CEPE6F.SA', 'CEPE5F.SA', 'CEPE3F.SA', 'CEPE6.SA', 'CEPE5.SA', 'CEPE3.SA', 'CEED3F.SA', 'CEED4F.SA', 'CEED4.SA', 'CEED3.SA', 'EEEL4F.SA', 'EEEL3F.SA', 'EEEL4.SA', 'EEEL3.SA', 'CASN4F.SA', 'CASN3F.SA', 'CASN4.SA', 'CASN3.SA', 'CEGR3F.SA', 'CEGR3.SA', 'CEBR3F.SA', 'CEBR6F.SA', 'CEBR5F.SA', 'CEBR6.SA', 'CEBR5.SA', 'CEBR3.SA', 'RNEW11F.SA', 'RNEW11F.SA', 'RNEW4F.SA', 'RNEW4.SA', 'RNEW3.SA', 'COCE6F.SA', 
    #                 'COCE5F.SA', 'COCE3F.SA', 'COCE6.SA', 'COCE5.SA', 'COCE3.SA', 'CLSC4F.SA', 'CLSC3F.SA', 'CLSC4.SA', 'CLSC3.SA', 'ALUP4F.SA', 'ALUP3F.SA', 'ALUP11F.SA', 'ALUP4.SA', 'ALUP3.SA', 'ALUP11.SA', 'SAPR11F.SA', 'SAPR4F.SA', 'SAPR3F.SA', 'SAPR4.SA', 'SAPR3.SA', 'SAPR11.SA', 'CPRE3F.SA', 'CPRE3.SA', 'CPLE5F.SA', 'CPLE6F.SA', 'CPLE6.SA', 'CPLE5.SA', 'CPLE3F.SA', 
    #                 'CPLE3.SA', 'CPFE3F.SA', 'CPFE3.SA', 'CGAS3F.SA', 'CGAS5F.SA', 'CGAS5.SA', 'CGAS3.SA', 'AESB3F.SA', 'AESB3.SA', 'NEOE3.SA', 'TRPL4F.SA', 'TRPL4.SA', 'TRPL3F.SA', 'TRPL3.SA', 'EGIE3.SA', 'TAEE4.SA', 'TAEE3.SA', 'TAEE11.SA', 'SBSP3F.SA', 'SBSP3.SA', 'RNEW11.SA', 'GEPA4.SA', 'GEPA3.SA', 'CESP6.SA',
    #                 'CESP5.SA', 'CESP3F.SA', 'CESP3.SA', 'CMIG4.SA', 'CMIG3F.SA', 'CMIG3.SA', 'AFLT3.SA','VALE3.SA']
                        

    # col1, col2 = st.columns(2)

    # rc = Risco()
    # with col1:
    #     st.subheader('VAR Metodo historico Equities')
    #     st.text('')
    #     st.text('')
    #     st.text('')
    #     data_inicial = st.date_input('Selecione a data inicial')
    #     data_final = st.date_input('Selecione o periodo final')
    #     try:
    #         if st.button('Rodar VAR Equities'):   
    #             var_historico = rc.var_historico(data_inicial,data_final)
    #     except:
    #         pass
    #     st.text('')
    #     st.text('')
    #     st.text('')
    #     st.text('')
    #     st.text('')
    #     st.subheader(' Simular VAR Metodo historico ')
    #     st.text('')
    #     data_inicial_var_simulacao = st.date_input('Selecione a data inicial',key='simulacao_var')
    #     data_final_var_simulacao = st.date_input('Selecione o periodo final',key='simulacao_var_data_final')
    #     lista_de_acoes_var = st.multiselect('Coloque os ativos para simulação:',options=lista_ativos_b3,key='Simulacao_var')
    #     lista_de_pesos_var = []
    #     try:
    #         for ativo in lista_de_acoes_var:
    #             peso = int(float(st.text_input(f'Coloque o peso para o {ativo}')))
    #             lista_de_pesos_var.append(peso)
    #     except:st.write('Preencha todos os campos de pesos')                

       
    #     if st.button('Rodar VAR'):   
    #         var_historico = rc.var_historico_simulacao(data_inicial_var_simulacao,data_final_var_simulacao,lista_de_acoes_var,lista_de_pesos_var)

    
    # with col2:


    #     st.subheader('Simulção Monte Carlo Equities')
    #     st.text('')
    #     st.text('')

    #     st.text('')
    #     dias_uteis = float(st.text_input('Coloque o número de dias úteis:', value=1))
    #     try:
    #         if st.button('Rodar Simulação Equities'):
    #             monte_carlo = rc.monte_carlo(int(dias_uteis))
    #         else:
    #             pass
    #     except:
    #         pass
    #     st.text('')
    #     st.text('')
    #     st.text('')
    #     st.text('')
    #     st.text('')
    #     st.text('')
    #     st.subheader('Simular Monte Carolo')
    #     st.text('')
    #     st.text('')
    #     st.text('')
    #     lista_de_acoes = st.multiselect('Coloque os ativos para simulação:',options=lista_ativos_b3)
    #     lista_de_pesos = []
    #     try:
    #         for ativo in lista_de_acoes:
    #             peso = int(st.text_input(f'Coloque o peso para o {ativo}'))
    #             lista_de_pesos.append(peso)    
    #     except:st.write('Preencha todos os campos de pesos')
            
    #     dias_uteis_nova_simulacao = int(float(st.text_input('Coloque o número de dias úteis:', value=125)))

    #     if st.button('Rodar Simulação'):
    #         monte_carlo_nova_carteira = rc.nova_carteira_monte_carlo(lista_de_acoes, dias_uteis_nova_simulacao, lista_de_pesos)





