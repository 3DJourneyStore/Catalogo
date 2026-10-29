
import requests
import streamlit as st
from urllib.parse import quote

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="3D Journey Shop",
    page_icon="🖨️",
    layout="wide"
)

# ==========================================
# CONFIGURAÇÕES DO REPOSITÓRIO GITHUB
# ==========================================
GITHUB_USER = "3DJourneyStore"
GITHUB_REPO = "Fotos"
GITHUB_BRANCH = "main"

GITHUB_API_BASE = (
    f"https://api.github.com/repos/"
    f"{GITHUB_USER}/{GITHUB_REPO}/contents"
)

GITHUB_RAW_BASE = (
    f"https://raw.githubusercontent.com/"
    f"{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
)

EXTENSOES_IMAGEM = (".png", ".jpg", ".jpeg")


# ==========================================
# CONSULTA À API DO GITHUB
# ==========================================
@st.cache_data(ttl=300, show_spinner=False)
def listar_conteudo_github(caminho=""):
    """
    Lista arquivos e pastas do repositório público.
    Retorna:
        - Lista de arquivos/pastas em caso de sucesso.
        - Dicionário com erro em caso de falha.
    """

    caminho = caminho.strip("/")
    caminho_codificado = quote(caminho, safe="/")

    api_url = GITHUB_API_BASE

    if caminho_codificado:
        api_url = f"{api_url}/{caminho_codificado}"

    try:
        resposta = requests.get(
            api_url,
            params={"ref": GITHUB_BRANCH},
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            timeout=15
        )

        if resposta.status_code == 200:
            dados = resposta.json()

            # A API pode retornar um objeto para um arquivo,
            # mas esperamos uma lista ao consultar pastas.
            if isinstance(dados, list):
                return dados

            return {
                "erro": "A API retornou um arquivo em vez de uma pasta.",
                "status": resposta.status_code,
                "caminho": caminho or "/"
            }

        try:
            detalhe = resposta.json().get(
                "message",
                resposta.text
            )
        except ValueError:
            detalhe = resposta.text

        return {
            "erro": detalhe,
            "status": resposta.status_code,
            "caminho": caminho or "/"
        }

    except requests.Timeout:
        return {
            "erro": "Tempo limite excedido ao consultar o GitHub.",
            "status": None,
            "caminho": caminho or "/"
        }

    except requests.RequestException as erro:
        return {
            "erro": str(erro),
            "status": None,
            "caminho": caminho or "/"
        }


# ==========================================
# EXIBIÇÃO DE ERROS
# ==========================================
def exibir_erro_github(resultado):
    """Apresenta os detalhes do erro retornado pela API."""

    if not isinstance(resultado, dict):
        st.error("Não foi possível carregar o conteúdo do GitHub.")
        return

    status = resultado.get("status")
    detalhe = resultado.get("erro", "Erro desconhecido")
    caminho = resultado.get("caminho", "/")

    if status is not None:
        st.error(f"Erro HTTP {status} ao consultar o GitHub.")

    st.warning(f"Detalhe informado: {detalhe}")
    st.caption(f"Caminho consultado: {caminho}")

    if status == 404:
        st.info(
            "Verifique se a branch main existe, se o repositório "
            "possui um commit inicial e se o caminho está correto."
        )

    elif status == 403:
        st.info(
            "O GitHub pode ter limitado as requisições ou bloqueado "
            "temporariamente o acesso. Verifique o limite da API."
        )


# ==========================================
# PÁGINA INICIAL
# ==========================================
def pagina_inicio():
    st.title("🏠 Início")

    st.write(
        "Bem-vindo ao **3D Journey Shop**! "
        "Selecione a opção **Catálogo de Fotos** no menu lateral "
        "para visualizar as imagens organizadas por categoria."
    )


# ==========================================
# EXIBIÇÃO DAS FOTOS
# ==========================================
def mostrar_fotos_pasta(caminho_pasta):
    """Busca e apresenta as imagens existentes em uma pasta."""

    conteudo = listar_conteudo_github(caminho_pasta)

    if isinstance(conteudo, dict):
        exibir_erro_github(conteudo)
        return

    fotos = [
        item
        for item in conteudo
        if item.get("type") == "file"
        and item.get("name", "").lower().endswith(EXTENSOES_IMAGEM)
    ]

    if not fotos:
        st.caption("Nenhuma foto cadastrada nesta pasta.")
        return

    cols = st.columns(3)

    for idx, foto in enumerate(fotos):
        with cols[idx % 3]:
            with st.container(border=True):

                caminho_arquivo = (
                    f"{caminho_pasta.strip('/')}/{foto['name']}"
                    if caminho_pasta.strip("/")
                    else foto["name"]
                )

                caminho_codificado = quote(
                    caminho_arquivo,
                    safe="/"
                )

                url_imagem = f"{GITHUB_RAW_BASE}/{caminho_codificado}"

                try:
                    st.image(
                        url_imagem,
                        use_container_width=True
                    )

                    nome_bonito = foto["name"].rsplit(".", 1)[0]
                    nome_bonito = nome_bonito.replace("_", " ")

                    st.caption(nome_bonito)

                except Exception as erro:
                    st.warning(
                        f"Não foi possível exibir "
                        f"{foto['name']}: {erro}"
                    )


