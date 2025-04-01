
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from io import BytesIO
import urllib.parse

# Carregamento da planilha
@st.cache_data
def carregar_dados():
    df = pd.read_excel("DADOS to AI Testing.xlsx", sheet_name="Dados para AI- Light")
    df = df.drop(columns=['total'])
    df_melted = df.melt(id_vars=['Conta Contábil'], var_name='Mês', value_name='Valor')
    return df, df_melted

# Layout do app
st.set_page_config(
    page_title="Dashboard Financeiro - Composição de Despesas",
    layout="wide",
    page_icon="📊"
)

# Logo e título
st.image("Panda Icon 32x32.ico", width=50)
st.markdown("# Dashboard Financeiro - Composição de Despesas")
st.markdown("Visualize a composição mensal de receitas e despesas com gráficos interativos.")

# Carregar os dados
df, df_melted = carregar_dados()

# Filtros interativos
contas = st.sidebar.multiselect("Selecione as Contas Contábeis:", options=df['Conta Contábil'].unique(), default=df['Conta Contábil'].unique())
meses = st.sidebar.multiselect("Selecione os Meses:", options=df_melted['Mês'].unique(), default=df_melted['Mês'].unique())

# Aplicar filtros
df_filtrado = df_melted[df_melted['Conta Contábil'].isin(contas) & df_melted['Mês'].isin(meses)]

# Cards de totais
st.markdown("### Totais Gerais")
col1, col2, col3 = st.columns(3)
resultado_geral = df[df['Conta Contábil'] == 'Receita Líquida'].drop(columns='Conta Contábil').sum().sum()
despesas = df[df['Conta Contábil'].str.contains("Despesa")].drop(columns='Conta Contábil').sum().sum()
receitas = df[df['Conta Contábil'].str.contains("Receita")].drop(columns='Conta Contábil').sum().sum()
col1.metric("Resultado Geral", f"R$ {resultado_geral:,.2f}")
col2.metric("Total Despesas", f"R$ {despesas:,.2f}")
col3.metric("Total Receitas", f"R$ {receitas:,.2f}")

# Gráfico de Linhas
st.markdown("### Evolução Mensal das Contas")
fig_linhas = go.Figure()
for conta in df_filtrado['Conta Contábil'].unique():
    dados_conta = df_filtrado[df_filtrado['Conta Contábil'] == conta]
    fig_linhas.add_trace(go.Scatter(
        x=dados_conta['Mês'],
        y=dados_conta['Valor'],
        mode='lines+markers',
        name=conta,
        line=dict(width=0.2)
    ))
fig_linhas.update_layout(
    xaxis_title='Mês',
    yaxis_title='Valor (R$)',
    plot_bgcolor='white',
    paper_bgcolor='white',
    hovermode='x unified'
)
st.plotly_chart(fig_linhas, use_container_width=True)

# Gráfico de Barras (Total Anual por Conta)
st.markdown("### Total Anual por Conta Contábil")
df_barras = df_filtrado.groupby('Conta Contábil')['Valor'].sum().reset_index()
fig_barras = go.Figure(go.Bar(
    x=df_barras['Valor'],
    y=df_barras['Conta Contábil'],
    orientation='h',
    text=df_barras['Valor'],
    textposition='auto'
))
fig_barras.update_layout(
    xaxis_title='Total Anual (R$)',
    yaxis_title='Conta Contábil',
    plot_bgcolor='white',
    paper_bgcolor='white'
)
st.plotly_chart(fig_barras, use_container_width=True)

# Gráfico de Pizza - Composição Percentual por Mês
st.markdown("### Composição Percentual das Contas por Mês")
mes_pizza = st.selectbox("Selecione um Mês para o Gráfico de Pizza:", options=meses)
df_pizza = df_filtrado[df_filtrado['Mês'] == mes_pizza]
df_pizza_grouped = df_pizza.groupby('Conta Contábil')['Valor'].sum().reset_index()
fig_pizza = go.Figure(go.Pie(
    labels=df_pizza_grouped['Conta Contábil'],
    values=df_pizza_grouped['Valor'],
    hoverinfo='label+percent',
    textinfo='percent+label',
    hole=0.3
))
fig_pizza.update_layout(
    paper_bgcolor='white'
)
st.plotly_chart(fig_pizza, use_container_width=True)

# Análise financeira dos gráficos
with st.expander("📊 Mostrar Análise Financeira"):
    st.markdown("### Análise Financeira")
    maiores = df_barras.sort_values(by='Valor', ascending=False).head(3)
    menores = df_barras.sort_values(by='Valor').head(3)
    st.write("**Top 3 maiores contas:**")
    for i, row in maiores.iterrows():
        st.write(f"- {row['Conta Contábil']}: R$ {row['Valor']:,.2f}")
    st.write("**Top 3 menores contas:**")
    for i, row in menores.iterrows():
        st.write(f"- {row['Conta Contábil']}: R$ {row['Valor']:,.2f}")

# Botões de exportação
st.markdown("### Exportações")
col_csv, col_img = st.columns(2)

# Download CSV dos dados filtrados
csv = df_filtrado.to_csv(index=False).encode('utf-8')
col_csv.download_button(
    label="📥 Baixar Dados Filtrados (.CSV)",
    data=csv,
    file_name='dados_filtrados.csv',
    mime='text/csv'
)

# Exportar gráfico como imagem PNG
img_bytes = fig_linhas.to_image(format="png")
col_img.download_button(
    label="🖼️ Exportar Gráfico de Linhas (PNG)",
    data=img_bytes,
    file_name="grafico_linhas.png",
    mime="image/png"
)

# Compartilhamento via WhatsApp e Email
st.markdown("### Compartilhar")
link_app = "https://seuapp.streamlit.app"  # substitua pelo link real do app
mensagem = f"Confira este dashboard financeiro: {link_app}"
url_whatsapp = f"https://wa.me/?text={urllib.parse.quote(mensagem)}"
url_email = f"mailto:?subject=Dashboard Financeiro&body={urllib.parse.quote(mensagem)}"
st.markdown(f"[📲 Enviar via WhatsApp]({url_whatsapp})", unsafe_allow_html=True)
st.markdown(f"[📧 Enviar por Email]({url_email})", unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido por Ricardo | Engenharia e Software Designer ©")
