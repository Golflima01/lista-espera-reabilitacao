
import pandas as pd
from datetime import datetime, date
import streamlit as st
import hashlib

# ============================
# SISTEMA DE LOGIN COM GESTÃO
# ============================

# Inicializar armazenamento de usuários
if "usuarios" not in st.session_state:
    st.session_state.usuarios = {
        "admin": {
            "senha": hashlib.sha256("admin123".encode()).hexdigest(),
            "perfil": "Administrador"
        },
        "user1": {
            "senha": hashlib.sha256("senha123".encode()).hexdigest(),
            "perfil": "Comum"
        }
    }

# Função para autenticar
def autenticar(usuario, senha):
    senha_cripto = hashlib.sha256(senha.encode()).hexdigest()
    if usuario in st.session_state.usuarios:
        return st.session_state.usuarios[usuario]["senha"] == senha_cripto
    return False

# ============================
# FUNÇÕES AUXILIARES
# ============================

def calcular_dias_espera(data_contato):
    if isinstance(data_contato, date):
        data_contato = datetime.combine(data_contato, datetime.min.time())
    hoje = datetime.today()
    return (hoje - data_contato).days

def cor_tempo_espera(dias):
    if dias < 15:
        return 'background-color: #d4edda'
    elif dias < 30:
        return 'background-color: #fff3cd'
    else:
        return 'background-color: #f8d7da'

def aplicar_estilo(df):
    return df.style.applymap(lambda x: cor_tempo_espera(x) if isinstance(x, int) else "")

def alterar_senha(usuario, nova_senha):
    st.session_state.usuarios[usuario]["senha"] = hashlib.sha256(nova_senha.encode()).hexdigest()

def alterar_perfil(usuario, novo_perfil):
    st.session_state.usuarios[usuario]["perfil"] = novo_perfil

def adicionar_usuario(novo_usuario, senha, perfil):
    if novo_usuario not in st.session_state.usuarios:
        st.session_state.usuarios[novo_usuario] = {
            "senha": hashlib.sha256(senha.encode()).hexdigest(),
            "perfil": perfil
        }
        return True
    return False

def excluir_usuario(usuario):
    if usuario in st.session_state.usuarios and usuario != "admin":
        del st.session_state.usuarios[usuario]

# ============================
# INTERFACE STREAMLIT
# ============================

st.set_page_config(page_title="Lista de Espera - Reabilitação", layout="wide")
st.title("🔐 Sistema de Lista de Espera - Centro de Reabilitação")

