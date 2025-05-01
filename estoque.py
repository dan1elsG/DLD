import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Controle de Estoque - Roupas Masculinas",
    page_icon="👔",
    layout="wide"
)

# Título da aplicação
st.title("👔 Sistema de Controle de Estoque - Roupas Masculinas")

# Inicialização do estado da sessão
if 'produtos' not in st.session_state:
    st.session_state.produtos = pd.DataFrame(columns=[
        'codigo',
        'produto',
        'tamanho',
        'cor',
        'preco_custo',
        'preco_venda',
        'estoque_minimo',
        'estoque_atual',
        'data_cadastro',
        'ultima_atualizacao'
    ])

if 'pedidos' not in st.session_state:
    st.session_state.pedidos = pd.DataFrame(columns=[
        'ID',
        'Cliente',
        'Codigo_Produto',
        'Produto',
        'Tamanho',
        'Cor',
        'Quantidade',
        'Valor_Unitario',
        'Valor_Total',
        'Data',
        'Status'
    ])


# Funções para salvar e carregar dados
def salvar_dados():
    st.session_state.produtos.to_csv('estoque.csv', index=False)
    st.session_state.pedidos.to_csv('pedidos.csv', index=False)


def carregar_dados():
    if os.path.exists('estoque.csv'):
        try:
            st.session_state.produtos = pd.read_csv('estoque.csv')
        except:
            st.warning("Arquivo de estoque encontrado, mas com formato diferente. Iniciando com dados vazios.")

    if os.path.exists('pedidos.csv'):
        try:
            st.session_state.pedidos = pd.read_csv('pedidos.csv')
        except:
            st.warning("Arquivo de pedidos encontrado, mas com formato diferente. Iniciando com dados vazios.")


# Carregar dados existentes
carregar_dados()

# Criar as abas
tab1, tab2, tab3 = st.tabs(["📝 Cadastrar Produtos", "📋 Lista de Produtos", "🛍️ Pedidos"])

# Aba 1: Cadastrar Produtos
with tab1:
    st.header("Cadastro de Roupas")

    # Formulário de cadastro
    with st.form("form_cadastro_produto"):
        col1, col2 = st.columns(2)

        with col1:
            codigo = st.text_input("Código do Produto*")
            produto = st.text_input("Nome do Produto*")
            tamanho = st.selectbox(
                "Tamanho*",
                ["PP", "P", "M", "G", "GG", "XG"]
            )
            cor = st.text_input("Cor*")

        with col2:
            preco_custo = st.number_input("Preço de Custo (R$)*", min_value=0.0, format="%.2f")
            preco_venda = st.number_input("Preço de Venda (R$)*", min_value=0.0, format="%.2f")
            estoque_minimo = st.number_input("Estoque Mínimo*", min_value=0)
            estoque_atual = st.number_input("Estoque Inicial*", min_value=0)

        # Botão de submit
        submitted = st.form_submit_button("Cadastrar Produto", type="primary")

        if submitted:
            if codigo and produto and cor and preco_custo and preco_venda:
                # Verificar se o código já existe
                if codigo in st.session_state.produtos['codigo'].values:
                    st.error("❌ Código do produto já existe!")
                else:
                    # Criar novo produto
                    novo_produto = pd.DataFrame({
                        'codigo': [codigo],
                        'produto': [produto],
                        'tamanho': [tamanho],
                        'cor': [cor],
                        'preco_custo': [preco_custo],
                        'preco_venda': [preco_venda],
                        'estoque_minimo': [estoque_minimo],
                        'estoque_atual': [estoque_atual],
                        'data_cadastro': [datetime.now()],
                        'ultima_atualizacao': [datetime.now()]
                    })

                    # Adicionar ao DataFrame
                    st.session_state.produtos = pd.concat([st.session_state.produtos, novo_produto], ignore_index=True)

                    # Salvar dados
                    salvar_dados()

                    st.success("✅ Produto cadastrado com sucesso!")
            else:
                st.error("❌ Por favor, preencha todos os campos obrigatórios!")

