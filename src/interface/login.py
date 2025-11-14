import streamlit as st
from src.interface.mongo import criar_usuario, autenticar_usuario

def tela_login():
    st.title("🔐 Área de Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if not usuario or not senha:
            st.warning("⚠️ Preencha todos os campos!")
            return

        if autenticar_usuario(usuario, senha):
            st.success(f"✅ Login realizado! Bem-vindo, {usuario}")
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.session_state.pagina = "recomendador"
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos!")

def criar_conta():
    st.title("📝 Criar Conta")

    usuario = st.text_input("Escolha um nome de usuário")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    senha_conf = st.text_input("Confirme a senha", type="password")

    if st.button("Criar Conta"):
        if not usuario or not senha or not email:
            st.warning("⚠️ Preencha todos os campos!")
            return
        if senha != senha_conf:
            st.warning("⚠️ As senhas não coincidem!")
            return

        sucesso, msg = criar_usuario(usuario, senha, email)

        if sucesso:
            st.success(f"✅ Conta criada com sucesso! Você já pode logar, {usuario}")
        else:
            # 🔥 Mensagens específicas
            if "E-mail" in msg:
                st.warning("⚠️ Este e-mail já está cadastrado. Tente outro.")
            elif "Usuário" in msg:
                st.warning("⚠️ Nome de usuário já existe. Escolha outro.")
            else:
                st.error(f"❌ Não foi possível criar a conta: {msg}")
