import pandas as pd
from datetime import datetime, date
import streamlit as st
import hashlib
import os

# ============================
# SISTEMA DE LOGIN COM GESTÃO
# ============================

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

def autenticar(usuario, senha):
    senha_cripto = hashlib.sha256(senha.encode()).hexdigest()
    if usuario in st.session_state.usuarios:
        return st.session_state.usuarios[usuario]["senha"] == senha_cripto
    return False

# ============================
# FUNÇÕES AUXILIARES
# ============================

def calcular_dias_espera(data_contato):
    if isinstance(data_contato, pd.Timestamp):
        data_contato = data_contato.to_pydatetime()
    elif isinstance(data_contato, date):
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
# DADOS E ARQUIVOS
# ============================

DATA_FILE_ESPERA = "data_espera.csv"
DATA_FILE_ATENDIDOS = "data_atendidos.csv"

colunas_padrao = [
    "Nome", "Nº Carteirinha", "Data 1º Contato", "Dias de Espera", "Especialidade",
    "Telefone", "Horário Preferencial", "Preferência Profissional", "Profissional Indicado",
    "Registrado Por", "Data Registro", "Vaga Concedida", "Profissional Responsável",
    "Horário Atendimento", "Data de Início"
]

def carregar_dados():
    if "dados" not in st.session_state:
        if os.path.exists(DATA_FILE_ESPERA):
            st.session_state.dados = pd.read_csv(DATA_FILE_ESPERA)
            st.session_state.dados["Data 1º Contato"] = pd.to_datetime(st.session_state.dados["Data 1º Contato"], errors="coerce")
        else:
            st.session_state.dados = pd.DataFrame(columns=colunas_padrao)

    if "atendidos" not in st.session_state:
        if os.path.exists(DATA_FILE_ATENDIDOS):
            st.session_state.atendidos = pd.read_csv(DATA_FILE_ATENDIDOS)
            st.session_state.atendidos["Data 1º Contato"] = pd.to_datetime(st.session_state.atendidos["Data 1º Contato"], errors="coerce")
        else:
            st.session_state.atendidos = pd.DataFrame(columns=colunas_padrao)

def salvar_dados():
    st.session_state.dados.to_csv(DATA_FILE_ESPERA, index=False)
    st.session_state.atendidos.to_csv(DATA_FILE_ATENDIDOS, index=False)

# ============================
# INTERFACE STREAMLIT
# ============================

st.set_page_config(page_title="Lista de Espera - Reabilitação", layout="wide")
st.title("📋 Sistema de Lista de Espera - Centro de Reabilitação")

# Carrega os dados
carregar_dados()

# Login
if "usuario" not in st.session_state:
    with st.form("login_form"):
        st.subheader("🔐 Acesso ao Sistema")
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

