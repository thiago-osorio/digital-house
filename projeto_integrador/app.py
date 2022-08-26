import pickle
import streamlit as st
import pandas as pd
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

def get_month_number(month):
    if month == 'Janeiro':
        return 1
    elif month == 'Fevereiro':
        return 2
    elif month == 'Março':
        return 3
    elif month == 'Abril':
        return 4
    elif month == 'Maio':
        return 5
    elif month == 'Junho':
        return 6
    elif month == 'Julho':
        return 7
    elif month == 'Agosto':
        return 8
    elif month == 'Setembro':
        return 9
    elif month == 'Outubro':
        return 10
    elif month == 'Novembro':
        return 11
    elif month == 'Dezembro':
        return 12
def get_month_name(month):
    if month == 1:
        return 'Janeiro'
    elif month == 2:
        return 'Fevereiro'
    elif month == 3:
        return 'Março'
    elif month == 4:
        return 'Abril'
    elif month == 5:
        return 'Maio'
    elif month == 6:
        return 'Junho'
    elif month == 7:
        return 'Julho'
    elif month == 8:
        return 'Agosto'
    elif month == 9:
        return 'Setembro'
    elif month == 10:
        return 'Outubro'
    elif month == 11:
        return 'Novembro'
    elif month == 12:
        return 'Dezembro'
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
    if month == 'Fevereiro':
        fevereiro = 1
        maio = 0
        dezembro = 0
    elif month == 'Maio':
        fevereiro = 0
        maio = 1
        dezembro = 0
    elif month == 'Dezembro':
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
    ordem = ['vendas_Porto_Alegre_LAG_1', 'vendas_LAG_6', 'seasonal_LAG_12', 'mes_December', 'mes_February', 'mes_May']
    df = df[ordem]
    return df

modelo = pickle.load(open('Modelos/pipeline.pkl', 'rb'))
erro_modelo = 0.1738

st.set_page_config(page_title='Previsão Demanda', layout="wide", page_icon=":chart:")

st.image(Image.open('cover.png'))
st.title('Previsão da Demanda de Vendas')

choice = st.radio('Escolha qual previsão deseja realizar', ['Previsão de um único mês', 'Previsão de vários meses'])

if choice == 'Previsão de um único mês':
    st.markdown('---')
    st.header('Previsão Única de Venda')
    st.markdown(' ')
    col1, col2, col3 = st.columns(3)
    with col1:
        mes = st.selectbox('Mês da Previsão', ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])
        
    with col2:
        month_1 = get_month_name(month_sub(get_month_number(mes),1))
        porto_alegre = st.slider(f'Vendas Porto Alegre - {month_1} (M-1)', 0, 500)
    with col3:
        month_6 = get_month_name(month_sub(get_month_number(mes),6))
        vendas_lag6 = st.slider(f'Vendas Totais - {month_6} (M-6)', 0, 15000, step=1)


    if st.button('Gerar previsão'):
        col1, col2, col3 = st.columns(3)
        with col2:
            df = get_features(mes, porto_alegre, vendas_lag6)
            st.dataframe(df)
            predicao = modelo.predict(df)
            predicao_md_text = f'''
            <p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 20px; line-height: 20px; text-align: center;"><b>Previsão de vendas</b></p>
            <p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 80px; color: #383535; line-height: 55px; text-align: center;">{str(int(round(predicao[0],0)))}</p>
            <p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 15px; color: Gray; line-height: 15px; text-align: center;">+/- {str(int(round(predicao[0]*erro_modelo,0)))}</p>
            '''
            st.markdown(predicao_md_text, unsafe_allow_html=True)
else:
    st.markdown('---')
    #st.error('Em desenvolvimento')
    st.caption('Por favor, baixe o arquivo csv e coloque as informações necessárias para a previsão')
    with open('Dados/exemplo.csv', 'rb') as file:
        btn = st.download_button(
            label='Baixar',
            data=file,
            file_name='exemplo.csv'
            )