# Aba 2: Lista de Produtos
with tab2:
    st.header("Lista de Produtos")

    if not st.session_state.produtos.empty:
        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            tamanho_filtro = st.selectbox(
                "Filtrar por Tamanho",
                ["Todos"] + list(st.session_state.produtos['tamanho'].unique()),
                key="filtro_tamanho"
            )

        with col2:
            cor_filtro = st.selectbox(
                "Filtrar por Cor",
                ["Todas"] + list(st.session_state.produtos['cor'].unique()),
                key="filtro_cor"
            )

        with col3:
            estoque_baixo = st.checkbox("Mostrar apenas produtos com estoque abaixo do mínimo")

        # Aplicar filtros
        df_filtrado = st.session_state.produtos.copy()

        if tamanho_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['tamanho'] == tamanho_filtro]

        if cor_filtro != "Todas":
            df_filtrado = df_filtrado[df_filtrado['cor'] == cor_filtro]

        if estoque_baixo:
            df_filtrado = df_filtrado[df_filtrado['estoque_atual'] < df_filtrado['estoque_minimo']]

        # Exibir tabela
        st.dataframe(
            df_filtrado,
            column_config={
                "codigo": "Código",
                "produto": "Produto",
                "tamanho": "Tamanho",
                "cor": "Cor",
                "preco_custo": st.column_config.NumberColumn(
                    "Preço de Custo",
                    format="R$ %.2f"
                ),
                "preco_venda": st.column_config.NumberColumn(
                    "Preço de Venda",
                    format="R$ %.2f"
                ),
                "estoque_minimo": st.column_config.NumberColumn(
                    "Estoque Mínimo",
                    format="%d"
                ),
                "estoque_atual": st.column_config.NumberColumn(
                    "Estoque Atual",
                    format="%d"
                ),
                "data_cadastro": "Data de Cadastro",
                "ultima_atualizacao": "Última Atualização"
            },
            hide_index=True
        )

        # Estatísticas rápidas
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Produtos", len(df_filtrado))

        with col2:
            produtos_baixo_estoque = len(df_filtrado[df_filtrado['estoque_atual'] < df_filtrado['estoque_minimo']])
            st.metric("Produtos com Estoque Baixo", produtos_baixo_estoque)

        with col3:
            valor_total = (df_filtrado['estoque_atual'] * df_filtrado['preco_custo']).sum()
            st.metric("Valor Total em Estoque", f"R$ {valor_total:.2f}")
    else:
        st.info("Nenhum produto cadastrado ainda.")

