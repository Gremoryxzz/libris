import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random


# ---------------------------
# UTILITÁRIOS
# ---------------------------

def extrair_texto(livro):
    """Extrai texto relevante do JSON do Google Books."""
    info = livro.get("volumeInfo", {})

    titulo = info.get("title", "")
    autores = " ".join(info.get("authors", []))
    categorias = " ".join(info.get("categories", []))
    descricao = info.get("description", "")
    ano = info.get("publishedDate", "")

    texto = f"{titulo} {autores} {categorias} {descricao} {ano}"
    return texto


# ---------------------------
# CONSULTA GOOGLE
# ---------------------------

def buscar_livros_google(query, max_results=20):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"

    response = requests.get(url)
    data = response.json()

    if "items" not in data:
        return []

    return data["items"]


# ---------------------------
# RECOMENDAÇÃO PRINCIPAL
# ---------------------------

def recomendar_por_favoritos(usuario, db_favoritos, qtd=10):
    """
    Gera recomendações automáticas baseadas nos favoritos do usuário.
    - usuario: string
    - db_favoritos: dicionário vindo do fake-mongo
    - qtd: quantidade de recomendações (5–10)
    """

    if usuario not in db_favoritos or len(db_favoritos[usuario]) == 0:
        return []  # Sem favoritos, sem recomendação

    favoritos = db_favoritos[usuario]

    # ---------------------------
    # 1. Montar TF-IDF dos favoritos
    # ---------------------------
    textos_favoritos = [extrair_texto(l) for l in favoritos]

    vectorizer = TfidfVectorizer(stop_words="english")
    matriz_favoritos = vectorizer.fit_transform(textos_favoritos)

    # ---------------------------
    # 2. Escolher um livro favorito representativo
    # ---------------------------
    livro_base = random.choice(favoritos)
    texto_base = extrair_texto(livro_base)

    # ---------------------------
    # 3. Buscar candidatos no Google Books
    #    → usa título / categoria / autor do favorito como query
    # ---------------------------

    info = livro_base.get("volumeInfo", {})
    titulo = info.get("title", "")
    categoria = info.get("categories", [""])[0]
    autor = " ".join(info.get("authors", []))

    query = f"{titulo} {categoria} {autor}"

    candidatos = buscar_livros_google(query, max_results=20)

    if not candidatos:
        return []

    # ---------------------------
    # 4. Vetorizar candidatos
    # ---------------------------
    textos_candidatos = [extrair_texto(c) for c in candidatos]
    matriz_candidatos = vectorizer.transform(textos_candidatos)

    # ---------------------------
    # 5. Similaridade
    # ---------------------------
    base_vetor = vectorizer.transform([texto_base])

    scores = cosine_similarity(base_vetor, matriz_candidatos).flatten()

    # index + score
    ordenado = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)

    # ---------------------------
    # 6. Filtrar 5–10 melhores, ignorar livros repetidos do favorito
    # ---------------------------
    recomendacoes = []

    for idx, score in ordenado:
        candidato = candidatos[idx]

        # evita recomendar favoritos novamente
        ids_favoritos = {f["id"] for f in favoritos}
        if candidato["id"] in ids_favoritos:
            continue

        recomendacoes.append(candidato)

        if len(recomendacoes) >= qtd:
            break

    # Se não conseguir qtd, retorna o que tiver
    return recomendacoes
