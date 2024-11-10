import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import time

#função para fazer o download do arquivo

@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

#mensagem de sucesso
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()

st.title('Dados Brutos :shopping_trolley:')
# Lê o arquivo JSON
try:
    with open("produto.json", "r", encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("Arquivo JSON não encontrado. Certifique-se de que o arquivo esteja no mesmo diretório do seu script ou forneça o caminho completo.")
    st.stop()  # Interrompe a execução do aplicativo se o arquivo não for encontrado
except json.JSONDecodeError:
    st.error("Erro ao decodificar o JSON. Verifique se o arquivo JSON é válido.")
    st.stop()

# Converte o JSON para DataFrame do Pandas
df = pd.DataFrame(data)
df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(df.columns), list(df.columns))

#criação dos filtros
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', df['Produto'].unique(), df['Produto'].unique())
with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione as categorias', df['Categoria do Produto'].unique(), df['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Frete', 0,250, (0,250))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (df['Data da Compra'].min(), df['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', df['Vendedor'].unique(), df['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra', df['Local da compra'].unique(), df['Local da compra'].unique())
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',df['Tipo de pagamento'].unique(), df['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

#filtragem
query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

dados_filtrados = df.query(query)
dados_filtrados = dados_filtrados[colunas]

# Exibe o DataFrame como uma tabela no Streamlit
st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

#extraindo o arquivo
st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
