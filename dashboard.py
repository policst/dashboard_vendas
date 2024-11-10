import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json


st.set_page_config(layout = 'wide')

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('Dashboard de Vendas :shopping_bags:')

# Lê o arquivo JSON
try:
    with open("produto.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

        st.sidebar.title('Filtros')
        regiao = st.sidebar.selectbox('Região', regioes)

        if regiao == 'Brasil':
         regiao = ''

        todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
        if todos_anos:
             ano = ''
        else:
            ano = st.sidebar.slider('Ano', 2020, 2023)
        

except FileNotFoundError:
    st.error("Arquivo JSON não encontrado. Certifique-se de que o arquivo esteja no mesmo diretório do seu script ou forneça o caminho completo.")
    st.stop()  # Interrompe a execução do aplicativo se o arquivo não for encontrado
except json.JSONDecodeError:
    st.error("Erro ao decodificar o JSON. Verifique se o arquivo JSON é válido.")
    st.stop()


# Converte o JSON para DataFrame do Pandas
df = pd.DataFrame(data)
df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format = '%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', df['Vendedor'].unique())
if filtro_vendedores:
    dados = df[df['Vendedor'].isin(filtro_vendedores)]

##tabelas utilizadas para os gráficos
receita_estados = df.groupby('Local da compra')[['Preço']].sum()
receita_estados = df.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False) #remove linhas duplicadas (estados e siglas)

receita_mensal = df.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = df.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

##tabelas de quantidade de vendas
##tabelas de vendedores
### Tabelas vendedores 
vendedores = pd.DataFrame(df.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

## MOntagem do Gráficos de mapa
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america', #grafico mapa mundi do mundo inteiro - filtro por area do mapa
                                  size = 'Preço', #tamanho com base na receita de cada estado
                                  template = 'seaborn', #formato visual do grafico
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat':False, 'lon':False}, #remove legenga
                                  title = 'Receita por Estado'
                                  )

fig_receita_mensal = px.line(receita_mensal,
                                                     x = 'Mês',
                                                     y = 'Preço',
                                                     markers = True,
                                                     range_y = (0, receita_mensal.max()),
                                                       color='Ano',
                                                        line_dash = 'Ano',
                                                        title = 'Receita mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita')

fig_receita_estados = px.bar(receita_estados.head(), #.head mostra somente os 5 primeiros
                                            x = 'Local da compra',
                                            y = 'Preço',
                                            text_auto = True,
                                            title = 'Top estados(receita)')

fig_receita_estados.update_layout(yaxis_title = 'Receita')
fig_receita_categorias = px.bar(receita_categorias,
                                                                text_auto = True,
                                                                title = 'Receita por categoria')

fig_receita_estados.update_layout(yaxis_title = 'Receita')

##Visualização no streamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita',formata_numero(df['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita,use_container_width = True)
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(df.shape[0]))
        st.plotly_chart(fig_receita_mensal,use_container_width = True)
        st.plotly_chart(fig_receita_categorias, use_container_width = True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita',formata_numero(df['Preço'].sum(), 'R$'))
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(df.shape[0]))

with aba3:
    with aba3:
        qtd_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita',formata_numero(df['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values(['sum'], ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(df.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x='count',
                                        y=vendedores[['count']].sort_values(['count'], ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (quantidade de vendas)')
        st.plotly_chart(fig_vendas_vendedores)
# Exibe o DataFrame como uma tabela no Streamlit
##st.dataframe(df)