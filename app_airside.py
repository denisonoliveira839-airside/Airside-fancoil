import streamlit as st
import math
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(page_title="AirSide PRO", layout="wide")
st.title("🌀 AirSide PRO - Sistema Profissional de Dimensionamento Elétrico")
st.divider()

# =====================================================
# BANCO DE DADOS
# =====================================================

def conectar():
    return sqlite3.connect("airside.db")

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        tecnico TEXT,
        data TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS projetos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        tecnico TEXT,
        tipo TEXT,
        tensao INTEGER,
        motor REAL,
        corrente REAL,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

# =====================================================
# FUNÇÕES
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
# ABAS
# =====================================================

aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais",
     "🎛️ Simulador", "👥 Clientes", "📁 Projetos", "💰 Orçamento"]
)

# =====================================================
# ABA 1 - DADOS
# =====================================================

with aba1:

    col1, col2 = st.columns(2)
    cliente = col1.text_input("Nome do Cliente", key="cliente_dados")
    tecnico = col2.text_input("Nome do Técnico", key="tecnico_dados")

    st.divider()

    tipo_partida = st.selectbox(
        "Tipo de Partida",
        ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter"],
        key="tipo_partida"
    )

    tensao = st.selectbox("Tensão (V)", [220, 380, 440], key="tensao")
    vazao = st.number_input("Vazão (m³/h)", value=5000.0)
    pressao = st.number_input("Pressão Total (Pa)", value=500.0)

    if st.button("🔎 Gerar Projeto", use_container_width=True):

        motor_data = calcular_motor(vazao, tensao, pressao)

        st.session_state["motor"] = motor_data
        st.session_state["cliente"] = cliente
        st.session_state["tecnico"] = tecnico
        st.session_state["tipo"] = tipo_partida
        st.session_state["tensao"] = tensao

        st.success("Projeto gerado com sucesso!")

# =====================================================
# ABA 2 - RESULTADO
# =====================================================

with aba2:

    if st.session_state.get("motor"):

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]

        st.success("Projeto calculado com sucesso!")
        st.write(f"**Motor:** {motor} CV")
        st.write(f"**Corrente:** {corrente} A")
        st.write(f"**Disjuntor Motor:** {disj_motor} A")
        st.write(f"**Disjuntor Geral:** {disj_geral} A")
        st.write(f"**Cabo Sugerido:** {cabo} mm²")

    else:
        st.info("Gere um projeto na aba Dados.")

# =====================================================
# ABA 3 - MULTIFILAR
# =====================================================

with aba3:

    if st.session_state.get("motor"):

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]
        tipo = st.session_state["tipo"]

        st.subheader("📑 Diagrama Multifilar")

        if tipo == "Inversor":
            st.write("Rede → Disjuntor Geral → Inversor → Motor")
        elif tipo == "Direta":
            st.write("Rede → Disjuntor → Contator → Relé → Motor")
        elif tipo == "Estrela-Triângulo":
            st.write("Rede → Disjuntor → 3 Contatores → Motor")
        elif tipo == "Softstarter":
            st.write("Rede → Disjuntor → Softstarter → Motor")

        st.write(f"Cabo: {cabo} mm²")

    else:
        st.info("Gere um projeto na aba Dados.")

# =====================================================
# ABA 4 - MATERIAIS
# =====================================================

with aba4:

    if st.session_state.get("motor"):

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]

        df = pd.DataFrame({
            "Item": ["Motor", "Disjuntor Motor", "Disjuntor Geral", "Cabo"],
            "Valor": [f"{motor} CV", f"{disj_motor} A", f"{disj_geral} A", f"{cabo} mm²"]
        })

        st.dataframe(df, use_container_width=True)

    else:
        st.info("Gere um projeto na aba Dados.")

# =====================================================
# ABA 5 - SIMULADOR
# =====================================================

with aba5:

    if st.session_state.get("motor"):

        motor, corrente, _, _, _ = st.session_state["motor"]

        tempo = np.linspace(0, 5, 100)
        corrente_sim = corrente * (1 - np.exp(-tempo))

        fig, ax = plt.subplots()
        ax.plot(tempo, corrente_sim)
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Corrente (A)")
        ax.set_title("Simulação de Partida")

        st.pyplot(fig)

    else:
        st.info("Gere um projeto na aba Dados.")

# =====================================================
# ABA 6 - CLIENTES
# =====================================================

with aba6:

    st.subheader("👥 Clientes")

    nome = st.text_input("Nome", key="cliente_novo")
    tecnico = st.text_input("Técnico", key="tecnico_novo")

    if st.button("Salvar Cliente"):

        conn = conectar()
        c = conn.cursor()

        c.execute(
            "INSERT INTO clientes (nome, tecnico, data) VALUES (?, ?, ?)",
            (nome, tecnico, datetime.now().strftime("%d/%m/%Y"))
        )

        conn.commit()
        conn.close()

        st.success("Cliente salvo!")

    conn = conectar()
    df = pd.read_sql("SELECT * FROM clientes", conn)
    conn.close()

    st.dataframe(df, use_container_width=True)

# =====================================================
# ABA 7 - PROJETOS
# =====================================================

with aba7:

    if st.session_state.get("motor"):

        if st.button("Salvar Projeto"):

            motor, corrente, _, _, _ = st.session_state["motor"]

            conn = conectar()
            c = conn.cursor()

            c.execute("""
                INSERT INTO projetos (cliente, tecnico, tipo, tensao, motor, corrente, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                st.session_state.get("cliente", ""),
                st.session_state.get("tecnico", ""),
                st.session_state.get("tipo", ""),
                st.session_state.get("tensao", 0),
                motor,
                corrente,
                datetime.now().strftime("%d/%m/%Y")
            ))

            conn.commit()
            conn.close()

            st.success("Projeto salvo!")

    conn = conectar()
    df = pd.read_sql("SELECT * FROM projetos", conn)
    conn.close()

    st.dataframe(df, use_container_width=True)

# =====================================================
# ABA 8 - ORÇAMENTO
# =====================================================

with aba8:

    if st.session_state.get("motor"):

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]

        base = motor * 300 + disj_geral * 5 + cabo * 20
        margem = st.slider("Margem (%)", 0, 100, 30)
        total = base * (1 + margem / 100)

        st.write(f"Valor Base: R$ {round(base, 2)}")
        st.write(f"Valor Final: R$ {round(total, 2)}")

    else:
        st.info("Gere um projeto na aba Dados.")
