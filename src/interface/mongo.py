from src.api.google_books import buscar_livros
from typing import Tuple

# Fallback em memória
usuarios_col = []

def is_db_available() -> bool:
    """Simula verificação do banco de dados"""
    try:
        return True
    except:
        return False

def pre_cadastro():
    """Pré-cadastra usuário renan1227"""
    if not any(u["usuario"] == "renan1227" for u in usuarios_col):
        usuarios_col.append({
            "usuario": "renan1227",
            "senha": "123",
            "email": "renasin122"
        })

def criar_usuario(usuario: str, senha: str, email: str) -> Tuple[bool, str]:
    """Cria um usuário, retorna (True, "") se sucesso ou (False, msg) se falha"""

    # Verifica se o nome de usuário já existe
    if any(u["usuario"] == usuario for u in usuarios_col):
        return False, "Usuário já existe"

    # ⚠️ Verifica se o e-mail já está cadastrado
    if any(u["email"] == email for u in usuarios_col):
        return False, "E-mail já cadastrado"

    # Cria o novo usuário
    usuarios_col.append({
        "usuario": usuario,
        "senha": senha,
        "email": email
    })
    return True, ""

def autenticar_usuario(usuario: str, senha: str) -> bool:
    """Autentica usuário"""
    for u in usuarios_col:
        if u["usuario"] == usuario and u["senha"] == senha:
            return True
    return False
