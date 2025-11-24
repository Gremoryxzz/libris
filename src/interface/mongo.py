# src/interface/mongo.py
# Banco de dados simulado com interface parecida com MongoDB
# Não usa servidor externo e funciona 100% offline
# Persistência opcional (salvamento em JSON)

import json
import os

DB_FILE = "fake_mongo.json"

# Estrutura do banco em memória
db = {
    "usuarios": [],        # {usuario, senha, email}
    "favoritos": {},       # usuario -> [livros]
    "notas": {},           # usuario -> {titulo: nota}
}

# ===============================
# 🔄 Persistência Opcional (JSON)
# ===============================

def carregar_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                db["usuarios"] = data.get("usuarios", [])
                db["favoritos"] = data.get("favoritos", {})
                db["notas"] = data.get("notas", {})
        except:
            print("⚠ Erro ao carregar DB, usando memória limpa.")


def salvar_db():
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=4)
    except:
        print("⚠ Erro ao salvar DB.")


# Carrega banco ao iniciar
carregar_db()

# ===============================
# 🟦 Funções básicas
# ===============================

def is_db_available():
    """O banco simulado está sempre disponível."""
    return True


# ===============================
# 👤 Usuários
# ===============================

def pre_cadastro():
    """Cria um usuário padrão apenas uma vez."""
    if not any(u["usuario"] == "renan1227" for u in db["usuarios"]):
        db["usuarios"].append({
            "usuario": "renan1227",
            "senha": "123",
            "email": "renasin122"
        })
        salvar_db()


def criar_usuario(usuario, senha, email):
    if any(u["usuario"] == usuario for u in db["usuarios"]):
        return False, "Usuário já existe"

    if any(u["email"] == email for u in db["usuarios"]):
        return False, "E-mail já cadastrado"

    db["usuarios"].append({
        "usuario": usuario,
        "senha": senha,
        "email": email
    })

    salvar_db()
    return True, "OK"


def autenticar_usuario(usuario, senha):
    return any(u["usuario"] == usuario and u["senha"] == senha for u in db["usuarios"])


# ===============================
# ⭐ Favoritos
# ===============================

def adicionar_favorito(usuario, livro):
    """Adiciona um livro completo ao favorito."""
    user_favs = db["favoritos"].setdefault(usuario, [])

    # Evita duplicados usando id do Google Books
    id_livro = livro.get("id")
    if id_livro and any(f.get("id") == id_livro for f in user_favs):
        return False  # já existe

    user_favs.append(livro)
    salvar_db()
    return True


def listar_favoritos(usuario):
    return db["favoritos"].get(usuario, [])


def remover_favorito(usuario, livro_id):
    if usuario not in db["favoritos"]:
        return

    db["favoritos"][usuario] = [
        f for f in db["favoritos"][usuario] if f.get("id") != livro_id
    ]
    salvar_db()


# ===============================
# 📝 Notas
# ===============================

def salvar_nota(usuario, titulo, nota):
    user_notas = db["notas"].setdefault(usuario, {})
    user_notas[titulo] = nota
    salvar_db()


def pegar_notas(usuario):
    return db["notas"].get(usuario, {})


def pegar_nota(usuario, titulo):
    return db["notas"].get(usuario, {}).get(titulo, 0)
