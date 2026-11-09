import requests
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="3D Journey Shop", page_icon="🖨️", layout="wide")

# ==========================================
# CONFIGURAÇÕES DO REPOSITÓRIO DE FOTOS
# ==========================================
GITHUB_USER = "3DJourneyStore"
GITHUB_REPO = "Fotos"
GITHUB_BRANCH = "main"

def listar_conteudo_github(caminho=""):
    """Busca pastas e ficheiros de um repositório público do GitHub via API."""
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{caminho}"
    try:
        resposta = requests.get(api_url)
        if resposta.status_code == 200:
            return resposta.json()
    except Exception:
        pass
    return []

def pagina_inicio():
    st.title("🏠 Início")
    st.write("Bem-vindo ao **3D Journey Shop**! Seleciona uma opção no menu lateral.")

def pagina_catalogo():
    st.title("📸 Catálogo de Fotos por Categoria e Subcategoria")
    st.write("Explora as tuas pastas sincronizadas diretamente do repositório no GitHub.")

    conteudo_raiz = listar_conteudo_github("")

    if not conteudo_raiz or (isinstance(conteudo_raiz, dict) and "message" in conteudo_raiz):
        st.error(
            f"Não foi possível acessar o repositório '{GITHUB_USER}/{GITHUB_REPO}'. "
            "Certifica-te de que o repositório está configurado como **Public** (Público) nas definições do GitHub."
        )
        return

    # Exclui a pasta 'Cores' do catálogo principal para separar as coisas, se quiseres
    cat_principais = [item["name"] for item in conteudo_raiz if item["type"] == "dir" and item["name"].lower() != "cores"]

    if not cat_principais:
        st.info("Ainda não há pastas de categorias criadas no repositório 'Fotos'.")
        return

    filtro_principal = st.selectbox("Filtrar Categoria Principal", ["Todas"] + cat_principais)
    cats_a_mostrar = cat_principais if filtro_principal == "Todas" else [filtro_principal]

    for princ in cats_a_mostrar:
        st.markdown(f"## 📁 Categoria: {princ}")

        conteudo_princ = listar_conteudo_github(princ)
        subcats = [item["name"] for item in conteudo_princ if item["type"] == "dir"]

        if not subcats:
            mostrar_fotos_pasta(princ)
            st.divider()
            continue

        sub_filtro = st.selectbox(
            f"Filtrar Subcategoria em '{princ}'",
            ["Todas"] + subcats,
            key=f"filtro_sub_{princ}"
        )
        subs_a_mostrar = subcats if sub_filtro == "Todas" else [sub_filtro]

        for sub in subs_a_mostrar:
            st.markdown(f"#### 🏷️ Subcategoria: {sub}")
            caminho_sub = f"{princ}/{sub}"
            conteudo_sub = listar_conteudo_github(caminho_sub)
            sub_subcats = [item["name"] for item in conteudo_sub if item["type"] == "dir"]
            
            if sub_subcats:
                for sub_sub in sub_subcats:
                    st.markdown(f"*📂 **{sub_sub}***")
                    mostrar_fotos_pasta(f"{caminho_sub}/{sub_sub}")
            else:
                mostrar_fotos_pasta(caminho_sub)
                
            st.write("")
        st.divider()

def pagina_cores():
    st.title("🎨 Cores e Filamentos Disponíveis")
    st.write("Consulte abaixo as opções de cores e materiais (PLA, PETG, etc.) disponíveis para os seus projetos.")

    # Busca os arquivos diretamente da pasta 'Cores' no repositório do GitHub
    pasta_cores = "Cores"
    conteudo_cores = listar_conteudo_github(pasta_cores)

    if not conteudo_cores or (isinstance(conteudo_cores, dict) and "message" in conteudo_cores):
        st.info("A pasta **'Cores'** ainda não foi criada no repositório do GitHub ou está vazia.")
        st.write("💡 *Dica: Crie uma pasta chamada `Cores` no repositório 'Fotos' e envie imagens das amostras de filamento para lá.*")
        return

    # Se houver subpastas dentro de Cores (ex: por tipo de material: PLA, PETG)
    subpastas_cores = [item["name"] for item in conteudo_cores if item["type"] == "dir"]
    
    if subpastas_cores:
        material_filtro = st.selectbox("Filtrar por Material/Categoria", ["Todos"] + subpastas_cores)
        materiais_a_mostrar = subpastas_cores if material_filtro == "Todos" else [material_filtro]

        for mat in materiais_a_mostrar:
            st.markdown(f"### 🧵 Material: {mat}")
            mostrar_fotos_pasta(f"{pasta_cores}/{mat}")
            st.divider()
    else:
        # Se as fotos estiverem soltas direto na pasta 'Cores'
        mostrar_fotos_pasta(pasta_cores)

def mostrar_fotos_pasta(caminho_pasta):
    """Função auxiliar para buscar e exibir fotos de um caminho específico do GitHub."""
    conteudo = listar_conteudo_github(caminho_pasta)
    fotos = [
        item for item in conteudo
        if item["type"] == "file" and item["name"].lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    if not fotos:
        st.write("Nenhuma foto cadastrada nesta pasta.")
    else:
        cols = st.columns(3)
        for idx, foto in enumerate(fotos):
            with cols[idx % 3]:
                with st.container(border=True):
                    url_raw = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{caminho_pasta}/{foto['name']}"
                    st.image(url_raw, use_column_width=True)
                    nome_bonito = foto["name"].rsplit(".", 1)[0].replace("_", " ")
                    st.caption(nome_bonito)

# ==========================================
# NAVEGAÇÃO / MENU LATERAL
# ==========================================
st.sidebar.title("🖨️ 3D Journey Shop")
opcao_menu = st.sidebar.radio(
    "Navegação",
    [
        "Início",
        "Catálogo de Fotos",
        "Cores Disponíveis"
    ]
)

if opcao_menu == "Início":
    pagina_inicio()
elif opcao_menu == "Catálogo de Fotos":
    pagina_catalogo()
elif opcao_menu == "Cores Disponíveis":
    pagina_cores()
