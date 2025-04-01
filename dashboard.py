
import streamlit as st
st.set_page_config(page_title="Dashboard Financeiro - Composição de Despesas", page_icon=":bar_chart:")

import pandas as pd
import plotly.express as px
from io import BytesIO
import urllib.parse

# Função para carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel("DADOS to AI Testing.xlsx", sheet_name="Dados para AI- Light")
    df = df.drop(columns=["total"], errors="ignore")
    df.set_index("Conta Contábil", inplace=True)
    df = df.T.apply(pd.to_numeric, errors='coerce')
    df = df.replace(1, pd.NA)  # remover valores 1 como placeholder
    return df

# Função para exportar CSV
def convert_df_to_csv(df):
    return df.to_csv(index=True).encode('utf-8')

# Função para exportar imagem PNG
def fig_to_png_bytes(fig):
    buf = BytesIO()
    fig.write_image(buf, format="png")
    buf.seek(0)
    return buf

# Carregar dados
df = load_data()

# Sidebar - Filtros
st.sidebar.header("Filtros")
selected_accounts = st.sidebar.multiselect("Selecionar contas contábeis:", df.columns.tolist(), default=df.columns.tolist())
selected_month = st.sidebar.selectbox("Selecionar mês para gráfico de pizza:", df.index.tolist())

# Filtrar dados
df_filtered = df[selected_accounts]

# Título e logo
st.image("Panda Icon 32x32.ico", width=60)
st.title("Dashboard Financeiro - Composição de Despesas")
st.subheader("Análise de Contas Contábeis por Mês")
st.markdown("Este dashboard mostra a evolução mensal das principais contas contábeis, com filtros interativos e opções de exportação.")

# Cards
if not df_filtered.empty:
    total_geral = df_filtered.sum().sum()
    total_receitas = df_filtered[df_filtered > 0].sum().sum()
    total_despesas = df_filtered[df_filtered < 0].sum().sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("Resultado Geral", f"R$ {total_geral:,.2f}")
    col2.metric("Total Receitas", f"R$ {total_receitas:,.2f}")
    col3.metric("Total Despesas", f"R$ {total_despesas:,.2f}")

    # Gráfico interativo de linha
    fig_line = px.line(df_filtered, x=df_filtered.index, y=df_filtered.columns, labels={"value": "Valor (R$)", "index": "Mês"}, title="Evolução Mensal das Contas")
    st.plotly_chart(fig_line)

    # Gráfico de barras: Total por conta
    totais_por_conta = df_filtered.sum()
    if totais_por_conta.dropna().empty:
        st.warning("Nenhum dado disponível para o gráfico de barras.")
    else:
        fig_bar = px.bar(totais_por_conta, x=totais_por_conta.index, y=totais_por_conta.values,
                         labels={"x": "Conta Contábil", "y": "Total (R$)"},
                         title="Total por Conta Contábil no Ano")
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar)

    # Gráfico de pizza: Composição percentual do mês selecionado
    valores_mes = df_filtered.loc[selected_month].dropna()
    if valores_mes.empty:
        st.warning("Nenhum dado disponível para o gráfico de pizza.")
    else:
        fig_pie = px.pie(names=valores_mes.index, values=valores_mes.values,
                         title=f"Composição Percentual - {selected_month}")
        st.plotly_chart(fig_pie)
        st.download_button("Exportar Pizza como PNG", fig_to_png_bytes(fig_pie), file_name="grafico_pizza.png")

    # Análise financeira
    with st.expander("Ver Análise Financeira"):
        for col in df_filtered.columns:
            serie = df_filtered[col]
            if serie.dropna().shape[0] > 1:
                var = serie.pct_change().mean()
                tendencia = "crescente" if var > 0 else "decrescente"
                st.write(f"- A conta **{col}** tem uma tendência {tendencia} com variação média de {var:.2%} por mês.")

    # Botões
    st.download_button("Baixar dados filtrados", convert_df_to_csv(df_filtered), "dados_filtrados.csv", "text/csv")
    st.download_button("Baixar todos os dados", convert_df_to_csv(df), "dados_completos.csv", "text/csv")
else:
    st.warning("Nenhuma conta contábil selecionada ou dados indisponíveis.")

# Compartilhar via WhatsApp
dashboard_url = "https://seuapp.streamlit.app/"  # Substituir com URL real
msg = f"Confira o dashboard financeiro aqui: {dashboard_url}"
encoded_msg = urllib.parse.quote(msg)
whatsapp_url = f"https://wa.me/?text={encoded_msg}"
st.markdown(f"[Compartilhar via WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

# Compartilhar via E-mail
email_subject = urllib.parse.quote("Dashboard Financeiro - Composição de Despesas")
email_body = urllib.parse.quote(f"Olá,

Confira o dashboard financeiro no seguinte link:
{dashboard_url}

Atenciosamente,")
mailto_link = f"mailto:?subject={email_subject}&body={email_body}"
st.markdown(f"[Compartilhar por E-mail]({mailto_link})", unsafe_allow_html=True)

# Rodapé
st.markdown("---")
st.markdown("Desenvolvido por [Sua Empresa](https://example.com)")
