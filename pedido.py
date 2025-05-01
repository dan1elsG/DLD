import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Pedidos - DLD",
    page_icon="🏪",
    layout="wide"
)

# Função para carregar dados do CSV
def carregar_pedidos():
    if os.path.exists('pedidos.csv'):
        try:
            return pd.read_csv('pedidos.csv')
        except:
            st.warning("Arquivo de pedidos encontrado, mas com formato diferente. Iniciando com dados vazios.")
    return pd.DataFrame(columns=['ID', 'Cliente', 'Produto', 'Tamanho', 'Quantidade', 'Valor', 'Data', 'Status'])

# Função para salvar dados no CSV
def salvar_pedidos(df):
    try:
        df.to_csv('pedidos.csv', index=False)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar pedidos: {str(e)}")
        return False

# Título do aplicativo
st.title("🏪 Sistema de Pedidos - DLD")

# Carregar dados
df = carregar_pedidos()

# Sidebar para adicionar novo pedido
st.sidebar.header("Novo Pedido")

# Formulário para novo pedido
with st.sidebar.form("novo_pedido"):
    cliente = st.text_input("Nome do Cliente")
    produto = st.text_input("Produto")
    tamanho = st.selectbox("Tamanho", ["PP", "P", "M", "G", "GG", "XG"])
    quantidade = st.number_input("Quantidade", min_value=1, value=1)
    valor = st.number_input("Valor (R$)", min_value=0.0, value=0.0)

    submitted = st.form_submit_button("Adicionar Pedido")

    if submitted:
        novo_pedido = {
            'ID': len(df) + 1,
            'Cliente': cliente,
            'Produto': produto,
            'Tamanho': tamanho,
            'Quantidade': quantidade,
            'Valor': valor,
            'Data': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'Status': 'Pendente'
        }
        df = pd.concat([df, pd.DataFrame([novo_pedido])], ignore_index=True)
        if salvar_pedidos(df):
            st.success("Pedido adicionado com sucesso!")
        else:
            st.error("Erro ao salvar o pedido.")

# Área principal - Visualização dos pedidos
st.header("Pedidos Atuais")

# Filtros
col1, col2 = st.columns(2)
with col1:
    status_filtro = st.selectbox("Filtrar por Status", ["Todos"] + list(df['Status'].unique()))
with col2:
    cliente_filtro = st.text_input("Buscar por Cliente")

# Aplicar filtros
if status_filtro != "Todos":
    df_filtrado = df[df['Status'] == status_filtro]
else:
    df_filtrado = df

if cliente_filtro:
    df_filtrado = df_filtrado[df_filtrado['Cliente'].str.contains(cliente_filtro, case=False)]

# Exibir tabela de pedidos
st.dataframe(df_filtrado, use_container_width=True)

# Área de estatísticas
st.header("Estatísticas")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Pedidos", len(df))
with col2:
    st.metric("Valor Total", f"R$ {df['Valor'].sum():.2f}")
with col3:
    st.metric("Pedidos Pendentes", len(df[df['Status'] == 'Pendente']))

# Área para atualizar status do pedido
st.header("Atualizar Status do Pedido")
pedido_id = st.number_input("ID do Pedido", min_value=1, max_value=len(df) if len(df) > 0 else 1)
novo_status = st.selectbox("Novo Status", ["Pendente", "Em Processamento", "Enviado", "Entregue", "Cancelado"])

if st.button("Atualizar Status"):
    if pedido_id in df['ID'].values:
        df.loc[df['ID'] == pedido_id, 'Status'] = novo_status
        if salvar_pedidos(df):
            st.success("Status atualizado com sucesso!")
        else:
            st.error("Erro ao atualizar o status.")
    else:
        st.error("ID do pedido não encontrado!")