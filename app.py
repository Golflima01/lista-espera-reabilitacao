# Gerenciador de Lista de Espera para Centro de Reabilitação
import pandas as pd
from datetime import datetime
import streamlit as st
import numpy as np

# Função para calcular dias de espera
def calcular_dias_espera(data_contato):
    hoje = datetime.today()
    return (hoje - data_contato).days

# Cores por tempo de espera
def cor_tempo_espera(dias):
    if dias < 15:
        return 'background-color: #d4edda'  # Verde claro
    elif dias < 30:
        return 'background-color: #fff3cd'  # Amarelo
    else:
        return 'background-color: #f8d7da'  # Vermelho claro

# Configuração do Streamlit
st.set_page_config(page_title="Lista de Espera - Centro de Reabilitação", layout="wide")
st.title("📋 Lista de Espera - Centro de Reabilitação")

# Carregar ou iniciar base de dados
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "Nome", "Nº Carteirinha", "Data 1º Contato", "Dias de Espera",
        "Especialidade", "Telefone", "Horário Preferencial",
        "Preferência Profissional", "Profissional Indicado"])

# Formulário de novo paciente
with st.form("novo_paciente"):
    st.subheader("Adicionar Novo Paciente à Lista de Espera")
    nome = st.text_input("Nome do Paciente")
    carteirinha = st.text_input("Número da Carteirinha")
    data_contato = st.date_input("Data do Primeiro Contato", datetime.today())
    especialidade = st.selectbox("Especialidade Necessária", [
        "Fisioterapia Traumato-Ortopédica",
        "Fisioterapia Neurofuncional",
        "Fisioterapia Uroginecológica",
        "Reeducação Postural Global",
        "Disfunção Temporomandibular",
        "Acupuntura",
        "Fonoaudiologia",
        "Psicologia",
        "Terapia Ocupacional"])
    telefone = st.text_input("Telefone para Contato")
    horario = st.radio("Horário Preferencial", ["Manhã", "Tarde", "Indiferente"])
    prefere_profissional = st.radio("Preferência por Profissional?", ["Não", "Sim"])
    profissional = ""
    if prefere_profissional == "Sim":
        profissional = st.text_input("Nome do Profissional Preferido")
    enviado = st.form_submit_button("Adicionar Paciente")

    if enviado:
        dias_espera = calcular_dias_espera(data_contato)
        novo = pd.DataFrame([[nome, carteirinha, data_contato, dias_espera,
                              especialidade, telefone, horario,
                              prefere_profissional, profissional]],
                            columns=st.session_state.dados.columns)
        st.session_state.dados = pd.concat([st.session_state.dados, novo], ignore_index=True)
        st.success("Paciente adicionado à lista de espera.")

# Atualizar dias de espera
st.session_state.dados["Dias de Espera"] = st.session_state.dados["Data 1º Contato"].apply(lambda x: calcular_dias_espera(pd.to_datetime(x)))

# Exibir tabela com coloração
st.subheader("📊 Lista Atual de Espera")
def aplicar_estilo(df):
    return df.style.applymap(lambda x: cor_tempo_espera(x) if isinstance(x, int) else "")

st.dataframe(aplicar_estilo(st.session_state.dados))

# Exportar para Excel
st.download_button("📥 Baixar Excel da Lista", data=st.session_state.dados.to_csv(index=False).encode('utf-8'), file_name='lista_espera_reabilitacao.csv', mime='text/csv')
