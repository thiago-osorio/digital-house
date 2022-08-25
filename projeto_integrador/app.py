import pickle
import streamlit as st
import pandas as pd

def get_month_number(month):
    if month == 'Jan':
        return 1
    elif month == 'Fev':
        return 2
    elif month == 'Mar':
        return 3
    elif month == 'Abr':
        return 4
    elif month == 'Mai':
        return 5
    elif month == 'Jun':
        return 6
    elif month == 'Jul':
        return 7
    elif month == 'Ago':
        return 8
    elif month == 'Set':
        return 9
    elif month == 'Out':
        return 10
    elif month == 'Nov':
        return 11
    elif month == 'Dez':
        return 12
def get_month_name(month):
    if month == 1:
        return 'janeiro'
    elif month == 2:
        return 'fevereiro'
    elif month == 3:
        return 'março'
    elif month == 4:
        return 'abril'
    elif month == 5:
        return 'maio'
    elif month == 6:
        return 'junho'
    elif month == 7:
        return 'julho'
    elif month == 8:
        return 'agosto'
    elif month == 9:
        return 'setembro'
    elif month == 10:
        return 'outubro'
    elif month == 11:
        return 'novembro'
    elif month == 12:
        return 'dezembro'
def month_sub(month, sub):
        if month <= sub:
            return (12-(sub-month))
        else:
            return (month-sub)
def get_fator_sazonal(month):
    mes = get_month_number(month)
    sazonal = pd.read_csv('Dados/df_final.csv')
    sazonal = sazonal[['data', 'seasonal']]
    sazonal['data'] = pd.to_datetime(sazonal['data'])
    sazonal['mes'] = sazonal['data'].dt.month
    filtered_df = sazonal.loc[sazonal['mes']== mes]
    filtered_df.drop_duplicates(subset='mes', keep='last', inplace=True)
    return filtered_df['seasonal'].values[0]
def get_features(month, porto_alegre, vendas_lag6):
    if month == 'Fev':
        fevereiro = 1
        maio = 0
        dezembro = 0
    elif month == 'Mai':
        fevereiro = 0
        maio = 1
        dezembro = 0
    elif month == 'Dez':
        fevereiro = 0
        maio = 0
        dezembro = 1
    else:
        fevereiro = 0
        maio = 0
        dezembro = 0
    sazonal = get_fator_sazonal(month)
    json = {
        'mes_February': fevereiro,
        'mes_May': maio,
        'mes_December': dezembro,
        'vendas_Porto_Alegre_LAG_1': porto_alegre,
        'vendas_LAG_6': vendas_lag6,
        'seasonal_LAG_12': sazonal
    }
    df = pd.DataFrame([json])
    return df

modelo = pickle.load(open('Modelos/pipeline.pkl', 'rb'))
st.set_page_config(page_title='Previsão Demanda', layout="wide", page_icon=":chart:")

st.title('Previsão da Demanda de Vendas')

mes = st.selectbox('Mês da Previsão', ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])

month_1 = get_month_name(month_sub(get_month_number(mes),1))
porto_alegre = st.slider(f'Vendas em Porto Alegre no mês de {month_1} (M-1)', 0, 500)

month_6 = get_month_name(month_sub(get_month_number(mes),6))
vendas_lag6 = st.slider(f'Vendas totais no mês de {month_6} (M-6)', 0, 15000)

df = get_features(mes, porto_alegre, vendas_lag6)

predicao = modelo.predict(df)
st.metric('Predição', predicao)