# Aba 3: Pedidos
with tab3:
    st.header("Pedidos")

    # Formulário para novo pedido
    with st.form("novo_pedido"):
        col1, col2 = st.columns(2)

        with col1:
            cliente = st.text_input("Nome do Cliente*")
            codigo_produto = st.text_input("Código do Produto*")

            # Buscar informações do produto
            if codigo_produto:
                produto_info = st.session_state.produtos[st.session_state.produtos['codigo'] == codigo_produto]
                if not produto_info.empty:
                    st.info(f"""
                    **Produto:** {produto_info['produto'].iloc[0]}  
                    **Tamanho:** {produto_info['tamanho'].iloc[0]}  
                    **Cor:** {produto_info['cor'].iloc[0]}  
                    **Preço:** R$ {produto_info['preco_venda'].iloc[0]:.2f}  
                    **Estoque:** {produto_info['estoque_atual'].iloc[0]} unidades
                    """)

        with col2:
            quantidade = st.number_input("Quantidade*", min_value=1, value=1)

        submitted = st.form_submit_button("Adicionar Pedido", type="primary")

        if submitted:
            if cliente and codigo_produto and quantidade:
                # Verificar se o produto existe
                produto_info = st.session_state.produtos[st.session_state.produtos['codigo'] == codigo_produto]
                if not produto_info.empty:
                    # Verificar estoque
                    if quantidade <= produto_info['estoque_atual'].iloc[0]:
                        valor_unitario = produto_info['preco_venda'].iloc[0]
                        valor_total = quantidade * valor_unitario

                        # Criar novo pedido
                        novo_pedido = pd.DataFrame({
                            'ID': [len(st.session_state.pedidos) + 1],
                            'Cliente': [cliente],
                            'Codigo_Produto': [codigo_produto],
                            'Produto': [produto_info['produto'].iloc[0]],
                            'Tamanho': [produto_info['tamanho'].iloc[0]],
                            'Cor': [produto_info['cor'].iloc[0]],
                            'Quantidade': [quantidade],
                            'Valor_Unitario': [valor_unitario],
                            'Valor_Total': [valor_total],
                            'Data': [datetime.now().strftime("%d/%m/%Y %H:%M")],
                            'Status': ['Pendente']
                        })

                        # Atualizar estoque
                        st.session_state.produtos.loc[
                            st.session_state.produtos['codigo'] == codigo_produto, 'estoque_atual'] -= quantidade

                        # Adicionar pedido
                        st.session_state.pedidos = pd.concat([st.session_state.pedidos, novo_pedido], ignore_index=True)

                        # Salvar dados
                        salvar_dados()

                        st.success("✅ Pedido adicionado com sucesso!")
                    else:
                        st.error("❌ Quantidade indisponível em estoque!")
                else:
                    st.error("❌ Código do produto não encontrado!")
            else:
                st.error("❌ Por favor, preencha todos os campos obrigatórios!")

    # Filtros de pedidos
    col1, col2 = st.columns(2)
    with col1:
        status_filtro = st.selectbox(
            "Filtrar por Status",
            ["Todos"] + list(st.session_state.pedidos['Status'].unique()) if not st.session_state.pedidos.empty else [
                "Todos"],
            key="filtro_status"
        )
    with col2:
        cliente_filtro = st.text_input("Buscar por Cliente", key="busca_cliente")

    # Aplicar filtros
    if not st.session_state.pedidos.empty:
        df_filtrado = st.session_state.pedidos.copy()

        if status_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Status'] == status_filtro]

        if cliente_filtro:
            df_filtrado = df_filtrado[df_filtrado['Cliente'].str.contains(cliente_filtro, case=False)]

        # Exibir tabela de pedidos
        st.dataframe(
            df_filtrado,
            column_config={
                "ID": "ID",
                "Cliente": "Cliente",
                "Codigo_Produto": "Código",
                "Produto": "Produto",
                "Tamanho": "Tamanho",
                "Cor": "Cor",
                "Quantidade": st.column_config.NumberColumn(
                    "Quantidade",
                    format="%d"
                ),
                "Valor_Unitario": st.column_config.NumberColumn(
                    "Valor Unitário",
                    format="R$ %.2f"
                ),
                "Valor_Total": st.column_config.NumberColumn(
                    "Valor Total",
                    format="R$ %.2f"
                ),
                "Data": "Data",
                "Status": "Status"
            },
            hide_index=True
        )

        # Estatísticas
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de Pedidos", len(df_filtrado))

        with col2:
            valor_total = df_filtrado['Valor_Total'].sum() if 'Valor_Total' in df_filtrado.columns else 0
            st.metric("Valor Total", f"R$ {valor_total:.2f}")

        with col3:
            st.metric("Pedidos Pendentes", len(df_filtrado[df_filtrado['Status'] == 'Pendente']))

        # Atualizar status
        st.subheader("Atualizar Status do Pedido")
        col1, col2 = st.columns(2)

        with col1:
            pedido_id = st.number_input("ID do Pedido", min_value=1,
                                        max_value=len(df_filtrado) if len(df_filtrado) > 0 else 1)

        with col2:
            novo_status = st.selectbox(
                "Novo Status",
                ["Pendente", "Em Processamento", "Enviado", "Entregue", "Cancelado"],
                key="novo_status"
            )

        if st.button("Atualizar Status", type="primary"):
            if pedido_id in df_filtrado['ID'].values:
                st.session_state.pedidos.loc[st.session_state.pedidos['ID'] == pedido_id, 'Status'] = novo_status
                salvar_dados()
                st.success("✅ Status atualizado com sucesso!")
            else:
                st.error("❌ ID do pedido não encontrado!")
    else:
        st.info("Nenhum pedido registrado ainda.")