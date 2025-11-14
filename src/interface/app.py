# src/interface/app.py
import streamlit as st
import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Imports do projeto
from src.api.google_books import buscar_livros
from src.interface.login import tela_login, criar_conta
from src.interface.mongo import pre_cadastro, is_db_available

# Configura a página
st.set_page_config(page_title="📘 Libris", layout="centered")

# Session state defaults
if "logado" not in st.session_state:
    st.session_state.logado = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "livro_selecionado" not in st.session_state:
    st.session_state.livro_selecionado = None

# Pré-cadastro
if is_db_available():
    pre_cadastro()
else:
    st.warning("⚠️ Banco offline. Usando fallback em memória.")

# Recomendador de livros
def tela_recomendador():
    st.sidebar.title(f"👋 Olá, {st.session_state.usuario}")
    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.pagina = "login"
        st.session_state.livro_selecionado = None
        st.rerun()

    st.title("📘 Libris – Recomendador de Livros")

    if st.session_state.livro_selecionado is None:
        query = st.text_input("Digite um livro que você gosta:")
        if query:
            resultados = buscar_livros(query)
            for idx, item in enumerate(resultados.get("items", [])[:10]):
                info = item.get("volumeInfo", {})
                titulo = info.get("title", "Sem título")
                autores = ", ".join(info.get("authors", ["Desconhecido"]))
                imagem = info.get("imageLinks", {}).get("thumbnail", None)
                descricao = info.get("description", "Sem descrição disponível.")[:150] + "..."

                with st.container():
                    cols = st.columns([1, 4])
                    with cols[0]:
                        if imagem and imagem.startswith("http"):
                            st.image(imagem, width=100)
                        else:
                            st.image("https://via.placeholder.com/120x180?text=Sem+Capa", width=100)
                    with cols[1]:
                        st.markdown(f"### {titulo}")
                        st.markdown(f"**Autor(es):** {autores}")
                        st.markdown(f"_{descricao}_")
                        if st.button(f"📖 Ver mais sobre '{titulo}'", key=f"btn_{idx}"):
                            st.session_state.livro_selecionado = item
                            st.rerun()
    else:
        livro = st.session_state.livro_selecionado
        info = livro["volumeInfo"]
        titulo = info.get("title", "Sem título")
        autores = ", ".join(info.get("authors", ["Desconhecido"]))
        imagem = info.get("imageLinks", {}).get("thumbnail", None)

        st.markdown(f"## {titulo}")
        if imagem and imagem.startswith("http"):
            st.image(imagem, width=150)
        else:
            st.image("https://via.placeholder.com/150x220?text=Sem+Capa", width=150)
        st.write(f"**Autor(es):** {autores}")
        st.write(f"**Ano de publicação:** {info.get('publishedDate', 'Desconhecido')}")
        st.write(f"**Gênero:** {', '.join(info.get('categories', ['Não informado']))}")
        st.write(f"**Avaliação média:** {info.get('averageRating', 'Sem avaliação')}")
        st.markdown("### 📖 Sinopse:")
        st.write(info.get("description", "Sem sinopse disponível."))

        if st.button("🔙 Voltar"):
            st.session_state.livro_selecionado = None
            st.rerun()

# -----------------------------
# Fluxo principal
# -----------------------------
if st.session_state.logado:
    # Usuário logado → mostra recomendador
    tela_recomendador()
else:
    # Usuário não logado → mostra menu lateral de Login/Criar Conta
    menu = ["Login", "Criar Conta"]
    pagina_escolhida = st.sidebar.selectbox("Menu", menu)

    if pagina_escolhida == "Login":
        tela_login()
    elif pagina_escolhida == "Criar Conta":
        criar_conta()
