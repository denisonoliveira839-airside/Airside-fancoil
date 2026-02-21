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
# BANCO
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
        corrente_res REAL,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

# =====================================================
# FUNÇÕES
# =====================================================

def calcular_motor(vazao, tensao, pressao_total=500):
    potencia_kw = (vazao * pressao_total) / (0.65 * 3600000)
    potencia_kw *= 1.15
    potencia_cv = potencia_kw / 0.736
    potencia_motor = max(1, math.ceil(potencia_cv))

    corrente = round((potencia_kw * 1000) / (math.sqrt(3) * tensao * 0.85), 2)
    disj_motor = math.ceil(corrente * 1.25)
    disj_geral = math.ceil(disj_motor * 1.3)

    cabo = 2.5
    if corrente > 18: cabo = 4
    if corrente > 28: cabo = 6
    if corrente > 36: cabo = 10
    if corrente > 50: cabo = 16

    return potencia_motor, corrente, disj_motor, disj_geral, cabo

def calcular_resistencia(potencia_kw, tensao):
    corrente = round((potencia_kw * 1000) / tensao, 2)
    disj = math.ceil(corrente * 1.25)

    cabo = 2.5
    if corrente > 18: cabo = 4
    if corrente > 28: cabo = 6
    if corrente > 36: cabo = 10
    if corrente > 50: cabo = 16

    return corrente, disj, cabo

# =====================================================
# ABAS
# =====================================================

aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais",
     "🎛️ Simulador", "👥 Clientes", "📁 Projetos", "💰 Orçamento"]
)

# =====================================================
# ABA 1
# =====================================================

with aba1:

    cliente = st.text_input("Cliente")
    tecnico = st.text_input("Técnico")
    tipo = st.selectbox("Tipo", ["Motor", "Motor + Resistência", "Somente Resistência"])
    tensao = st.selectbox("Tensão (V)", [220, 380, 440])

    vazao = 0
    pressao = 0
    pot_res = 0

    if tipo != "Somente Resistência":
        vazao = st.number_input("Vazão (m³/h)", value=5000.0)
        pressao = st.number_input("Pressão (Pa)", value=500.0)

    if tipo != "Motor":
        pot_res = st.number_input("Potência Resistência (kW)", value=10.0)

    if st.button("🔎 Gerar Projeto"):

        motor_data = None
        res_data = None

        if tipo != "Somente Resistência":
            motor_data = calcular_motor(vazao, tensao, pressao)

        if tipo != "Motor":
            res_data = calcular_resistencia(pot_res, tensao)

        st.session_state["motor"] = motor_data
        st.session_state["res"] = res_data
        st.session_state["cliente"] = cliente
        st.session_state["tecnico"] = tecnico
        st.session_state["tipo"] = tipo
        st.session_state["tensao"] = tensao

        st.success("Projeto gerado!")

# =====================================================
# ABA 2 - RESULTADO
# =====================================================

with aba2:

    if st.session_state.get("motor"):
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]
        st.write(f"Motor: {motor} CV")
        st.write(f"Corrente: {corrente} A")
        st.write(f"Disjuntor Motor: {disj_motor} A")
        st.write(f"Cabo Motor: {cabo} mm²")

    if st.session_state.get("res"):
        corrente_res, disj_res, cabo_res = st.session_state["res"]
        st.write("---")
        st.write("🔥 Resistência")
        st.write(f"Corrente: {corrente_res} A")
        st.write(f"Disjuntor: {disj_res} A")
        st.write(f"Cabo: {cabo_res} mm²")

# =====================================================
# ABA 3
# =====================================================

with aba3:
    st.write("Diagrama lógico simplificado")
    if st.session_state.get("motor"):
        st.write("Rede → Disjuntor → Motor")
    if st.session_state.get("res"):
        st.write("Rede → Disjuntor → Resistência")

# =====================================================
# ABA 4
# =====================================================

with aba4:

    dados = []

    if st.session_state.get("motor"):
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]
        dados.append(["Motor", f"{motor} CV"])
        dados.append(["Cabo Motor", f"{cabo} mm²"])

    if st.session_state.get("res"):
        corrente_res, disj_res, cabo_res = st.session_state["res"]
        dados.append(["Cabo Resistência", f"{cabo_res} mm²"])

    if dados:
        df = pd.DataFrame(dados, columns=["Item", "Especificação"])
        st.dataframe(df)

# =====================================================
# ABA 5
# =====================================================

with aba5:

    if st.session_state.get("motor"):
        motor, corrente, _, _, _ = st.session_state["motor"]
        tempo = np.linspace(0, 5, 100)
        corrente_sim = corrente * (1 - np.exp(-tempo))

        fig, ax = plt.subplots()
        ax.plot(tempo, corrente_sim)
        st.pyplot(fig)

# =====================================================
# ABA 6
# =====================================================

with aba6:

    nome = st.text_input("Novo Cliente")
    tecnico = st.text_input("Novo Técnico")

    if st.button("Salvar Cliente"):
        conn = conectar()
        c = conn.cursor()
        c.execute(
            "INSERT INTO clientes (nome, tecnico, data) VALUES (?, ?, ?)",
            (nome, tecnico, datetime.now().strftime("%d/%m/%Y"))
        )
        conn.commit()
        conn.close()
        st.success("Salvo!")

    conn = conectar()
    df = pd.read_sql("SELECT * FROM clientes", conn)
    conn.close()
    st.dataframe(df)

# =====================================================
# ABA 7
# =====================================================

with aba7:

    if st.button("Salvar Projeto"):

        motor = st.session_state.get("motor")
        res = st.session_state.get("res")

        corrente = motor[1] if motor else 0
        corrente_res = res[0] if res else 0

        conn = conectar()
        c = conn.cursor()

        c.execute("""
            INSERT INTO projetos (cliente, tecnico, tipo, tensao, motor, corrente, corrente_res, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            st.session_state.get("cliente",""),
            st.session_state.get("tecnico",""),
            st.session_state.get("tipo",""),
            st.session_state.get("tensao",0),
            motor[0] if motor else 0,
            corrente,
            corrente_res,
            datetime.now().strftime("%d/%m/%Y")
        ))

        conn.commit()
        conn.close()
        st.success("Projeto salvo!")

    conn = conectar()
    df = pd.read_sql("SELECT * FROM projetos", conn)
    conn.close()
    st.dataframe(df)

# =====================================================
# ABA 8
# =====================================================

with aba8:

    total = 0

    if st.session_state.get("motor"):
        total += st.session_state["motor"][0] * 300

    if st.session_state.get("res"):
        total += 500

    margem = st.slider("Margem (%)", 0, 100, 30)
    total_final = total * (1 + margem / 100)

    st.write(f"Valor Base: R$ {round(total,2)}")
    st.write(f"Valor Final: R$ {round(total_final,2)}")
