import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def tela_dashboard():
    st.title("📊 Dashboard de Análises")
    st.write("Visualização simples, objetiva e profissional sobre os livros pesquisados.")

    st.divider()

    # --- Entrada de Pesquisa ---
    st.subheader("Pesquisa de Livros")
    termo = st.text_input("Digite o nome do livro para análise")

    if st.button("Buscar"):
        with st.spinner("Carregando dados..."):
            dados = buscar_livros(termo)

        if dados.empty:
            st.warning("Nenhum resultado encontrado.")
            return

        st.success(f"{len(dados)} livros encontrados.")

        st.divider()

        # --- Métricas Minimalistas ---
        c1, c2, c3 = st.columns(3)

        c1.metric("Total de Livros", len(dados))
        c2.metric("Ano Mais Comum", dados["ano"].mode().iloc[0])
        c3.metric("Autor Mais Frequente", dados["autor"].mode().iloc[0])

        st.divider()

        # --- 1. Gráfico: Publicações por Ano ---
        st.subheader("Publicações por Ano")
        fig, ax = plt.subplots()
        ax.hist(dados["ano"], bins=10)
        ax.set_xlabel("Ano")
        ax.set_ylabel("Quantidade")
        st.pyplot(fig)

        st.divider()

        # --- 2. Gráfico: Livros por Autor ---
        st.subheader("Livros por Autor")
        top_autores = dados["autor"].value_counts().head(10)

        fig2, ax2 = plt.subplots()
        ax2.bar(top_autores.index, top_autores.values)
        ax2.set_ylabel("Quantidade")
        ax2.set_xticklabels(top_autores.index, rotation=45, ha="right")
        st.pyplot(fig2)

        st.divider()

        # --- 3. Gráfico: Categorias (se existirem) ---
        if "categoria" in dados.columns and dados["categoria"].notna().sum() > 0:
            st.subheader("Categorias Principais")
            top_cat = dados["categoria"].value_counts().head(10)

            fig3, ax3 = plt.subplots()
            ax3.bar(top_cat.index, top_cat.values)
            ax3.set_ylabel("Quantidade")
            ax3.set_xticklabels(top_cat.index, rotation=45, ha="right")
            st.pyplot(fig3)


# ---------------------------------------------------------
# Função auxiliar que extrai dados importantes do Google Books
# ---------------------------------------------------------

def buscar_livros(termo):
    import requests

    url = f"https://www.googleapis.com/books/v1/volumes?q={termo}"
    r = requests.get(url)
    data = r.json()

    if "items" not in data:
        return pd.DataFrame()

    livros = []

    for item in data["items"]:
        info = item.get("volumeInfo", {})

        livros.append({
            "titulo": info.get("title", "Sem título"),
            "autor": (info.get("authors") or ["Desconhecido"])[0],
            "ano": extrair_ano(info.get("publishedDate")),
            "categoria": (info.get("categories") or ["Outros"])[0]
        })

    return pd.DataFrame(livros)


def extrair_ano(data_str):
    """
    publishedDate às vezes vem:
    - '2010-01-15'
    - '2010'
    - '2008-09'
    - None
    Aqui extraímos somente o ano.
    """
    if not data_str:
        return 0
    try:
        return int(data_str[:4])
    except:
        return 0
