import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf

class Var():
    def __init__(self):

        print('hello world')

    # def  var_historioco(acao,alpha = 0.05,periodo = 'D'):
    #     dados_acao = yf.download(acao)['Adj Close']

    #     if periodo == "M":

    #         retorno_da_acao = dados_acao.resample('M').last().pct_change().dropna()
    #     else:
    #         retorno_da_acao = dados_acao.pct_change().dropna()


    #     retornos_ordenados = np.sort(retorno_da_acao.values)

    #     posicao_do_retorno_alpha = int(alpha* len(retornos_ordenados))

    #     retorno_var = retornos_ordenados[posicao_do_retorno_alpha]

    #     return retorno_var


# if __name__=='__main__':

#     var = Var()
#     dados = var.var_historioco('WEGE3.SA')*100
#     print(f'O var e {dados}')




def  var_historioco(acao,alpha = 0.05,periodo = 'D'):
    dados_acao = yf.download(acao)['Adj Close']

    if periodo == "M":

        retorno_da_acao = dados_acao.resample('M').last().pct_change().dropna()
    else:
        retorno_da_acao = dados_acao.pct_change().dropna()

    print(dados_acao)

    retornos_ordenados = np.sort(retorno_da_acao.values)

    posicao_do_retorno_alpha = int(alpha* len(retornos_ordenados))

    retorno_var = retornos_ordenados[posicao_do_retorno_alpha]

    return retorno_var


var = var_historioco('WEGE3.SA')*100
print(var)
