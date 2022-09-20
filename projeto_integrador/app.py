import pickle
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

def obter_month_number(month):
    if month == 'Janeiro':
        return '01'
    elif month == 'Fevereiro':
        return '02'
    elif month == 'Março':
        return '03'
    elif month == 'Abril':
        return '04'
    elif month == 'Maio':
        return '05'
    elif month == 'Junho':
        return '06'
    elif month == 'Julho':
        return '07'
    elif month == 'Agosto':
        return '08'
    elif month == 'Setembro':
        return '09'
    elif month == 'Outubro':
        return '10'
    elif month == 'Novembro':
        return '11'
    elif month == 'Dezembro':
        return '12'
def subtrair_mes(month, sub):
        if month <= sub:
            return (12-(sub-month))
        else:
            return (month-sub)
def obter_features(month, year):
    mes = obter_month_number(month)
    data = f'{year}-{mes}-01'
    json = {
        'ds': data
    }
    df = pd.DataFrame([json])
    return df

modelo = pickle.load(open('Modelos/prophet.pkl', 'rb'))

st.set_page_config(
    page_title='Previsão Demanda', 
    layout="wide", 
    page_icon=":chart:")

st.image(Image.open('cover.png'))
st.title('Previsão de Vendas')

modo = st.radio(
    'Escolha o tipo de previsão que deseja realizar', 
    ['Previsão de um único mês', 'Previsão de vários meses'])

if modo == 'Previsão de um único mês':
    st.markdown('---')
    st.header('Previsão Única de Venda')
    st.markdown(' ')
    col1, col2 = st.columns(2)
    with col1:
        mes = st.selectbox(
            'Mês da Previsão', 
            ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])
    with col2:
        ano = st.selectbox(
            'Ano da Previsão', 
            ['2018', '2019', '2020', '2021', '2022', '2023', '2024'])

    if st.button('Gerar previsão'):
        col1, col2, col3 = st.columns(3)
        with col2:
            df = obter_features(mes, ano)
            predicao = modelo.predict(df)
            predicao_md_text = f'''
            <p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 20px; line-height: 20px; text-align: center;"><b>Previsão de vendas</b></p>
            <p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 80px; color: #383535; line-height: 55px; text-align: center;">{str(int(round(predicao['yhat'],0)))}</p>
            <p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 15px; color: Gray; line-height: 15px; text-align: center;">+/- {str(int(round((predicao['yhat_upper']-predicao['yhat_lower'])/2,0)))}</p>
            '''
            st.markdown(
                predicao_md_text, 
                unsafe_allow_html=True)
else:
    st.markdown('---')
    with st.expander('Caso não possua o template em Excel, baixe-o aqui'):
        with open('Dados/exemplo.xlsx', 'rb') as file:
            btn = st.download_button(
                label='Baixar',
                data=file,
                file_name='exemplo.xlsx'
                )
            md_text = '''<p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 15px;"><b>Dados necessários:</b><br>
            <ul>
            <li><b><u>Data</u></b> - Data no formato YYYY-MM-01 (Ex: 2022-12-01). <font color= Red><u>OBS:</u></font> São realizadas somente previsões mensais</li>
            </ul>
            </p>'''
            st.markdown(
                md_text, 
                unsafe_allow_html=True)
    
    data = st.file_uploader(
        label='Carregue o arquivo Excel com os dados preenchidos',
        type='xlsx'
    )

    if data is not None:
        df = pd.read_excel(data)
        df.rename(columns={'data (YYYY-MM-01)': 'ds'}, inplace=True)
        
        pred = modelo.predict(df)
        df['Vendas'] = pred['yhat']
        df['Min'] = pred['yhat_lower']
        df['Max'] = pred['yhat_upper']
        df['Vendas'] = round(df['Vendas'],0).astype('int')
        df['Min'] = round(df['Min'],0).astype('int')
        df['Max'] = round(df['Max'],0).astype('int')
        df.rename(columns={'ds': 'Data'}, inplace=True)
        ordem = ['Data', 'Min', 'Vendas', 'Max']
        df = df[ordem]
        df.to_excel('Previsoes/pred.xlsx', index=None)
        with open('Previsoes/pred.xlsx',  'rb') as previsao:
            botao_download = st.download_button(
                label='Baixar Previsões',
                data=previsao,
                file_name='previsoes.xlsx'
                )
        fig = go.Figure(data=[
            go.Scatter(x=df['Data'], y=df['Min'], marker={'color': 'gray'}, name='Mínimo'),
            go.Scatter(x=df['Data'], y=df['Vendas'], marker={'color': 'blue'}, name='Previsão'),
            go.Scatter(x=df['Data'], y=df['Max'], marker={'color': 'gray'}, name='Máximo')
            ])
        fig.update_layout(font=dict(color='black'), title_text='Gráfico da Previsão')
        st.plotly_chart(fig, use_container_width=True)