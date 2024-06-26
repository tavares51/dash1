import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import plotly.express as px
from streamlit_dynamic_filters import DynamicFilters

st.set_page_config(layout="wide", page_title="Vendas")
vendedores = {1: 'João', 2: 'Maria', 3: 'Pedro', 4: 'Ana', 5: 'Carlos'}
# valores considerando a uma Saca (60kg)
produtos = [
    {'ProdutoId':1, 'Produto':'Soja', 'Valor': 136.42},
    {'ProdutoId':2, 'Produto':'Milho', 'Valor': 57.71},
    {'ProdutoId':3, 'Produto':'Sorgo', 'Valor': 38.00}
    ]
regioes = {1:'Norte', 2:'Sul', 3:'Leste', 4:'Oeste', 5:'Centro'}
     
vendedores_df = pd.DataFrame(list(vendedores.items()), columns=['VendedorId', 'Vendedor'])
produtos_df = pd.DataFrame(produtos)
regioes_df = pd.DataFrame(list(regioes.items()), columns=['RegiaoId', 'Regiao'])

clientes = list()
for i in range(1,16):
    clientes.append({'ClienteId':i, 'Cliente':f'Cliente {i}', 'VendedorId':(i % 5) + 1})
clientes_df = pd.DataFrame(clientes)

SEED = 42
random.seed(SEED)
meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
data_inicial = datetime(2023, 1, 1)
data_final = datetime(2023, 12, 31)
quantidades = list(range(50, 200))
num_registros = 200

vendas = []
for _ in range(num_registros):
    data_venda = data_inicial + timedelta(days=random.randint(0, (data_final - data_inicial).days))
    cliente_id = random.randint(clientes_df.ClienteId.min(), clientes_df.ClienteId.max())
    vendedor_id = clientes_df.loc[clientes_df['ClienteId'] == cliente_id, 'VendedorId'].values[0]
    produto_id = random.choice([1, 2, 3])
    regiao_id = random.randint(1, 5)
    quantidade = random.choice(quantidades)
    vendas.append([cliente_id, vendedor_id, produto_id, data_venda, regiao_id, quantidade])

colunas = ["ClienteId", "VendedorId", "ProdutoId", "DataVenda", "RegiaoId", "Quantidade"]
df_vendas = pd.DataFrame(vendas, columns=colunas)

df_vendas = df_vendas.merge(vendedores_df, on="VendedorId")
df_vendas = df_vendas.merge(regioes_df, on="RegiaoId")
df_vendas = df_vendas.merge(produtos_df, on="ProdutoId")
df_vendas = df_vendas.merge(clientes_df, on="ClienteId")

df_vendas['Valor_Total'] = df_vendas['Quantidade'] * df_vendas['Valor']
df_vendas['Valor_Total'] = df_vendas['Valor_Total'].round(2)

df_final = df_vendas[['Produto','Valor','Quantidade','Valor_Total','DataVenda','Vendedor','Regiao','Cliente']]

df_final['mes'] = df_final['DataVenda'].dt.month
df_final['ano'] = df_final['DataVenda'].dt.year

#mes_filtro = st.sidebar.selectbox("Mês", sorted(df_final["mes"].unique()))
#ano_filtro = st.sidebar.selectbox("Ano", sorted(df_final["ano"].unique()))
dynamic_filters = DynamicFilters(df_final, filters=['Produto', 'Vendedor', 'Regiao', 'Cliente', 'mes', 'ano'])
dynamic_filters.display_filters(location='sidebar', num_columns=1, gap='large')
df_vendas_filtrado = dynamic_filters.filter_df()

#df_vendas_mes_filtrado = df_vendas_filtrado[df_vendas_filtrado['mes'] == mes_filtro]
#df_vendas_mes_filtrado = df_vendas_mes_filtrado[df_vendas_mes_filtrado['ano'] == ano_filtro]

#st.title(f'Mês: {meses[mes_filtro-1]}')

col_1, col_2 = st.columns(2)

df_clientes_por_faturamento  = df_vendas_filtrado.groupby(['Cliente'],as_index=False)['Valor_Total'].sum()
df_clientes_por_faturamento.sort_values(by = 'Valor_Total', ascending=False, inplace = True)

ax1 = px.bar(
    df_clientes_por_faturamento
    , x='Cliente'
    , y = 'Valor_Total'
    , color = 'Cliente'
    , title = 'Faturamento'
    , template='plotly_dark'
    , color_discrete_sequence=['#1f77b4', '#ffffff', '#2ca02c', '#d62728', '#9467bd']
    , width=1500
    , height=500
    , text_auto=True
    , opacity=0.7
)
#col_1.plotly_chart(ax1)

df_clientes_por_quantidade  = df_vendas_filtrado.groupby(['Cliente'],as_index=False)['Quantidade'].sum()
#df_clientes_por_quantidade
df_clientes_por_quantidade.sort_values(by = 'Quantidade', ascending=False, inplace = True)

ax2 = px.bar(
    df_clientes_por_quantidade
    , x='Cliente'
    , y = 'Quantidade'
    , color = 'Cliente'
    , title = 'Quantidade de Vendas - Considerando a uma Saca (60kg)'
    , template='plotly_dark'
    , color_discrete_sequence=['#1f77b4', '#ffffff', '#2ca02c', '#d62728', '#9467bd']
    , width=1500
    , height=500
    , text_auto=True
    , opacity=0.7
)
#
st.plotly_chart(ax1)
st.plotly_chart(ax2)