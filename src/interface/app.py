import streamlit as st
import sys
import os
import matplotlib.pyplot as plt
from collections import Counter

# =============================
# CONFIGURAÇÃO DO PATH DO PROJETO
# =============================
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# =============================
# IMPORTS DO PROJETO
# =============================
from src.api.google_books import buscar_livros
from src.interface.login import tela_login, criar_conta
from src.interface.mongo import pre_cadastro, is_db_available

st.set_page_config(page_title="📘 Libris", layout="centered")

# =============================
# SESSION STATE DEFAULTS
# =============================
defaults = {
    "logado": False,
    "pagina": "login",
    "usuario": "",
    "livro_selecionado": None,
    "favoritos": [],
    "notas": {},
    "mostrar_grafico": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =============================
# PRÉ-CADASTRO
# =============================
if is_db_available():
    pre_cadastro()
else:
    st.warning("⚠️ Banco offline. Usando fallback em memória.")


# =============================
# GERAÇÃO DE GRÁFICO
# =============================
def grafico_livros_por_ano(resultados, termo_busca: str):
    anos = []
    for item in resultados.get("items", []):
        info = item.get("volumeInfo", {})
        if "publishedDate" in info:
            ano = info["publishedDate"].split("-")[0]
            anos.append(ano)

    if anos:
        contagem = Counter(anos)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(contagem.keys(), contagem.values())
        ax.set_title(f"Distribuição de livros sobre '{termo_busca}' por ano")
        ax.set_xlabel("Ano de publicação")
        ax.set_ylabel("Quantidade de livros")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("Nenhum dado de ano de publicação disponível para gerar gráfico.")


# =============================
# TELA RECOMENDADOR
# =============================
def tela_recomendador():
    st.sidebar.title(f"👋 Olá, {st.session_state.usuario}")

    if st.sidebar.button("Sair"):
        for key in defaults:
            st.session_state[key] = defaults[key]
        st.rerun()

    st.sidebar.markdown("### Navegação")
    if st.sidebar.button("❤️ Favoritos"):
        st.session_state.pagina = "favoritos"
        st.rerun()

    st.title("📘 Libris – Recomendador de Livros")

    # Se nenhum livro foi selecionado ainda
    if st.session_state.livro_selecionado is None:

        if st.button("🔍 Análise por título"):
            st.session_state.pagina = "analise"
            st.rerun()

        query = st.text_input("Digite um livro que você gosta:")
        if query:
            resultados = buscar_livros(query)

            if not resultados or "items" not in resultados:
                st.warning("Nenhum resultado encontrado.")
                return

            for idx, item in enumerate(resultados.get("items", [])[:10]):
                info = item.get("volumeInfo", {})
                titulo = info.get("title", "Sem título")
                autores = ", ".join(info.get("authors", ["Desconhecido"]))
                imagem = info.get("imageLinks", {}).get("thumbnail")
                descricao = info.get("description", "Sem descrição.")[:150] + "..."

                with st.container():
                    cols = st.columns([1, 4])
                    with cols[0]:
                        st.image(imagem or "https://via.placeholder.com/120x180?text=Sem+Capa", width=100)

                    with cols[1]:
                        st.markdown(f"### {titulo}")
                        st.markdown(f"**Autor(es):** {autores}")
                        st.write(descricao)

                        if st.button(f"📖 Ver mais sobre {titulo}", key=f"btn_{idx}"):
                            st.session_state.livro_selecionado = item
                            st.rerun()

    else:
        livro = st.session_state.livro_selecionado
        info = livro["volumeInfo"]

        titulo = info.get("title", "Sem título")
        autores = info.get("authors", ["Desconhecido"])
        categorias = info.get("categories", ["Não informado"])
        imagem = info.get("imageLinks", {}).get("thumbnail")

        st.markdown(f"## {titulo}")

        cols = st.columns([1, 3])

        # ---------------------------
        # COLUNA DA ESQUERDA
        # ---------------------------
        with cols[0]:
            st.image(imagem or "https://via.placeholder.com/150x220?text=Sem+Capa", width=150)

            # FAVORITAR
            if st.button("❤️ Favoritar"):
                st.session_state.favoritos.append(livro)
                st.success("Salvo nos favoritos!")

            # NOTA
            st.markdown("### ⭐ Sua avaliação")
            nota_atual = st.session_state.notas.get(titulo, 0)
            nota = st.slider("Nota:", 0, 5, nota_atual)

            if st.button("Salvar nota"):
                st.session_state.notas[titulo] = nota
                st.success("Nota salva!")

        # ---------------------------
        # COLUNA DA DIREITA
        # ---------------------------
        with cols[1]:
            st.write(f"**Autor(es):** {', '.join(autores)}")
            st.write(f"**Ano:** {info.get('publishedDate', 'Desconhecido')}")
            st.write(f"**Gênero:** {', '.join(categorias)}")
            st.write(f"**Avaliação média:** {info.get('averageRating', 'Sem dados')}")

            st.markdown("### 📖 Sinopse")
            st.write(info.get("description", "Sem sinopse disponível."))

        # ---------------------------
        # RECOMENDAÇÕES
        # ---------------------------
        st.markdown("## 🔮 Recomendações semelhantes")

        try:
            recomendacoes = []

            if autores[0] != "Desconhecido":
                recomendacoes += buscar_livros(autores[0]).get("items", [])

            if categorias[0] != "Não informado":
                recomendacoes += buscar_livros(categorias[0]).get("items", [])

            recomendacoes = [
                r for r in recomendacoes
                if r["volumeInfo"].get("title") != titulo
            ]

            for r in recomendacoes[:5]:
                r_info = r["volumeInfo"]
                nome = r_info.get("title", "Sem título")
                img = r_info.get("imageLinks", {}).get("thumbnail")

                rec_cols = st.columns([1, 4])
                with rec_cols[0]:
                    st.image(img or "https://via.placeholder.com/100x150?text=Sem+Capa", width=80)

                with rec_cols[1]:
                    st.markdown(f"### {nome}")
                    if st.button(f"📖 Abrir {nome}", key=f"open_{nome}"):
                        st.session_state.livro_selecionado = r
                        st.rerun()

        except:
            st.warning("Não foi possível gerar recomendações agora.")

        # ---------------------------
        # GRÁFICO
        # ---------------------------
        if st.button("📊 Ver/Ocultar gráfico"):
            st.session_state.mostrar_grafico = not st.session_state.mostrar_grafico
            st.rerun()

        if st.session_state.mostrar_grafico:
            grafico_livros_por_ano({"items": [livro]}, titulo)

        if st.button("🔙 Voltar"):
            st.session_state.livro_selecionado = None
            st.session_state.mostrar_grafico = False
            st.rerun()


# =============================
# TELA DE ANÁLISE
# =============================
def tela_analise():
    st.title("📊 Análise por título")

    termo = st.text_input("Título:")
    if termo:
        resultados = buscar_livros(termo)
        if "items" in resultados:
            grafico_livros_por_ano(resultados, termo)

    if st.button("🔙 Voltar"):
        st.session_state.pagina = "recomendador"
        st.rerun()


# =============================
# TELA DE FAVORITOS
# =============================
def tela_favoritos():
    st.title("❤️ Meus Favoritos")

    if not st.session_state.favoritos:
        st.info("Nenhum favorito ainda.")
    else:
        for idx, livro in enumerate(st.session_state.favoritos):
            info = livro["volumeInfo"]
            titulo = info.get("title", "Sem título")
            img = info.get("imageLinks", {}).get("thumbnail")

            cols = st.columns([1, 4, 1])
            with cols[0]:
                st.image(img or "https://via.placeholder.com/120x180?text=Sem+Capa", width=100)

            with cols[1]:
                st.markdown(f"### {titulo}")
                if st.button(f"📖 Abrir {titulo}", key=f"fav_{idx}"):
                    st.session_state.livro_selecionado = livro
                    st.session_state.pagina = "recomendador"
                    st.rerun()

            with cols[2]:
                if st.button("❌ Remover", key=f"rem_{idx}"):
                    st.session_state.favoritos.pop(idx)
                    st.rerun()

    if st.button("🔙 Voltar"):
        st.session_state.pagina = "recomendador"
        st.rerun()


# =============================
# CONTROLE DE PÁGINAS
# =============================
if st.session_state.logado:

    if st.session_state.pagina == "recomendador":
        tela_recomendador()

    elif st.session_state.pagina == "analise":
        tela_analise()

    elif st.session_state.pagina == "favoritos":
        tela_favoritos()

else:
    opc = st.sidebar.selectbox("Menu", ["Login", "Criar Conta"])

    if opc == "Login":
        tela_login()
    else:
        criar_conta()