# Após login
if "usuario" in st.session_state:
    usuario_atual = st.session_state.usuario
    perfil = st.session_state.usuarios[usuario_atual]["perfil"]
    st.sidebar.success(f"Usuário: {usuario_atual} ({perfil})")

    if st.sidebar.button("Sair"):
        del st.session_state.usuario
        st.rerun()

    # Alterar senha
    with st.sidebar.expander("🔒 Alterar Senha"):
        nova = st.text_input("Nova Senha", type="password")
        confirmar = st.text_input("Confirmar Senha", type="password")
        if st.button("Atualizar Senha"):
            if nova == confirmar and nova != "":
                alterar_senha(usuario_atual, nova)
                st.success("Senha atualizada.")
            else:
                st.error("As senhas não coincidem.")

    # Área Administrativa
    if perfil == "Administrador":
        st.sidebar.markdown("---")
        st.sidebar.markdown("🛠️ **Gerenciar Usuários**")

        with st.sidebar.expander("➕ Novo Usuário"):
            novo_user = st.text_input("Usuário")
            nova_senha = st.text_input("Senha", type="password")
            tipo = st.selectbox("Perfil", ["Administrador", "Comum"])
            if st.button("Criar"):
                if adicionar_usuario(novo_user, nova_senha, tipo):
                    st.success("Usuário criado.")
                else:
                    st.error("Usuário já existe.")

        with st.sidebar.expander("👥 Lista de Usuários"):
            for u, dados in st.session_state.usuarios.items():
                col1, col2, col3 = st.columns([4, 3, 1])
                col1.markdown(f"**{u}**")
                p = col2.selectbox(f"Perfil de {u}", ["Administrador", "Comum"], index=0 if dados["perfil"] == "Administrador" else 1, key=f"perfil_{u}")
                if p != dados["perfil"]:
                    alterar_perfil(u, p)
                if u != "admin":
                    if col3.button("❌", key=f"del_{u}"):
                        excluir_usuario(u)
                        st.experimental_rerun()

    # Formulário
    st.subheader("➕ Adicionar Novo Paciente")
    with st.form("novo_paciente"):
        nome = st.text_input("Nome")
        carteirinha = st.text_input("Nº da Carteirinha")
        data_contato = st.date_input("Data do Primeiro Contato", datetime.today())
        especialidade = st.selectbox("Especialidade", [
            "Fisioterapia Traumato-Ortopédica", "Fisioterapia Neurofuncional",
            "Fisioterapia Uroginecológica", "Reeducação Postural Global",
            "Disfunção Temporomandibular", "Acupuntura", "Fonoaudiologia",
            "Psicologia", "Terapia Ocupacional"
        ])
        telefone = st.text_input("Telefone")
        horario = st.radio("Turno Preferido", ["Manhã", "Tarde", "Indiferente"])
        preferencia = st.radio("Preferência por Profissional?", ["Não", "Sim"])
        prof_indicado = ""
        if preferencia == "Sim":
            prof_indicado = st.text_input("Profissional Preferido")

        vaga = st.radio("Vaga Concedida?", ["Não", "Sim"])
        prof_resp = ""
        horario_atend = ""
        data_inicio = ""
        if vaga == "Sim":
            prof_resp = st.text_input("Profissional Responsável")
            horario_atend = st.text_input("Horário de Atendimento")
            data_inicio = st.date_input("Data de Início")

        enviar = st.form_submit_button("Salvar Paciente")
        if enviar:
            dias = calcular_dias_espera(data_contato)
            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            novo = pd.DataFrame([[nome, carteirinha, data_contato, dias, especialidade, telefone, horario,
                                  preferencia, prof_indicado, usuario_atual, agora, vaga, prof_resp,
                                  horario_atend, data_inicio]], columns=colunas_padrao)

            if vaga == "Sim":
                st.session_state.atendidos = pd.concat([st.session_state.atendidos, novo], ignore_index=True)
                st.success("Paciente movido para atendidos.")
            else:
                st.session_state.dados = pd.concat([st.session_state.dados, novo], ignore_index=True)
                st.success("Paciente adicionado à lista de espera.")
            salvar_dados()

    # Atualiza dias de espera
    st.session_state.dados["Dias de Espera"] = st.session_state.dados["Data 1º Contato"].apply(
        lambda x: calcular_dias_espera(pd.to_datetime(x))
    )

    # Tabelas
    st.subheader("🕐 Pacientes em Espera")
    st.subheader("🕐 Pacientes em Espera")

for i, row in st.session_state.dados.iterrows():
    with st.expander(f"{row['Nome']} - {row['Especialidade']}"):
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"📅 Esperando desde: **{row['Data 1º Contato'].strftime('%d/%m/%Y')}**")
        col2.markdown(f"📞 Telefone: **{row['Telefone']}**")
        col3.markdown(f"🕐 Preferência: **{row['Horário Preferencial']}**")

        if "editar_espera" in st.session_state.usuarios[usuario_atual]["permissoes"]:
            with st.form(f"alocar_form_{i}"):
                st.markdown("### 📌 Marcar Vaga Encontrada")
                prof_resp = st.text_input("Profissional Responsável", key=f"prof_{i}")
                horario_atend = st.text_input("Horário de Atendimento", key=f"horario_{i}")
                data_inicio = st.date_input("Data de Início", key=f"data_inicio_{i}")
                confirmar = st.form_submit_button("Confirmar Vaga")

                if confirmar:
                    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                    row_data = row.copy()
                    row_data["Profissional Responsável"] = prof_resp
                    row_data["Horário Atendimento"] = horario_atend
                    row_data["Data de Início"] = data_inicio
                    row_data["Vaga Concedida"] = "Sim"
                    row_data["Data Registro"] = agora
                    row_data["Registrado Por"] = usuario_atual

                    st.session_state.atendidos = pd.concat([st.session_state.atendidos, pd.DataFrame([row_data])], ignore_index=True)
                    st.session_state.dados.drop(index=i, inplace=True)
                    st.success(f"Paciente {row['Nome']} movido para atendidos.")
                    salvar_dados()
                    st.experimental_rerun()


    st.subheader("✅ Pacientes Atendidos")
    st.dataframe(st.session_state.atendidos)

    # Exportar Excel com duas abas
    st.subheader("📥 Exportar Dados")
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        st.session_state.dados.to_excel(writer, sheet_name="Em Espera", index=False)
        st.session_state.atendidos.to_excel(writer, sheet_name="Atendidos", index=False)
    st.download_button("📤 Baixar Excel", data=output.getvalue(), file_name="lista_reabilitacao.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Histórico
    if perfil == "Administrador":
        st.subheader("📜 Histórico de Registros")
        historico = pd.concat([st.session_state.dados, st.session_state.atendidos])
        st.dataframe(historico[["Nome", "Especialidade", "Registrado Por", "Data Registro", "Vaga Concedida"]])
