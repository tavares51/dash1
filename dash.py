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
dynamic_filters = DynamicFilters(df_final, filters=['Produto', 'Vendedor', 'Regiao', 'mes', 'ano'])
dynamic_filters.display_filters(location='sidebar', num_columns=1, gap='large')
df_vendas_filtrado = dynamic_filters.filter_df()

#df_vendas_mes_filtrado = df_vendas_filtrado[df_vendas_filtrado['mes'] == mes_filtro]
#df_vendas_mes_filtrado = df_vendas_mes_filtrado[df_vendas_mes_filtrado['ano'] == ano_filtro]

st.title(f'Visão Geral')

col_1, col_2, col_3 = st.columns(3)

df_regiao_clientes = df_vendas_filtrado.groupby('Regiao')['Cliente'].value_counts().reset_index(name='QuantidadeClientes')
quantidade_cliente_regiao = df_regiao_clientes.Regiao.value_counts()
ax1 = px.bar(
    x=quantidade_cliente_regiao.values
    , y=quantidade_cliente_regiao.index
    , title='Clientes'
    , labels={'x':'Região', 'y':'Quantidade de Clientes'}
    , color=quantidade_cliente_regiao.index
    , color_discrete_sequence=['#1f77b4', '#ffffff', '#2ca02c', '#d62728', '#9467bd']
    , width=500
    , height=300
    , template='plotly_dark'
    , text_auto=True
)
ax1.update_layout(title_x=0.5)

col_1.plotly_chart(ax1)

df_vendas_mes = df_vendas_filtrado.copy()
df_vendas_mes = df_vendas_mes.groupby(['Vendedor'], as_index=False)['Valor_Total'].sum()
meta_vendas = 100000
#df_vendas_mes_filtrado = df_vendas_mes[df_vendas_mes['mes'] == mes_filtro]
#df_vendas_mes
ax2 = px.bar(
    df_vendas_mes
    , x='Vendedor'
    , y='Valor_Total'
    , color='Vendedor'
    , color_discrete_sequence=['#1f77b4', '#ffffff', '#2ca02c', '#d62728', '#9467bd']
    , title='Vendas'
    , width=500
    , height=300
    , text='Valor_Total'
    , text_auto=True
    , template='plotly_dark'
    #, range_y = [0, meta_vendas]
)
ax2.update_layout(title_x=0.5)
col_2.plotly_chart(ax2)

df_vendas_mes_1 = df_vendas_filtrado.copy()
df_vendas_mes_1['mes'] = df_vendas_mes_1['DataVenda'].dt.month
df_vendas_mes_1['ano'] = df_vendas_mes_1['DataVenda'].dt.year
df_vendas_mes_1 = df_vendas_mes_1.groupby(['Produto', 'mes', 'ano'], as_index=False)['Valor'].sum()
df_vendas_mes1_filtrado = df_vendas_mes_1.groupby('Produto')['Valor'].sum().reset_index()
ax3 = px.bar(
    df_vendas_mes1_filtrado
    , x='Produto'
    , y='Valor'
    , color='Produto'
    , color_discrete_sequence=['#1f77b4', '#ffffff', '#2ca02c', '#d62728', '#9467bd']
    , title='Produtos'
    , labels={'x':'Produto', 'y':'Quantidade Total de Vendas'}
    , width=500
    , height=300
    , text='Valor'
    , text_auto=True
    , template='plotly_dark'
)
ax3.update_layout(title_x=0.5)
col_3.plotly_chart(ax3)

df_vendas_filtrado['mes'] = df_vendas_filtrado['DataVenda'].dt.month
df_vendas_produto_mes = df_vendas_filtrado.groupby(['mes', 'Vendedor'], as_index=False)['Valor_Total'].sum()
ax4 = px.bar(data_frame=df_vendas_produto_mes, x="mes", y="Valor_Total", color= 'Vendedor', barmode='group')

ax4.update_layout(
    title="Vendas Mensal",
    xaxis_title="Mês",
    yaxis_title="Valor Total de Vendas",
    legend_title="Vendedor",
    template='plotly_dark',
    width=1600,
    height=300,
    font=dict(size=14),
    legend=dict(font=dict(size=12)),
    xaxis=dict(ticktext=meses, tickvals=list(range(1, 13))),
    yaxis=dict(tickformat=".2f"),
    hovermode="x",
    hoverlabel=dict(font=dict(size=12)),
    margin=dict(l=50, r=50, t=50, b=50),
    showlegend=True,
    title_x=0.5,
    title_font=dict(size=20)
)
ax4.add_hline(y=50000, line_dash="dash", line_color="red", annotation=dict(text="Meta de Vendas", showarrow=False))
st.plotly_chart(ax4)
