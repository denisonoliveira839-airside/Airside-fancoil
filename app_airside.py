import streamlit as st
import math
import pandas as pd
from datetime import datetime
import sqlite3

st.set_page_config(page_title="AirSide PRO", layout="wide")

st.title("🌀 AirSide PRO")
st.markdown("### Sistema Profissional de Dimensionamento Elétrico")
st.divider()

# =====================================================
# BANCO DE DADOS (NOVO - NÃO INTERFERE NO RESTO)
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
        motor REAL,
        corrente REAL,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

# =====================================================
# CÁLCULO MOTOR
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
# ABAS (APENAS EXPANDIDAS)
# =====================================================

aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8 = st.tabs(
    [
        "📋 Dados",
        "📊 Resultado",
        "📑 Multifilar",
        "📦 Materiais",
        "🎛️ Simulador",
        "👥 Clientes",
        "📁 Projetos",
        "💰 Orçamento"
    ]
)

# =====================================================
# ABA 1 - DADOS
# =====================================================

with aba1:

    col1, col2 = st.columns(2)
    cliente = col1.text_input("Nome do Cliente")
    tecnico = col2.text_input("Nome do Técnico")

    col3, col4, col5 = st.columns(3)

    tipo_partida = col3.selectbox(
        "Tipo de Partida",
        ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter", "Somente Resistência"]
    )

    tensao = col4.selectbox("Tensão (V)", [220, 380, 440])

    if tipo_partida != "Somente Resistência":
        vazao = col5.number_input("Vazão (m³/h)", value=5000.0)
        pressao = st.number_input("Pressão Total (Pa)", min_value=100.0, value=500.0)

    calcular = st.button("🔎 Gerar Projeto", use_container_width=True)


# =====================================================
# PROCESSAMENTO
# =====================================================

if calcular:

    if tipo_partida != "Somente Resistência":
        motor_data = calcular_motor(vazao, tensao, pressao)
    else:
        motor_data = None

    st.session_state.update({
        "motor": motor_data
    })


# =====================================================
# ABA 2 - RESULTADO
# =====================================================

with aba2:
    if "motor" in st.session_state and st.session_state.motor:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.motor
        st.metric("Motor (CV)", motor)
        st.metric("Corrente (A)", corrente)
        st.metric("DJ Motor (A)", disj_motor)
        st.metric("DJ Geral (A)", disj_geral)
        st.metric("Cabo (mm²)", cabo)


# =====================================================
# ABA 5 - SIMULADOR (INALTERADO)
# =====================================================

with aba5:

    st.subheader("🎛️ Simulador Industrial - Inversor + CLP")

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

    velocidade = max(0.2, 5 - (rpm / rpm_max) * 4.5)

    motor_html = f"""
    <div style="display:flex; justify-content:center;">
        <div style="
            width:150px;
            height:150px;
            border-radius:50%;
            border:8px solid #1f77b4;
            animation: spin {velocidade}s linear infinite;
        "></div>
    </div>
    <style>
    @keyframes spin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    </style>
    """

    if rpm > 0:
        st.markdown(motor_html, unsafe_allow_html=True)
        st.success("🟢 Motor em Operação")
    else:
        st.markdown("🔴 Motor Parado")


# =====================================================
# ABA 6 - CLIENTES
# =====================================================

with aba6:

    st.subheader("Cadastro de Clientes")

    nome = st.text_input("Nome")
    empresa = st.text_input("Empresa")
    email = st.text_input("Email")
    telefone = st.text_input("Telefone")

    if st.button("Salvar Cliente"):
        conn = conectar()
        c = conn.cursor()
        c.execute(
            "INSERT INTO clientes (nome, empresa, email, telefone) VALUES (?,?,?,?)",
            (nome, empresa, email, telefone)
        )
        conn.commit()
        conn.close()
        st.success("Cliente salvo com sucesso!")

    conn = conectar()
    df_clientes = pd.read_sql("SELECT * FROM clientes", conn)
    conn.close()

    st.dataframe(df_clientes, use_container_width=True)


# =====================================================
# ABA 7 - PROJETOS
# =====================================================

with aba7:

    st.subheader("Projetos Salvos")

    conn = conectar()
    df_proj = pd.read_sql("SELECT * FROM projetos", conn)
    conn.close()

    st.dataframe(df_proj, use_container_width=True)

    if "motor" in st.session_state and st.session_state.motor:
        if st.button("Salvar Projeto Atual"):

            motor, corrente, _, _, _ = st.session_state.motor

            conn = conectar()
            c = conn.cursor()
            c.execute("""
                INSERT INTO projetos (cliente, tecnico, motor, corrente, data)
                VALUES (?,?,?,?,?)
            """, (
                cliente,
                tecnico,
                motor,
                corrente,
                datetime.now().strftime("%d/%m/%Y")
            ))
            conn.commit()
            conn.close()

            st.success("Projeto salvo com sucesso!")


# =====================================================
# ABA 8 - ORÇAMENTO
# =====================================================

with aba8:

    st.subheader("Orçamento")

    margem = st.slider("Margem (%)", 0, 100, 30)

    if "motor" in st.session_state and st.session_state.motor:

        motor, _, _, _, _ = st.session_state.motor

        custo_base = motor * 500
        valor_venda = custo_base * (1 + margem/100)

        st.metric("Custo Base Estimado", f"R$ {round(custo_base,2)}")
        st.metric("Preço de Venda", f"R$ {round(valor_venda,2)}")
