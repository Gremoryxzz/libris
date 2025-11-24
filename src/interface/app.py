# src/interface/app.py
import streamlit as st
import sys
import os
import textwrap
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import time
from typing import List, Tuple

# =============================
# CONFIGURAÇÃO DO PATH DO PROJETO
# =============================
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# =============================
# IMPORTS DO PROJETO
# =============================
from src.services.recomendador_sklearn import recomendar_por_favoritos
from src.services.google_books import buscar_livros
from src.interface.login import tela_login, criar_conta
from src.interface.mongo import (
    pre_cadastro,
    is_db_available,
    adicionar_favorito,
    listar_favoritos,
    remover_favorito,
    salvar_nota,
    pegar_notas,
    pegar_nota,
)

# =============================
# CONFIG STREAMLIT
# =============================
st.set_page_config(page_title="📘 Libris", layout="wide")

# =============================
# CSS — estilo Amazon-like (clean, foco na capa)
# =============================
st.markdown(
    """
    <style>
    /* Container clean */
    .book-card {
      display: flex;
      gap: 16px;
      padding: 12px;
      border-radius: 8px;
      background: linear-gradient(180deg, #ffffff, #fbfbfb);
      box-shadow: 0 6px 18px rgba(0,0,0,0.06);
      border: 1px solid rgba(0,0,0,0.04);
      margin-bottom: 10px;
      align-items: center;
    }
    .book-card .cover {
      width: 120px;
      min-width: 120px;
      height: 170px;
      overflow: hidden;
      border-radius: 4px;
      background: #f0f0f0;
    }
    .book-card .meta {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .book-card h3 {
      margin: 0;
      font-size: 18px;
      color: #111827;
    }
    .book-card .sub {
      color: #6b7280;
      font-size: 13px;
    }
    .book-card .desc {
      color: #374151;
      font-size: 14px;
      margin-top: 6px;
    }
    .book-actions { display:flex; gap:8px; margin-top:8px; }
    .btn-prim {
      background: linear-gradient(90deg,#ff9900,#ff7a00);
      color: #fff !important;
      padding: 8px 12px;
      border-radius: 6px;
      border: none;
    }
    .btn-sec {
      background: transparent;
      color: #111827;
      padding: 8px 10px;
      border-radius: 6px;
      border: 1px solid rgba(0,0,0,0.08);
    }
    .small-muted { color: #6b7280; font-size: 13px; }
    footer.back-footer {
      margin-top: 18px;
      display: flex;
      justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    "db_loaded": False,
    # pagination & cache
    "recom_auto_page": 1,
    "recom_auto_per_page": 8,
    "recom_auto_max": 20,
    "recom_auto_cache": None,
    "search_page": 1,
    "search_per_page": 8,
    "fav_page": 1,
    "fav_per_page": 8,
    "similares_page": 1,
    "similares_per_page": 6,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =============================
# PRÉ-CADASTRO
# =============================
if is_db_available():
    pre_cadastro()
else:
    st.warning("⚠️ Banco offline. Usando fallback em memória.")

# =============================
# HELPERS
# =============================
def short_text(text: str, max_chars: int = 300) -> Tuple[str, bool]:
    if not text:
        return "", False
    if len(text) <= max_chars:
        return text, False
    short = textwrap.shorten(text, width=max_chars, placeholder="...")
    return short, True

def paginate_list(items: List, page: int, per_page: int) -> Tuple[List, int]:
    total = len(items)
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total_pages

def extrair_ano(data_str):
    if not data_str:
        return None
    try:
        return int(str(data_str)[:4])
    except:
        return None

def render_back_footer():
    """Exibe botão de voltar no rodapé (padrão para todas as telas)."""
    st.markdown('<footer class="back-footer">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🔙 Voltar"):
            # comportamento padrão: voltar para recomendador e limpar seleção de livro
            st.session_state.livro_selecionado = None
            st.session_state.pagina = "recomendador"
            st.rerun()
    st.markdown('</footer>', unsafe_allow_html=True)

# =============================
# RENDER CARD — Amazon-like vertical (foco na capa)
# =============================
def render_book_card(item: dict, key_prefix: str, show_expand: bool = True, show_actions: bool = True):
    info = item.get("volumeInfo", {})
    title = info.get("title", "Sem título")
    authors = ", ".join(info.get("authors", ["Desconhecido"]))
    year = info.get("publishedDate", "—")
    rating = info.get("averageRating", None)
    pages = info.get("pageCount", "—")
    categories = ", ".join(info.get("categories", ["—"]))
    img = info.get("imageLinks", {}).get("thumbnail")

    desc_full = info.get("description", "")
    desc_short, truncated = short_text(desc_full, max_chars=280)

    # card container
    st.markdown('<div class="book-card">', unsafe_allow_html=True)
    cols = st.columns([0.7, 3])
    with cols[0]:
        if img:
            st.markdown(f'<div class="cover"><img src="{img}" style="width:120px;height:170px;object-fit:cover;border-radius:4px"/></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cover"><img src="https://via.placeholder.com/120x170?text=Sem+Capa" style="width:120px;height:170px;object-fit:cover;border-radius:4px"/></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='meta'><h3>{title}</h3>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub'>{authors} • {year}</div>", unsafe_allow_html=True)
        if desc_short:
            st.markdown(f"<div class='desc'>{desc_short}</div>", unsafe_allow_html=True)
        if truncated and show_expand:
            with st.expander("Ver descrição completa"):
                st.write(desc_full)
        meta_line = f"<div class='small-muted'>📄 {pages} páginas"
        if rating:
            meta_line += f"  •  ⭐ {rating}"
        meta_line += f"  •  {categories}</div>"
        st.markdown(meta_line, unsafe_allow_html=True)

        if show_actions:
            a_col1, a_col2, a_col3 = st.columns([1,1,1])
            with a_col1:
                if st.button("📖 Detalhes", key=f"{key_prefix}_open"):
                    st.session_state.livro_selecionado = item
                    st.session_state.pagina = "recomendador"
                    st.rerun()
            with a_col2:
                if st.button("❤️ Favoritar", key=f"{key_prefix}_fav"):
                    user = st.session_state.usuario
                    if not user:
                        st.warning("⚠️ Faça login para favoritar.")
                    else:
                        ok = adicionar_favorito(user, item)
                        if ok:
                            st.session_state.favoritos = listar_favoritos(user)
                            st.session_state.recom_auto_cache = None
                            st.success("Adicionado aos favoritos!")
                        else:
                            st.info("Já está nos favoritos.")
            with a_col3:
                if st.button("🔗 Mais", key=f"{key_prefix}_more"):
                    # abrir link do livro (se existir)
                    link = info.get("infoLink") or info.get("previewLink")
                    if link:
                        st.write(f"[Abrir na Google Books]({link})")
    st.markdown('</div>', unsafe_allow_html=True)

# =============================
# DB helper
# =============================
def carregar_dados_usuario_do_db():
    if not st.session_state.logado or st.session_state.db_loaded:
        return
    usuario = st.session_state.usuario
    if not usuario:
        return
    favs = listar_favoritos(usuario)
    notas = pegar_notas(usuario)
    st.session_state.favoritos = favs or []
    st.session_state.notas = notas or {}
    st.session_state.db_loaded = True

# =============================
# DASHBOARD
# =============================
def tela_dashboard():
    st.title("📊 Dashboard de Análises")
    tipo_busca = st.selectbox("Buscar livros por:", ["Título", "Autor", "Gênero", "Ano"])
    entrada = st.text_input(f"Digite o {tipo_busca.lower()}:")
    if not entrada:
        st.info("Digite algo para iniciar a análise...")
        render_back_footer()
        return
    with st.spinner("Buscando dados..."):
        dados = buscar_livros(entrada)
    if not dados or "items" not in dados:
        st.warning("Nenhum resultado encontrado.")
        render_back_footer()
        return

    items = dados["items"]
    rows = []
    for it in items:
        info = it.get("volumeInfo", {})
        rows.append({
            "titulo": info.get("title"),
            "categoria": info.get("categories", ["Desconhecido"])[0],
            "ano": extrair_ano(info.get("publishedDate")),
            "rating": info.get("averageRating", 0) or 0,
            "paginas": info.get("pageCount", 0) or 0
        })
    df = pd.DataFrame(rows)

    sns.set_theme(style="whitegrid")
    c1, c2 = st.columns([1,1])
    with c1:
        st.subheader("Top categorias")
        fig1, ax1 = plt.subplots(figsize=(6,4))
        df["categoria"].value_counts().nlargest(8).plot(kind="barh", ax=ax1, color="#ff9900")
        ax1.invert_yaxis()
        st.pyplot(fig1)
    with c2:
        st.subheader("Publicações por ano")
        fig2, ax2 = plt.subplots(figsize=(6,4))
        sns.histplot(df["ano"].dropna(), bins=12, kde=True, ax=ax2)
        st.pyplot(fig2)
    st.subheader("Ratings vs Páginas")
    fig3, ax3 = plt.subplots(figsize=(10,4))
    sns.scatterplot(data=df, x="paginas", y="rating", hue="categoria", ax=ax3, legend=False)
    st.pyplot(fig3)
    render_back_footer()

# =============================
# RECOMENDADOR (BUSCA) — com paginação
# =============================
def tela_recomendador():
    st.sidebar.title(f"👋 Olá, {st.session_state.usuario}")
    if st.sidebar.button("Sair"):
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.rerun()
    st.sidebar.markdown("### Navegação")
    if st.sidebar.button("❤️ Favoritos"):
        st.session_state.pagina = "favoritos"
        st.rerun()
    if st.sidebar.button("📊 Dashboard"):
        st.session_state.pagina = "dashboard"
        st.rerun()
    if st.sidebar.button("🔮 Recomendações"):
        st.session_state.pagina = "recom_auto"
        st.rerun()

    st.title("📘 Libris")
    carregar_dados_usuario_do_db()

    col_search, col_pp = st.columns([4,1])
    with col_search:
        query = st.text_input("Pesquisar livros (Google Books):", key="main_search")
    with col_pp:
        per_page = st.selectbox("Por página:", options=[4,6,8,10], index=2, key="search_pp")
    st.session_state.search_per_page = per_page

    if not query:
        st.info("Digite um termo para pesquisar.")

        return

    # cache per query
    cache_key = ("search", query)
    cache = st.session_state.get("search_cache", {})
    if cache.get("key") == cache_key:
        results = cache.get("items", [])
    else:
        with st.spinner("Buscando Google Books..."):
            data = buscar_livros(query)
            results = data.get("items", []) if data and "items" in data else []
            st.session_state["search_cache"] = {"key": cache_key, "items": results}
            st.session_state.search_page = 1

    page = st.session_state.get("search_page", 1)
    per_page = st.session_state.search_per_page
    subset, total_pages = paginate_list(results, page, per_page)
    st.markdown(f"**Página {page} / {total_pages} — {len(results)} resultados**")
    for idx, item in enumerate(subset):
        render_book_card(item, key_prefix=f"search_{page}_{idx}", show_actions=True)
    nav_col1, nav_col2, nav_col3 = st.columns([1,1,1])
    with nav_col1:
        if st.button("⬅️ Anterior", key="search_prev"):
            if page > 1:
                st.session_state.search_page = page - 1
                st.rerun()
    with nav_col3:
        if st.button("Próxima ➡️", key="search_next"):
            if page < total_pages:
                st.session_state.search_page = page + 1
                st.rerun()
    render_back_footer()

# =============================
# FAVORITOS — paginação
# =============================
def tela_favoritos():
    st.title("❤️ Meus Favoritos")
    carregar_dados_usuario_do_db()
    favs = listar_favoritos(st.session_state.usuario) if st.session_state.logado else []
    if not favs:
        st.info("Nenhum favorito ainda.")
        render_back_footer()
        return
    per_page = st.session_state.get("fav_per_page", 8)
    page = st.session_state.get("fav_page", 1)
    subset, total_pages = paginate_list(favs, page, per_page)
    st.markdown(f"**Página {page} / {total_pages} — {len(favs)} favoritos**")
    for idx, item in enumerate(subset):
        render_book_card(item, key_prefix=f"fav_{page}_{idx}", show_actions=False)

    nav1, nav2, nav3 = st.columns([1,1,1])
    with nav1:
        if st.button("⬅️ Anterior", key="fav_prev"):
            if page > 1:
                st.session_state.fav_page = page - 1
                st.rerun()
    with nav3:
        if st.button("Próxima ➡️", key="fav_next"):
            if page < total_pages:
                st.session_state.fav_page = page + 1
                st.rerun()
    render_back_footer()

# =============================
# RECOMENDAÇÕES AUTOMÁTICAS — paginada, cache
# =============================
def tela_recom_auto():
    st.title("🔮 Recomendações Automáticas")
    usuario = st.session_state.usuario
    if not usuario:
        st.info("Faça login para recomendações.")
        render_back_footer()
        return
    favoritos = listar_favoritos(usuario)
    if not favoritos:
        st.info("Adicione favoritos para receber recomendações.")
        render_back_footer()
        return
    with st.expander("Favoritos usados como base"):
        for fav in favoritos:
            info = fav.get("volumeInfo", {})
            st.write(f"• {info.get('title', 'Sem título')} — {', '.join(info.get('authors', []))}")

    # Removido o slider de número de recomendações
    # Definido o valor fixo de recomendações
    max_recs = 20  # Número fixo de recomendações

    # Remover a parte de selecionar quantos por página
    per_page = st.selectbox("Itens por página:", options=[4, 6, 8, 10], index=2, key="recom_pp")
    st.session_state.recom_auto_per_page = per_page
    st.session_state.recom_auto_max = max_recs

    cache = st.session_state.recom_auto_cache
    cache_key = (usuario, max_recs)  # Número fixo de recomendações
    need_fetch = True
    if cache and isinstance(cache, dict) and cache.get("key") == cache_key:
        recs = cache.get("recs", [])
        need_fetch = False
    if need_fetch:
        with st.spinner("Gerando recomendações (IA)..."):
            recs = recomendar_por_favoritos(usuario, {usuario: favoritos}, qtd=max_recs)
            st.session_state.recom_auto_cache = {"key": cache_key, "recs": recs}
            st.session_state.recom_auto_page = 1
    if not recs:
        st.warning("Sem recomendações.")
        render_back_footer()
        return
    page = st.session_state.get("recom_auto_page", 1)
    per_page = st.session_state.recom_auto_per_page
    subset, total_pages = paginate_list(recs, page, per_page)
    st.markdown(f"**Página {page} / {total_pages} — mostrando {len(subset)} de {len(recs)}**")
    for idx, item in enumerate(subset):
        render_book_card(item, key_prefix=f"recom_{page}_{idx}", show_actions=True)
    nav1, nav2, nav3 = st.columns([1, 1, 1])

    with nav1:
        if st.button("⬅️ Anterior", key="recom_prev"):
            if page > 1:
                st.session_state.recom_auto_page = page - 1
                st.rerun()

    with nav3:
        if st.button("Próxima ➡️", key="recom_next"):
            if page < total_pages:
                st.session_state.recom_auto_page = page + 1
                st.rerun()

    if st.button("🔄 Regenerar recomendações"):
        st.session_state.recom_auto_cache = None
        st.rerun()
    render_back_footer()

# =============================
# RECOMENDAÇÕES SEMELHANTES (quando livro aberto) — paginada
# =============================
def tela_recomendacoes_semelhantes(livro):
    st.title("🔎 Recomendações Semelhantes")
    info = livro.get("volumeInfo", {})
    st.markdown(f"### {info.get('title', 'Sem título')}")
    autores = info.get("authors", [])
    categorias = info.get("categories", [])
    candidatos = []
    if autores:
        for a in autores:
            candidatos += buscar_livros(a).get("items", []) or []
    if categorias:
        for c in categorias:
            candidatos += buscar_livros(c).get("items", []) or []
    vistos = set()
    limpos = []
    for it in candidatos:
        vid = it.get("id") or it.get("volumeInfo", {}).get("title", "")
        if vid not in vistos and it.get("volumeInfo", {}).get("title") != info.get("title"):
            limpos.append(it)
            vistos.add(vid)
    if not limpos:
        st.info("Nenhuma recomendação semelhante encontrada.")
        render_back_footer()
        return
    page = st.session_state.get("similares_page", 1)
    per_page = st.session_state.get("similares_per_page", 6)
    subset, total_pages = paginate_list(limpos, page, per_page)
    for idx, item in enumerate(subset):
        render_book_card(item, key_prefix=f"sim_{page}_{idx}", show_actions=True)
    nav1, nav2, nav3 = st.columns([1,1,1])
    with nav1:
        if st.button("⬅️ Anterior", key="sim_prev"):
            if page > 1:
                st.session_state.similares_page = page - 1
                st.rerun()
    with nav3:
        if st.button("Próxima ➡️", key="sim_next"):
            if page < total_pages:
                st.session_state.similares_page = page + 1
                st.rerun()
    render_back_footer()

# =============================
# RENDER BOOK DETAIL (central)
# =============================
def render_book_detail(livro):
    info = livro.get("volumeInfo", {})
    st.markdown(f"## {info.get('title', 'Sem título')}")
    cols = st.columns([1, 2])
    with cols[0]:
        img = info.get("imageLinks", {}).get("thumbnail")
        if img:
            st.image(img, width=200)
        else:
            st.image("https://via.placeholder.com/200x300?text=Sem+Capa", width=200)
    with cols[1]:
        st.write(f"**Autor(es):** {', '.join(info.get('authors', ['Desconhecido']))}")
        st.write(f"**Ano:** {info.get('publishedDate', '—')}")
        st.write(f"**Gênero:** {', '.join(info.get('categories', ['—']))}")
        st.write(f"**Rating médio:** {info.get('averageRating', '—')}")
        st.write(f"**Páginas:** {info.get('pageCount', '—')}")
    desc = info.get("description", "")
    if desc:
        with st.expander("Sinopse completa"):
            st.write(desc)
    # actions
    a1, a2, a3 = st.columns([1,1,1])
    with a1:
        if st.button("🔮 Recomendações semelhantes"):
            st.session_state.pagina = "semelhantes"
            st.rerun()
    with a2:
        if st.button("❤️ Favoritar este livro"):
            user = st.session_state.usuario
            if not user:
                st.warning("Faça login para favoritar.")
            else:
                ok = adicionar_favorito(user, livro)
                if ok:
                    st.session_state.favoritos = listar_favoritos(user)
                    st.session_state.recom_auto_cache = None
                    st.success("Favoritado!")
                else:
                    st.info("Já estava favoritado.")
    with a3:
        if st.button("🔙 Voltar (detalhes)"):
            st.session_state.livro_selecionado = None
            st.session_state.pagina = "recomendador"
            st.rerun()
    # footer back to main too
    render_back_footer()

# =============================
# MAIN ROUTING
# =============================
if st.session_state.logado:
    carregar_dados_usuario_do_db()
    # if a book is selected show detail else show pages
    if st.session_state.livro_selecionado:
        render_book_detail(st.session_state.livro_selecionado)
    else:
        if st.session_state.pagina == "recomendador":
            tela_recomendador()
        elif st.session_state.pagina == "favoritos":
            tela_favoritos()
        elif st.session_state.pagina == "dashboard":
            tela_dashboard()
        elif st.session_state.pagina == "recom_auto":
            tela_recom_auto()
        elif st.session_state.pagina == "semelhantes":
            # ensure livro selected
            if st.session_state.livro_selecionado:
                tela_recomendacoes_semelhantes(st.session_state.livro_selecionado)
            else:
                st.info("Selecione um livro para ver recomendações semelhantes.")
                render_back_footer()
else:
    opc = st.sidebar.selectbox("Menu", ["Login", "Criar Conta"])
    if opc == "Login":
        tela_login()
    else:
        criar_conta()
