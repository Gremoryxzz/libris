import streamlit as st
from src.interface.mongo import criar_usuario, autenticar_usuario

# =============================
# TELA DE LOGIN
# =============================
def tela_login():
    st.title("🔐 Login")

    usuario = st.text_input("Usuário:")
    senha = st.text_input("Senha:", type="password")

    if st.button("Entrar"):
        if autenticar_usuario(usuario, senha):
            st.success("Login realizado com sucesso!")

            # inicializar sessão
            st.session_state.logado = True
            st.session_state.usuario = usuario

            # resetar estado do app
            st.session_state.pagina = "recomendador"
            st.session_state.livro_selecionado = None
            st.session_state.favoritos = []
            st.session_state.notas = {}
            st.session_state.db_loaded = False

            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")


# =============================
# TELA DE CRIAR CONTA
# =============================
def criar_conta():
    st.title("📝 Criar nova conta")

    usuario = st.text_input("Usuário:")
    email = st.text_input("E-mail:")
    senha = st.text_input("Senha:", type="password")
    senha2 = st.text_input("Confirmar senha:", type="password")

    if st.button("Cadastrar"):

        if senha != senha2:
            st.error("As senhas não coincidem.")
            return

        ok, msg = criar_usuario(usuario, senha, email)

        if ok:
            st.success("Conta criada com sucesso!")

            # login automático após criação da conta
            st.session_state.logado = True
            st.session_state.usuario = usuario

            # resetar estado do app
            st.session_state.pagina = "recomendador"
            st.session_state.livro_selecionado = None
            st.session_state.favoritos = []
            st.session_state.notas = {}
            st.session_state.db_loaded = False

            st.rerun()

        else:
            st.error(msg)
