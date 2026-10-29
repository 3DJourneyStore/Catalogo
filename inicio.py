import requests
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="3D Journey Shop", page_icon="🖨️", layout="wide")

# ==========================================
# CONFIGURAÇÕES DO REPOSITÓRIO DE FOTOS
# ==========================================
GITHUB_USER = "3DJourneyStore"  # Baseado no print do seu repositório
GITHUB_REPO = "Fotos"
GITHUB_BRANCH = "main"


def listar_conteudo_github(caminho=""):
  """Busca os arquivos do repositório via API do GitHub."""
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
  st.write(
      "Bem-vindo ao **3D Journey Shop**! Selecione a opção 'Catálogo de Fotos'"
      " no menu lateral."
  )


def pagina_catalogo():
  st.title("📸 Catálogo de Fotos do Repositório")
  st.write(
      "As imagens abaixo são sincronizadas diretamente do seu repositório"
      f" **{GITHUB_REPO}**."
  )

  # Busca os arquivos na raiz do repositório
  conteudo = listar_conteudo_github("")

  if not conteudo or isinstance(conteudo, dict) and "message" in conteudo:
    st.error(
        f"Não foi possível acessar o repositório '{GITHUB_USER}/{GITHUB_REPO}'."
        " Se ele for privado, certifique-se de torná-lo público nas"
        " configurações do GitHub."
    )
    return

  # Filtra apenas imagens válidas
  fotos = [
      item
      for item in conteudo
      if item["type"] == "file"
      and item["name"].lower().endswith((".png", ".jpg", ".jpeg"))
  ]

  if not fotos:
    st.info("Nenhuma foto encontrada na raiz do repositório.")
    return

  # Organizando os produtos de forma inteligente com base no nome do arquivo (Ex: Caixa_Bege_Aberta)
  # Você pode criar um filtro simples por palavra-chave ou exibir em grade geral:
  pesquisa = st.text_input("🔍 Buscar foto no catálogo", "")

  fotos_filtradas = [
      f for f in fotos if pesquisa.lower() in f["name"].lower()
  ]

  st.write(f"Mostrando {len(fotos_filtradas)} foto(s)")

  cols = st.columns(3)
  for idx, foto in enumerate(fotos_filtradas):
    with cols[idx % 3]:
      with st.container(border=True):
        # URL raw oficial do GitHub
        url_raw = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{foto['name']}"
        st.image(url_raw, use_column_width=True)
        # Limpa o nome do arquivo para ficar bonito na legenda (tira o .jpeg e troca _ por espaço)
        nome_bonito = (
            foto["name"].rsplit(".", 1)[0].replace("_", " ")
        )
        st.caption(nome_bonito)


# ==========================================
# NAVEGAÇÃO / MENU LATERAL
# ==========================================
st.sidebar.title("🖨️ 3D Journey Shop")
opcao_menu = st.sidebar.radio("Navegação", ["Início", "Catálogo de Fotos"])

if opcao_menu == "Início":
  pagina_inicio()
elif opcao_menu == "Catálogo de Fotos":
  pagina_catalogo()
