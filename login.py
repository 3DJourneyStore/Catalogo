import streamlit as st

st.set_page_config(page_title="3D Journey Shop", page_icon="🖨️", layout="wide")

inicio = st.Page("pages/inicio.py", title="Início", icon=":material/home:", default=True)

calculadora = st.Page(
    "pages/calculadora.py", title="Calculadora 3D", icon=":material/calculate:"
)

produtos = st.Page(
    "pages/produtos.py", title="Produtos", icon=":material/inventory_2:"
)

# ADICIONANDO A PÁGINA DE CATÁLOGO AQUI:
catalogo = st.Page(
    "pages/catalogo.py", title="Catálogo de Fotos", icon=":material/photo_library:"
)

configuracoes = st.Page(
    "pages/configuracoes.py",
    title="Configurações de custos",
    icon=":material/settings:",
)

orcamentos = st.Page(
    "pages/orcamentos.py", title="Orçamentos", icon=":material/receipt_long:"
)

pedidos = st.Page(
    "pages/pedidos.py", title="Pedidos", icon=":material/shopping_cart:"
)

clientes = st.Page("pages/clientes.py", title="Clientes", icon=":material/group:")

paginas = {
    "Principal": [inicio],
    "Produção": [pedidos, orcamentos],
    # Coloquei o catálogo junto com produtos e calculadora, mas você pode mudar se quiser!
    "Cadastros": [produtos, calculadora, catalogo],
    "Sistema": [configuracoes, clientes],
}

navegacao = st.navigation(paginas)
navegacao.run()