import pickle
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

def obter_month_number(month):
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
def obter_month_name(month):
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
def subtrair_mes(month, sub):
        if month <= sub:
            return (12-(sub-month))
        else:
            return (month-sub)
def obter_fator_sazonal(month):
    mes = obter_month_number(month)
    sazonal = pd.read_csv('Dados/df_final.csv')
    sazonal = sazonal[['data', 'seasonal']]
    sazonal['data'] = pd.to_datetime(sazonal['data'])
    sazonal['mes'] = sazonal['data'].dt.month
    filtered_df = sazonal.loc[sazonal['mes']== mes]
    filtered_df.drop_duplicates(subset='mes', keep='last', inplace=True)
    return filtered_df['seasonal'].values[0]
def obter_features(month, usp, sao_carlos, vendas_lag8):
    sazonal = obter_fator_sazonal(month)
    json = {
        'vendas_USP_LAG_5': usp,
        'vendas_Sao_Carlos_LAG_5': sao_carlos,
        'vendas_LAG_8': vendas_lag8,
        'seasonal_LAG_12': sazonal
    }
    df = pd.DataFrame([json])
    ordem = ['vendas_USP_LAG_5', 'vendas_Sao_Carlos_LAG_5', 'vendas_LAG_8', 'seasonal_LAG_12']
    df = df[ordem]
    return df

modelo = pickle.load(open('Modelos/pipeline.pkl', 'rb'))
erro_modelo = 0.2964

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
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        mes = st.selectbox(
            'Mês da Previsão', 
            ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])
    with col2:
        month_5 = obter_month_name(subtrair_mes(obter_month_number(mes),5))
        sao_carlos = st.slider(
            f'Vendas São Carlos - {month_5} (M-5)', 
            0, 
            200)
    with col3:
        vendas_usp = st.slider(
            f'Vendas USP - {month_5} (M-5)', 
            0, 
            500)
    with col4:
        month_8 = obter_month_name(subtrair_mes(obter_month_number(mes),8))
        vendas_lag8 = st.number_input(f'Vendas Totais - {month_8} (M-8)', min_value=0, format='%i')

    if st.button('Gerar previsão'):
        col1, col2, col3 = st.columns(3)
        with col2:
            df = obter_features(mes, vendas_usp, sao_carlos, vendas_lag8)
            predicao = modelo.predict(df)
            predicao_md_text = f'''
            <p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 20px; line-height: 20px; text-align: center;"><b>Previsão de vendas</b></p>
            <p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 80px; color: #383535; line-height: 55px; text-align: center;">{str(int(round(predicao[0],0)))}</p>
            <p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 15px; color: Gray; line-height: 15px; text-align: center;">+/- {str(int(round(predicao[0]*erro_modelo,0)))}</p>
            '''
            st.markdown(
                predicao_md_text, 
                unsafe_allow_html=True)
else:
    st.markdown('---')
    with st.expander('Caso não possua o template em CSV, baixe-o aqui'):
        with open('Dados/exemplo.xlsx', 'rb') as file:
            btn = st.download_button(
                label='Baixar',
                data=file,
                file_name='exemplo.xlsx'
                )
            md_text = '''<p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 15px;"><b>Dados necessários:</b><br>
            <ul>
            <li><u>Mês desejado</u> - Meses que você deseja prever (Ex: Janeiro, Feveiro, etc)</li>
            <li><u>Vendas São Carlos Cinco Meses Antes</u> - Vendas na cidade de São Carlos cinco meses antes (M-5) ao que se deseja prever</li>
            <li><u>Vendas USP Cinco Meses Antes</u> - Vendas na USP cinco meses antes (M-5) ao que se deseja prever</li>
            <li><u>Vendas Total Seis Meses Antes</u> - Vendas total (em todas as cidades) seis meses antes (M-6) ao que se deseja prever</li>
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
        df['seasonal_LAG_12'] = df['mes_desejado'].apply(obter_fator_sazonal)
        
        df.rename(columns={
            'mes_desejado': 'Mês',
            'vendas_usp_cinco_meses_antes': 'vendas_USP_LAG_5',
            'vendas_sao_carlos_cinco_meses_antes': 'vendas_Sao_Carlos_LAG_5',
            'vendas_total_oito_meses_antes': 'vendas_LAG_8'
        }, inplace=True)
        
        ordem = ['vendas_USP_LAG_5', 'vendas_Sao_Carlos_LAG_5', 'vendas_LAG_8', 'seasonal_LAG_12']
        
        X = df[ordem]
        X.fillna(0, inplace=True)
        pred = modelo.predict(X)
        df = df[['Mês']]
        df['Vendas'] = pred
        df['Min'] = pred*(1-erro_modelo)
        df['Max'] = pred*(1+erro_modelo)
        df['Vendas'] = round(df['Vendas'],0).astype('int')
        df['Min'] = round(df['Min'],0).astype('int')
        df['Max'] = round(df['Max'],0).astype('int')
        ordem = ['Mês', 'Min', 'Vendas', 'Max']
        df = df[ordem]
        df.to_excel('Previsoes/pred.xlsx', index=None)
        with open('Previsoes/pred.xlsx',  'rb') as previsao:
            botao_download = st.download_button(
                label='Baixar Previsões',
                data=previsao,
                file_name='previsoes.xlsx'
            )
        fig = go.Figure(data=[
            go.Scatter(x=df['Mês'], y=df['Min'], marker={'color': 'gray'}, name='Mínimo'),
            go.Scatter(x=df['Mês'], y=df['Vendas'], marker={'color': 'blue'}, name='Previsão'),
            go.Scatter(x=df['Mês'], y=df['Max'], marker={'color': 'gray'}, name='Máximo')
            ])
        fig.update_layout(font=dict(color='black'), title_text='Gráfico da Previsão')
        st.plotly_chart(fig, use_container_width=True)