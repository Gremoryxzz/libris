# src/interface/mongo.py
# Apenas lógica de dados (sem Streamlit)

usuarios_col = []

def is_db_available() -> bool:
    return True

def pre_cadastro():
    if not any(u["usuario"] == "renan1227" for u in usuarios_col):
        usuarios_col.append({
            "usuario": "renan1227",
            "senha": "123",
            "email": "renasin122"
        })

def criar_usuario(usuario, senha, email):
    if any(u["usuario"] == usuario for u in usuarios_col):
        return False, "Usuário já existe"
    if any(u["email"] == email for u in usuarios_col):
        return False, "E-mail já cadastrado"
    usuarios_col.append({
        "usuario": usuario,
        "senha": senha,
        "email": email
    })
    return True, ""

def autenticar_usuario(usuario, senha):
    return any(u["usuario"] == usuario and u["senha"] == senha for u in usuarios_col)
