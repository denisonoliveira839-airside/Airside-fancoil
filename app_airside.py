import streamlit as st
import math
import pandas as pd
import sqlite3
from datetime import datetime

st.set_page_config(page_title="AirSide PRO", layout="wide")

# =====================================================
# BANCO DE DADOS
# =====================================================

def conectar():
    return sqlite3.connect("hvac_system.db")

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        empresa TEXT,
        email TEXT,
        telefone TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS projetos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        tecnico TEXT,
        motor_cv REAL,
        corrente REAL,
        disj_motor REAL,
        disj_geral REAL,
        cabo REAL,
        valor REAL,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

# =====================================================
# CÁLCULO MOTOR (SEU CÓDIGO ORIGINAL INTACTO)
# =====================================================

def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):
    potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
    potencia_kw *= 1.15
    potencia_cv = potencia_kw / 0.736
    potencia_motor = max(1, math.ceil(potencia_cv))

    corrente = round((potencia_kw * 1000) / (math.sqrt(3) * tensao * 0.85), 2)
    disj_motor = math.ceil(corrente * 1.25)
    disj_geral = max(10, math.ceil(disj_motor * 1.3))

    if corrente <= 18:
        cabo = 2.5
    elif corrente <= 28:
        cabo = 4
    elif corrente <= 36:
        cabo = 6
    elif corrente <= 50:
        cabo = 10
    else:
        cabo = 16

    return potencia_motor, corrente, disj_motor, disj_geral, cabo

# =====================================================
# INTERFACE
# =====================================================

st.title("🌀 AirSide PRO")
st.markdown("### Sistema Profissional de Dimensionamento Elétrico")
st.divider()

abas = st.tabs([
    "📋 Dados",
    "📊 Resultado",
    "📑 Multifilar",
    "📦 Materiais",
    "🎛️ Simulador",
    "👥 Clientes",
    "📁 Projetos",
    "💰 Orçamento"
])

# =====================================================
# ABA 1 - DADOS (INALTERADA)
# =====================================================

with abas[0]:

    col1, col2 = st.columns(2)
    cliente = col1.text_input("Nome do Cliente")
    tecnico = col2.text_input("Nome do Técnico")

    col3, col4, col5 = st.columns(3)

    tipo_partida = col3.selectbox(
        "Tipo de Partida",
        ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter"]
    )

    tensao = col4.selectbox("Tensão (V)", [220, 380, 440])

    vazao = col5.number_input("Vazão (m³/h)", value=5000.0)
    pressao = st.number_input("Pressão Total (Pa)", min_value=100.0, value=500.0)

    calcular = st.button("🔎 Gerar Projeto", use_container_width=True)

# =====================================================
# PROCESSAMENTO
# =====================================================

if calcular:
    motor, corrente, disj_motor, disj_geral, cabo = calcular_motor(vazao, tensao, pressao)

    st.session_state.update({
        "motor": motor,
        "corrente": corrente,
        "disj_motor": disj_motor,
        "disj_geral": disj_geral,
        "cabo": cabo,
        "cliente": cliente,
        "tecnico": tecnico
    })

# =====================================================
# ABA 2 - RESULTADO
# =====================================================

with abas[1]:
    if "motor" in st.session_state:
        st.metric("Motor (CV)", st.session_state.motor)
        st.metric("Corrente (A)", st.session_state.corrente)
        st.metric("DJ Motor (A)", st.session_state.disj_motor)
        st.metric("DJ Geral (A)", st.session_state.disj_geral)
        st.metric("Cabo (mm²)", st.session_state.cabo)

# =====================================================
# ABA CLIENTES
# =====================================================

with abas[5]:

    st.subheader("Cadastro de Clientes")

    nome = st.text_input("Nome")
    empresa = st.text_input("Empresa")
    email = st.text_input("Email")
    telefone = st.text_input("Telefone")

    if st.button("Salvar Cliente"):
        conn = conectar()
        c = conn.cursor()
        c.execute("INSERT INTO clientes (nome, empresa, email, telefone) VALUES (?,?,?,?)",
                  (nome, empresa, email, telefone))
        conn.commit()
        conn.close()
        st.success("Cliente salvo com sucesso!")

    conn = conectar()
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    conn.close()

    st.dataframe(df_clientes, use_container_width=True)

# =====================================================
# ABA PROJETOS
# =====================================================

with abas[6]:

    st.subheader("Projetos Salvos")

    conn = conectar()
    df_proj = pd.read_sql("SELECT * FROM projetos", conn)
    conn.close()

    st.dataframe(df_proj, use_container_width=True)

    if "motor" in st.session_state:
        if st.button("Salvar Projeto Atual"):
            conn = conectar()
            c = conn.cursor()
            c.execute("""
            INSERT INTO projetos 
            (cliente, tecnico, motor_cv, corrente, disj_motor, disj_geral, cabo, valor, data)
            VALUES (?,?,?,?,?,?,?,?,?)
            """, (
                st.session_state.cliente,
                st.session_state.tecnico,
                st.session_state.motor,
                st.session_state.corrente,
                st.session_state.disj_motor,
                st.session_state.disj_geral,
                st.session_state.cabo,
                0,
                datetime.now().strftime("%d/%m/%Y")
            ))
            conn.commit()
            conn.close()
            st.success("Projeto salvo!")

# =====================================================
# ABA ORÇAMENTO
# =====================================================

with abas[7]:

    st.subheader("Gerar Orçamento")

    margem = st.slider("Margem (%)", 0, 100, 30)

    if "motor" in st.session_state:
        custo_base = st.session_state.motor * 500
        valor_venda = custo_base * (1 + margem/100)

        st.metric("Custo Base Estimado", f"R$ {round(custo_base,2)}")
        st.metric("Valor de Venda", f"R$ {round(valor_venda,2)}")

# =====================================================
# ABA SIMULADOR (SEU ORIGINAL INTACTO)
# =====================================================

with abas[4]:

    st.subheader("🎛️ Simulador Industrial")

    rpm_max = 3600
    setpoint = st.number_input("Pressão Alvo (Pa)", 100, 1000, 400)
    sujidade = st.slider("Sujidade do Filtro (%)", 0, 100, 0)

    if "rpm_auto" not in st.session_state:
        st.session_state.rpm_auto = 1200

    rpm = st.session_state.rpm_auto

    pressao_motor = (rpm / rpm_max) * 500
    contrapressao = sujidade * 5
    pressao_total = pressao_motor + contrapressao

    erro = setpoint - pressao_total
    rpm += erro * 0.4
    rpm = max(0, min(rpm, rpm_max))
    st.session_state.rpm_auto = rpm

    pressao_total = round((rpm / rpm_max) * 500 + contrapressao, 1)

    col1, col2, col3 = st.columns(3)
    col1.metric("RPM Atual", int(rpm))
    col2.metric("Pressão Total (Pa)", pressao_total)
    col3.metric("Erro", round(erro, 1))

    st.progress(rpm / rpm_max)
