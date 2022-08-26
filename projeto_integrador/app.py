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
def obter_features(month, porto_alegre, vendas_lag6):
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
    sazonal = obter_fator_sazonal(month)
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
def obter_mes(coluna, month):
    if coluna.upper() == month.upper():
        return 1
    else:
        return 0

modelo = pickle.load(open('Modelos/pipeline.pkl', 'rb'))
erro_modelo = 0.1738

st.set_page_config(
    page_title='Previsão Demanda', 
    layout="wide", 
    page_icon=":chart:")

st.image(Image.open('cover.png'))
st.title('Previsão da Demanda de Vendas')

modo = st.radio(
    'Escolha qual previsão deseja realizar', 
    ['Previsão de um único mês', 'Previsão de vários meses'])

if modo == 'Previsão de um único mês':
    st.markdown('---')
    st.header('Previsão Única de Venda')
    st.markdown(' ')
    col1, col2, col3 = st.columns(3)
    with col1:
        mes = st.selectbox(
            'Mês da Previsão', 
            ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'])
    with col2:
        month_1 = obter_month_name(subtrair_mes(obter_month_number(mes),1))
        porto_alegre = st.slider(
            f'Vendas Porto Alegre - {month_1} (M-1)', 
            0, 
            500)
    with col3:
        month_6 = obter_month_name(subtrair_mes(obter_month_number(mes),6))
        vendas_lag6 = st.slider(
            f'Vendas Totais - {month_6} (M-6)', 
            0, 
            15000, 
            step=1)

    if st.button('Gerar previsão'):
        col1, col2, col3 = st.columns(3)
        with col2:
            df = obter_features(mes, porto_alegre, vendas_lag6)
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
        with open('Dados/exemplo.csv', 'rb') as file:
            btn = st.download_button(
                label='Baixar',
                data=file,
                file_name='exemplo.csv'
                )
            md_text = '''<p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 15px;"><b>Dados necessários:</b><br>
            <ul>
            <li><u>Mês desejado</u> - Meses que você deseja prever (Ex: Janeiro, Feveiro, etc)</li>
            <li><u>Vendas Porto Alegre Mês Anterior</u> - Vendas na cidade de Porto Alegre no mês anterior (M-1) ao que se deseja prever</li>
            <li><u>Vendas Total Seis Meses Antes</u> - Vendas total (em todas as cidades) seis meses antes (M-6) ao que se deseja prever</li>
            </ul>
            </p>'''
            
            st.markdown(
                md_text, 
                unsafe_allow_html=True)
    
    # md_text = '<p style="https://fonts.googleapis.com/css?family=Source+Sans+Pro; font-size: 20px;">Agora é hora de gerar as previsões</p>'
    # st.markdown(
    #     md_text, 
    #     unsafe_allow_html=True)
    
    data = st.file_uploader(
        label='Carregue o arquivo CSV com os dados preenchidos',
        type='csv'
    )

    if data is not None:
        df = pd.read_csv(data, sep=';', encoding='utf8')
        df['mes_February'] = df['mes_desejado'].map(lambda x: obter_mes(x, 'fevereiro'))
        df['mes_May'] = df['mes_desejado'].map(lambda x: obter_mes(x, 'maio'))
        df['mes_December'] = df['mes_desejado'].map(lambda x: obter_mes(x, 'dezembro'))
        df['seasonal_LAG_12'] = df['mes_desejado'].apply(obter_fator_sazonal)
        
        #df_download = df[['mes_desejado']].copy()
        #df_download.rename(columns={'mes_desejado':'Mês'}, inplace=True)
        
        #df.drop('mes_desejado', axis=1, inplace=True)
        df.rename(columns={
            'mes_desejado': 'Mês',
            'vendas_porto_alegre_mes_anterior': 'vendas_Porto_Alegre_LAG_1',
            'vendas_total_seis_meses_antes': 'vendas_LAG_6'
        }, inplace=True)
        
        ordem = ['vendas_Porto_Alegre_LAG_1', 'vendas_LAG_6', 'seasonal_LAG_12', 'mes_December', 'mes_February', 'mes_May']
        #df = df[ordem]
        
        X = df[ordem]
        X.fillna(0, inplace=True)
        pred = modelo.predict(X)
        df = df[['Mês']]
        df['Vendas'] = pred
        df['Vendas'] = round(df['Vendas'],0).astype('int')
        df.to_excel('Previsoes/pred.xlsx', index=None)
        with open('Previsoes/pred.xlsx',  'rb') as previsao:
            botao_download = st.download_button(
                label='Baixar Previsões',
                data=previsao,
                file_name='previsoes.xlsx'
            )
        fig = go.Figure(data=go.Scatter(x=df['Mês'], y=df['Vendas'], marker={'color': 'gray'}))
        fig.update_layout(font=dict(color='black'), title_text='Gráfico da Previsão')
        st.plotly_chart(fig, use_container_width=True)