# ==========================================
# CATÁLOGO DE FOTOS
# ==========================================
def pagina_catalogo():
    st.title("📸 Catálogo de Fotos")
    st.write(
        "Explore as pastas sincronizadas diretamente "
        "do repositório público no GitHub."
    )

    # Botão para limpar o cache e consultar novamente
    if st.button("🔄 Atualizar catálogo"):
        st.cache_data.clear()
        st.rerun()

    # ------------------------------------------
    # 1. CATEGORIAS PRINCIPAIS
    # ------------------------------------------
    conteudo_raiz = listar_conteudo_github("")

    if isinstance(conteudo_raiz, dict):
        st.error(
            f"Não foi possível acessar "
            f"{GITHUB_USER}/{GITHUB_REPO}."
        )
        exibir_erro_github(conteudo_raiz)
        return

    cat_principais = sorted(
        [
            item["name"]
            for item in conteudo_raiz
            if item.get("type") == "dir"
        ],
        key=str.lower
    )

    if not cat_principais:
        st.info(
            "Nenhuma pasta de categoria foi encontrada na raiz "
            "do repositório. Verifique se os arquivos foram enviados "
            "e se existe uma branch main com um commit."
        )
        return

    filtro_principal = st.selectbox(
        "Filtrar categoria principal",
        ["Todas"] + cat_principais
    )

    cats_a_mostrar = (
        cat_principais
        if filtro_principal == "Todas"
        else [filtro_principal]
    )

    # ------------------------------------------
    # 2. PERCORRER CATEGORIAS
    # ------------------------------------------
    for princ in cats_a_mostrar:
        st.markdown(f"## 📁 Categoria: {princ}")

        conteudo_princ = listar_conteudo_github(princ)

        if isinstance(conteudo_princ, dict):
            exibir_erro_github(conteudo_princ)
            st.divider()
            continue

        subcats = sorted(
            [
                item["name"]
                for item in conteudo_princ
                if item.get("type") == "dir"
            ],
            key=str.lower
        )

        # Se não houver subcategorias, mostrar as fotos diretamente
        if not subcats:
            mostrar_fotos_pasta(princ)
            st.divider()
            continue

        sub_filtro = st.selectbox(
            f"Filtrar subcategoria em '{princ}'",
            ["Todas"] + subcats,
            key=f"filtro_sub_{princ}"
        )

        subs_a_mostrar = (
            subcats
            if sub_filtro == "Todas"
            else [sub_filtro]
        )

        # ------------------------------------------
        # 3. PERCORRER SUBCATEGORIAS
        # ------------------------------------------
        for sub in subs_a_mostrar:
            st.markdown(f"### 🏷️ Subcategoria: {sub}")

            caminho_sub = f"{princ}/{sub}"
            conteudo_sub = listar_conteudo_github(caminho_sub)

            if isinstance(conteudo_sub, dict):
                exibir_erro_github(conteudo_sub)
                continue

            sub_subcats = sorted(
                [
                    item["name"]
                    for item in conteudo_sub
                    if item.get("type") == "dir"
                ],
                key=str.lower
            )

            # ------------------------------------------
            # 4. SUB-SUBCATEGORIAS
            # ------------------------------------------
            if sub_subcats:
                for sub_sub in sub_subcats:
                    st.markdown(f"📂 **{sub_sub}**")

                    caminho_completo = f"{caminho_sub}/{sub_sub}"
                    mostrar_fotos_pasta(caminho_completo)

            else:
                # Fotos diretamente na subcategoria
                mostrar_fotos_pasta(caminho_sub)

            st.write("")

        st.divider()


# ==========================================
# MENU LATERAL / NAVEGAÇÃO
# ==========================================
st.sidebar.title("🖨️ 3D Journey Shop")

opcao_menu = st.sidebar.radio(
    "Navegação",
    ["Início", "Catálogo de Fotos"]
)

if opcao_menu == "Início":
    pagina_inicio()

elif opcao_menu == "Catálogo de Fotos":
    pagina_catalogo()
