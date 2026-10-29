import os
from PIL import Image
import streamlit as st

st.title("📸 Catálogo de Fotos por Categoria e Subcategoria")
st.write(
    "Organize seus produtos em categorias principais e subcategorias,"
    " enviando fotos facilmente."
)

UPLOAD_DIR = "fotos_catalogo"
if not os.path.exists(UPLOAD_DIR):
  os.makedirs(UPLOAD_DIR)

# Criando Abas para organizar
aba_catalogo, aba_upload = st.tabs(
    ["📂 Ver Catálogo", "📤 Enviar e Gerenciar"]
)

# ==========================================
# ABA 1: VISUALIZAÇÃO DO CATÁLOGO
# ==========================================
with aba_catalogo:
  # Listar categorias principais
  cat_principais = [
      d
      for d in os.listdir(UPLOAD_DIR)
      if os.path.isdir(os.path.join(UPLOAD_DIR, d))
  ]

  if not cat_principais:
    st.info("Ainda não há categorias cadastradas. Vá na aba 'Enviar e Gerenciar'.")
  else:
    # Filtro de Categoria Principal
    filtro_principal = st.selectbox(
        "Filtrar Categoria Principal", ["Todas"] + cat_principais, key="filtro_princ"
    )

    cats_a_mostrar = (
        cat_principais if filtro_principal == "Todas" else [filtro_principal]
    )

    for princ in cats_a_mostrar:
      pasta_princ = os.path.join(UPLOAD_DIR, princ)
      subcats = [
          d
          for d in os.listdir(pasta_princ)
          if os.path.isdir(os.path.join(pasta_princ, d))
      ]

      st.markdown(f"## 📁 Categoria: {princ}")

      if not subcats:
        st.write("Nenhuma subcategoria nesta categoria principal.")
        st.divider()
        continue

      # Filtro de Subcategoria opcional para visualização
      sub_filtro = st.selectbox(
          f"Filtrar Subcategoria em '{princ}'",
          ["Todas"] + subcats,
          key=f"filtro_sub_{princ}",
      )
      subs_a_mostrar = subcats if sub_filtro == "Todas" else [sub_filtro]

      for sub in subs_a_mostrar:
        pasta_sub = os.path.join(pasta_princ, sub)
        fotos = [
            f
            for f in os.listdir(pasta_sub)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        st.markdown(f"#### 🏷️ Subcategoria: {sub}")

        if not fotos:
          st.write("Nenhuma foto cadastrada nesta subcategoria.")
        else:
          cols = st.columns(3)
          for idx, foto in enumerate(fotos):
            with cols[idx % 3]:
              with st.container(border=True):
                caminho_img = os.path.join(pasta_sub, foto)
                st.image(caminho_img, use_column_width=True)
                st.caption(foto)
                if st.button(
                    "Excluir Foto", key=f"del_foto_{princ}_{sub}_{foto}"
                ):
                  os.remove(caminho_img)
                  st.success(f"Foto {foto} removida!")
                  st.rerun()
        st.write("")
      st.divider()

# ==========================================
# ABA 2: UPLOAD E GERENCIAMENTO
# ==========================================
with aba_upload:
  cat_principais_existentes = [
      d
      for d in os.listdir(UPLOAD_DIR)
      if os.path.isdir(os.path.join(UPLOAD_DIR, d))
  ]

  st.subheader("📤 Enviar Novas Fotos com Subcategoria")

  # 1. Definir Categoria Principal
  tipo_princ = st.radio(
      "Categoria Principal:",
      ["Existente", "Criar Nova Categoria Principal"],
      key="radio_princ",
  )
  cat_principal_alvo = ""

  if tipo_princ == "Existente":
    if not cat_principais_existentes:
      st.warning("Crie uma nova categoria principal primeiro.")
    else:
      cat_principal_alvo = st.selectbox(
          "Selecione a Categoria Principal",
          cat_principais_existentes,
          key="sel_princ_existente",
      )
  else:
    nova_princ = st.text_input(
        "Nome da Nova Categoria Principal (Ex: Chaveiros):", key="input_nova_princ"
    )
    if nova_princ:
      cat_principal_alvo = nova_princ.strip()

  # Se já temos uma categoria principal definida, gerenciamos a Subcategoria
  if cat_principal_alvo:
    pasta_princ_temp = os.path.join(UPLOAD_DIR, cat_principal_alvo)
    os.makedirs(pasta_princ_temp, exist_ok=True)

    subcats_existentes = [
        d
        for d in os.listdir(pasta_princ_temp)
        if os.path.isdir(os.path.join(pasta_princ_temp, d))
    ]

    tipo_sub = st.radio(
        "Subcategoria:",
        ["Existente", "Criar Nova Subcategoria"],
        key="radio_sub",
    )
    subcat_alvo = ""

    if tipo_sub == "Existente":
      if not subcats_existentes:
        st.warning(
            "Não há subcategorias nesta categoria. Escolha 'Criar Nova"
            " Subcategoria'."
        )
      else:
        subcat_alvo = st.selectbox(
            "Selecione a Subcategoria",
            subcats_existentes,
            key="sel_sub_existente",
        )
    else:
      nova_sub = st.text_input(
          "Nome da Nova Subcategoria (Ex: Esportivos):", key="input_nova_sub"
      )
      if nova_sub:
        subcat_alvo = nova_sub.strip()

    # Se a subcategoria estiver definida, liberamos o Upload
    if subcat_alvo:
      st.info(
          f"Destino atual: **{cat_principal_alvo}** ➔ **{subcat_alvo}**"
      )
      uploaded_files = st.file_uploader(
          "Escolha as imagens",
          type=["png", "jpg", "jpeg"],
          accept_multiple_files=True,
          key="uploader_fotos",
      )

      if uploaded_files and st.button("Salvar Fotos no Catálogo"):
        pasta_destino = os.path.join(UPLOAD_DIR, cat_principal_alvo, subcat_alvo)
        os.makedirs(pasta_destino, exist_ok=True)

        for arquivo in uploaded_files:
          caminho = os.path.join(pasta_destino, arquivo.name)
          with open(caminho, "wb") as f:
            f.write(arquivo.getbuffer())

        st.success(
            f"{len(uploaded_files)} foto(s) salva(s) em"
            f" '{cat_principal_alvo} / {subcat_alvo}'!"
        )
        st.rerun()

  st.divider()

  # Seção para Excluir Categoria/Subcategoria
  st.subheader("🗑️ Gerenciar / Excluir Estrutura")
  if not cat_principais_existentes:
    st.info("Não há estruturas para gerenciar.")
  else:
    cat_del_princ = st.selectbox(
        "Categoria Principal para excluir/gerenciar",
        cat_principais_existentes,
        key="del_princ_sel",
    )
    pasta_del_princ = os.path.join(UPLOAD_DIR, cat_del_princ)
    subcats_para_del = [
        d
        for d in os.listdir(pasta_del_princ)
        if os.path.isdir(os.path.join(pasta_del_princ, d))
    ]

    opcao_exclusao = st.radio(
        "O que deseja excluir?",
        ["Apenas uma Subcategoria específica", "Categoria Principal Inteira"],
        key="radio_tipo_del",
    )

    if opcao_exclusao == "Apenas uma Subcategoria específica":
      if not subcats_para_del:
        st.warning("Esta categoria principal não possui subcategorias.")
      else:
        sub_para_excluir = st.selectbox(
            "Selecione a Subcategoria", subcats_para_del, key="sub_del_sel"
        )
        confirma_sub = st.checkbox(
            f"Confirmo excluir a subcategoria '{sub_para_excluir}' e suas"
            " fotos."
        )

        if st.button("Excluir Subcategoria", type="primary"):
          if confirma_sub:
            pasta_sub_del = os.path.join(pasta_del_princ, sub_para_excluir)
            for arq in os.listdir(pasta_sub_del):
              c_arq = os.path.join(pasta_sub_del, arq)
              if os.path.isfile(c_arq):
                os.remove(c_arq)
            os.rmdir(pasta_sub_del)
            st.success(f"Subcategoria '{sub_para_excluir}' excluída!")
            st.rerun()
          else:
            st.warning("Marque a caixa de confirmação.")
    else:
      confirma_princ = st.checkbox(
          f"Confirmo excluir a Categoria Principal '{cat_del_princ}' INTEIRA"
          " (incluindo todas as subcategorias e fotos)."
      )
      if st.button("Excluir Categoria Principal", type="primary"):
        if confirma_princ:
          # Percorre e deleta tudo dentro recursivamente
          import shutil

          shutil.rmtree(pasta_del_princ)
          st.success(
              f"Categoria Principal '{cat_del_princ}' removida com sucesso!"
          )
          st.rerun()
        else:
          st.warning("Marque a caixa de confirmação.")