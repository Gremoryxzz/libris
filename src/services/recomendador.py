from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------------------------------------------
# Utilitário: juntar campos importantes do livro em um texto só
# -------------------------------------------------------------
def preparar_texto(livro):
    info = livro.get("volumeInfo", {})

    titulo = info.get("title", "")
    categorias = " ".join(info.get("categories", []))
    autores = " ".join(info.get("authors", []))
    descricao = info.get("description", "")

    texto = f"{titulo} {categorias} {autores} {descricao}"
    return texto.lower()


# -------------------------------------------------------------
# RECOMENDAÇÃO POR CONTEÚDO (TF-IDF + Cosseno)
# -------------------------------------------------------------
def recomendar_conteudo(livro_base, lista_livros):

    # Segurança
    if not lista_livros or not livro_base:
        return []

    # ---------------------------------------------------------
    # Garante que o livro-base está dentro da lista
    # ---------------------------------------------------------
    if livro_base not in lista_livros:
        lista_livros = [livro_base] + lista_livros

    # O livro-base SEMPRE será índice 0
    textos = [preparar_texto(l) for l in lista_livros]

    vectorizer = TfidfVectorizer(stop_words="english")
    matriz = vectorizer.fit_transform(textos)

    idx = 0
    similares = cosine_similarity(matriz[idx], matriz).flatten()

    # Ordena pelos mais similares, ignorando o próprio livro
    indices = [i for i in similares.argsort()[::-1] if i != idx]

    # Pega top-5
    indices = indices[:5]

    return [lista_livros[i] for i in indices]


# -------------------------------------------------------------
# RECOMENDAÇÃO BASEADA EM FAVORITOS (conteúdo também)
# -------------------------------------------------------------
def recomendar_por_favoritos(favoritos, lista_livros):

    if not favoritos or not lista_livros:
        return []

    recomendacoes = []

    # Para cada favorito, recomenda livros parecidos
    for fav in favoritos[:5]:  # limita para evitar custo alto
        recs = recomendar_conteudo(fav, lista_livros)
        recomendacoes.extend(recs)

    # Remove duplicatas mantendo ordem
    final = []
    ids = set()
    for r in recomendacoes:
        book_id = r.get("id")
        if book_id not in ids:
            ids.add(book_id)
            final.append(r)

    return final[:5]


# -------------------------------------------------------------
# MODELO HÍBRIDO (livro atual + favoritos)
# -------------------------------------------------------------
def recomendar_hibrido(livro_base, lista_livros, favoritos):

    if not lista_livros:
        return []

    # 1) Conteúdo baseado no livro atual
    conteudo = recomendar_conteudo(livro_base, lista_livros)

    # 2) Conteúdo baseado nos favoritos do usuário
    if favoritos:
        favs = recomendar_por_favoritos(favoritos, lista_livros)
    else:
        favs = []

    # Junta preservando ordem + remove duplicatas
    combinado = conteudo + favs

    final = []
    ids = set()

    for book in combinado:
        book_id = book.get("id")
        if book_id not in ids:
            ids.add(book_id)
            final.append(book)

    return final[:5]