# Login
if "usuario" not in st.session_state:
    with st.form("login_form"):
        st.subheader("Acesso ao Sistema")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        logar = st.form_submit_button("Entrar")

        if logar:
            if autenticar(usuario, senha):
                st.session_state.usuario = usuario
                st.success(f"Bem-vindo, {usuario}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# Se logado
if "usuario" in st.session_state:
    usuario_atual = st.session_state.usuario
    perfil = st.session_state.usuarios[usuario_atual]["perfil"]
    st.sidebar.success(f"Usuário: {usuario_atual} ({perfil})")
    if st.sidebar.button("Sair"):
        del st.session_state.usuario
        st.rerun()

    # Alterar senha
    with st.sidebar.expander("🔒 Alterar Senha"):
        senha_nova = st.text_input("Nova Senha", type="password")
        senha_confirmar = st.text_input("Confirmar Senha", type="password")
        if st.button("Atualizar Senha"):
            if senha_nova == senha_confirmar and senha_nova != "":
                alterar_senha(usuario_atual, senha_nova)
                st.success("Senha atualizada com sucesso.")
            else:
                st.error("As senhas não coincidem.")

    # Painel administrador
    if perfil == "Administrador":
        st.sidebar.markdown("---")
        st.sidebar.markdown("🛠️ **Gerenciar Usuários**")

        # Adicionar novo usuário
        with st.sidebar.expander("➕ Adicionar Usuário"):
            novo_user = st.text_input("Novo Usuário")
            nova_senha = st.text_input("Senha", type="password")
            novo_perfil = st.selectbox("Perfil", ["Administrador", "Comum"])
            if st.button("Criar Usuário"):
                if adicionar_usuario(novo_user, nova_senha, novo_perfil):
                    st.success("Usuário adicionado com sucesso.")
                else:
                    st.error("Usuário já existe.")

        # Lista de usuários
        with st.sidebar.expander("👥 Lista de Usuários"):
            for u, dados in st.session_state.usuarios.items():
                col1, col2, col3 = st.columns([4, 3, 1])
                col1.markdown(f"**{u}**")
                novo_p = col2.selectbox(f"Perfil de {u}", ["Administrador", "Comum"], index=0 if dados["perfil"] == "Administrador" else 1, key=f"perfil_{u}")
                if novo_p != dados["perfil"]:
                    alterar_perfil(u, novo_p)
                if u != "admin":
                    if col3.button("❌", key=f"del_{u}"):
                        excluir_usuario(u)
                        st.experimental_rerun()

    # Base de dados
    if "dados" not in st.session_state:
        st.session_state.dados = pd.DataFrame(columns=[
            "Nome", "Nº Carteirinha", "Data 1º Contato", "Dias de Espera",
            "Especialidade", "Telefone", "Horário Preferencial",
            "Preferência Profissional", "Profissional Indicado", "Registrado Por", "Data Registro"
        ])

    st.subheader("➕ Adicionar Novo Paciente")
    with st.form("novo_paciente"):
        nome = st.text_input("Nome do Paciente")
        carteirinha = st.text_input("Número da Carteirinha")
        data_contato = st.date_input("Data do Primeiro Contato", datetime.today())
        especialidade = st.selectbox("Especialidade Necessária", [
            "Fisioterapia Traumato-Ortopédica", "Fisioterapia Neurofuncional",
            "Fisioterapia Uroginecológica", "Reeducação Postural Global",
            "Disfunção Temporomandibular", "Acupuntura", "Fonoaudiologia",
            "Psicologia", "Terapia Ocupacional"
        ])
        telefone = st.text_input("Telefone para Contato")
        horario = st.radio("Horário Preferencial", ["Manhã", "Tarde", "Indiferente"])
        prefere_profissional = st.radio("Preferência por Profissional?", ["Não", "Sim"])
        profissional = ""
        if prefere_profissional == "Sim":
            profissional = st.text_input("Nome do Profissional Preferido")

        enviar = st.form_submit_button("Adicionar à Lista")
        if enviar:
            dias_espera = calcular_dias_espera(data_contato)
            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            novo = pd.DataFrame([[nome, carteirinha, data_contato, dias_espera,
                                  especialidade, telefone, horario,
                                  prefere_profissional, profissional,
                                  usuario_atual, agora]],
                                columns=st.session_state.dados.columns)
            st.session_state.dados = pd.concat([st.session_state.dados, novo], ignore_index=True)
            st.success("Paciente adicionado com sucesso.")

    # Atualizar dias
    st.session_state.dados["Dias de Espera"] = st.session_state.dados["Data 1º Contato"].apply(
        lambda x: calcular_dias_espera(pd.to_datetime(x)))

    # Exibir lista
    st.subheader("📊 Lista Atual de Espera")
    st.dataframe(aplicar_estilo(st.session_state.dados))

    # Exportar lista
    st.download_button("📥 Baixar Excel", data=st.session_state.dados.to_csv(index=False).encode('utf-8'),
                       file_name='lista_espera_reabilitacao.csv', mime='text/csv')

    if perfil == "Administrador":
        st.subheader("🧾 Histórico de Registros")
        historico = st.session_state.dados[["Nome", "Especialidade", "Registrado Por", "Data Registro"]]
        st.dataframe(historico)
