import streamlit as st
import math
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3


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
# FUNÇÕES DE CÁLCULO
# =====================================================

def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):
    potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
    potencia_kw *= 1.15
    potencia_cv = potencia_kw / 0.736
    potencia_motor = max(1, math.ceil(potencia_cv))
    corrente = round((potencia_kw*1000)/(math.sqrt(3)*tensao*0.85),2)
    disj_motor = math.ceil(corrente*1.25)
    disj_geral = max(10, math.ceil(disj_motor*1.3))
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

def calcular_resistencia_por_potencia(pot_total, pot_unit, tensao):
    qtd = math.ceil(pot_total / pot_unit)
    corrente_unit = round((pot_unit*1000)/tensao,2)
    corrente_total = round(corrente_unit*qtd,2)
    disj_res = math.ceil(corrente_total*1.25)
    return qtd, corrente_total, disj_res

def calcular_resistencia_por_quantidade(qtd, pot_unit, tensao):
    corrente_unit = round((pot_unit*1000)/tensao,2)
    corrente_total = round(corrente_unit*qtd,2)
    disj_res = math.ceil(corrente_total*1.25)
    return qtd, corrente_total, disj_res

def gerar_cabecalho(cliente, tecnico, tensao, tipo, vazao=None, pressao=None):
    data = datetime.now().strftime("%d/%m/%Y")
    texto = f"Cliente: {cliente}\nTécnico: {tecnico}\nData: {data}\nTensão: {tensao}V\nTipo de Partida: {tipo}"
    if vazao:
        texto += f"\nVazão: {vazao} m³/h"
    if pressao:
        texto += f"\nPressão Total: {pressao} Pa"
    return texto+"\n"+"="*50+"\n"

def multifilar_motor(tipo, tensao, motor, disj_geral):
    if tipo=="Inversor":
        return f"\n--- Multifilar Motor (Inversor) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → Inversor → Motor {motor}CV\n"
    elif tipo=="Direta":
        return f"\n--- Multifilar Motor (Partida Direta) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → Contator → Motor {motor}CV\n"
    elif tipo=="Estrela-Triângulo":
        return f"\n--- Multifilar Motor (Estrela-Triângulo) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → 3 Contatores → Motor {motor}CV\n"
    elif tipo=="Softstarter":
        return f"\n--- Multifilar Motor (Softstarter) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → Softstarter → Motor {motor}CV\n"
    else:
        return ""

def multifilar_resistencia(tensao, qtd, pot_unit, corrente_total):
    return f"\n--- Multifilar Resistências ---\nL1/L2 → Disj Resistência → {qtd}x Resistências {pot_unit}kW → Total Corrente: {corrente_total}A\n"

# =====================================================
# ABAS
# =====================================================

aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais", "🎛️ Simulador",
     "👥 Clientes", "📁 Projetos", "💰 Orçamento"]
)

# =====================================================
# ABA 1 - DADOS
# =====================================================

with aba1:
    col1, col2 = st.columns(2)
    cliente = col1.text_input("Nome do Cliente")
    tecnico = col2.text_input("Nome do Técnico")

    st.divider()
    tipo_partida = st.selectbox(
        "Tipo de Partida",
        ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter", "Somente Resistência"]
    )
    tensao = st.selectbox("Tensão (V)", [220, 380, 440])

    if tipo_partida != "Somente Resistência":
        vazao = st.number_input("Vazão (m³/h)", value=5000.0)
        pressao = st.number_input("Pressão Total (Pa)", value=500.0)
    else:
        vazao = None
        pressao = None

    st.divider()
    st.subheader("🔥 Resistência (Opcional)")
    usar_resistencia = st.checkbox("Adicionar Resistência ao Sistema")
    if usar_resistencia:
        modo_res = st.radio(
            "Modo de Cálculo",
            ["Informar Potência Total", "Informar Quantidade"]
        )
        pot_unit = st.number_input("Potência Unitária (kW)", value=1.75)
        if modo_res == "Informar Potência Total":
            pot_total = st.number_input("Potência Total Desejada (kW)", value=10.5)
        else:
            qtd_res = st.number_input("Quantidade de Resistências", value=6)

    calcular = st.button("🔎 Gerar Projeto", use_container_width=True)

# =====================================================
# PROCESSAMENTO
# =====================================================

if calcular:
    motor_data = None
    res_data = None
    if tipo_partida != "Somente Resistência":
        motor_data = calcular_motor(vazao, tensao, pressao)
    if usar_resistencia:
        if modo_res == "Informar Potência Total":
            res_data = calcular_resistencia_por_potencia(pot_total, pot_unit, tensao)
        else:
            res_data = calcular_resistencia_por_quantidade(qtd_res, pot_unit, tensao)
    st.session_state.update({
        "cliente": cliente,
        "tecnico": tecnico,
        "tipo": tipo_partida,
        "tensao": tensao,
        "vazao": vazao,
        "pressao": pressao,
        "motor": motor_data,
        "res": res_data,
        "pot_unit": pot_unit if usar_resistencia else None
    })
# =====================================================
# ABA 2 - RESULTADO
# =====================================================

with aba2:
    if "motor" in st.session_state and st.session_state["motor"]:

        st.subheader("⚙️ Resultado do Motor")

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]

        st.write(f"Potência do Motor: **{motor} CV**")
        st.write(f"Corrente Nominal: **{corrente} A**")
        st.write(f"Disjuntor Motor: **{disj_motor} A**")
        st.write(f"Disjuntor Geral: **{disj_geral} A**")
        st.write(f"Cabo Recomendado: **{cabo} mm²**")

    if "res" in st.session_state and st.session_state["res"]:

        st.subheader("🔥 Resultado das Resistências")

        qtd, corrente_total, disj_res = st.session_state["res"]

        st.write(f"Quantidade: **{qtd} un**")
        st.write(f"Corrente Total: **{corrente_total} A**")
        st.write(f"Disjuntor Resistência: **{disj_res} A**")


# =====================================================
# ABA 3 - MULTIFILAR
# =====================================================

with aba3:
    if "motor" in st.session_state and st.session_state["motor"]:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]
        texto_motor = multifilar_motor(
            st.session_state["tipo"],
            st.session_state["tensao"],
            motor,
            disj_geral
        )
        st.text(texto_motor)

    if "res" in st.session_state and st.session_state["res"]:
        qtd, corrente_total, disj_res = st.session_state["res"]
        texto_res = multifilar_resistencia(
            st.session_state["tensao"],
            qtd,
            st.session_state["pot_unit"],
            corrente_total
        )
        st.text(texto_res)


# =====================================================
# ABA 4 - MATERIAIS
# =====================================================

with aba4:
    lista = []

    if "motor" in st.session_state and st.session_state["motor"]:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]

        lista.append({"Item": "Disjuntor Geral", "Especificação": f"{disj_geral} A"})
        lista.append({"Item": "Disjuntor Motor", "Especificação": f"{disj_motor} A"})
        lista.append({"Item": "Cabo", "Especificação": f"{cabo} mm²"})
        lista.append({"Item": "Motor", "Especificação": f"{motor} CV"})

        if st.session_state["tipo"] == "Inversor":
            lista.append({"Item": "Inversor de Frequência", "Especificação": f"{motor} CV"})
        elif st.session_state["tipo"] == "Softstarter":
            lista.append({"Item": "Softstarter", "Especificação": f"{motor} CV"})
        elif st.session_state["tipo"] == "Direta":
            lista.append({"Item": "Contator", "Especificação": f"{motor} CV"})
        elif st.session_state["tipo"] == "Estrela-Triângulo":
            lista.append({"Item": "3 Contatores", "Especificação": f"{motor} CV"})

    if "res" in st.session_state and st.session_state["res"]:
        qtd, corrente_total, disj_res = st.session_state["res"]

        lista.append({"Item": "Disjuntor Resistência", "Especificação": f"{disj_res} A"})
        lista.append({"Item": "Resistências", "Especificação": f"{qtd} un"})

    if lista:
        df = pd.DataFrame(lista)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum material calculado ainda.")


# =====================================================
# ABA 5 - SIMULADOR
# =====================================================

with aba5:
    st.subheader("🎛️ Simulação Visual do Motor")

    if "motor" in st.session_state and st.session_state["motor"]:

        fig, ax = plt.subplots()
        circle = plt.Circle((0.5, 0.5), 0.3)
        ax.add_patch(circle)
        ax.set_xlim(0,1)
        ax.set_ylim(0,1)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title("Motor em Operação")

        st.pyplot(fig)

    else:
        st.info("Calcule um projeto para visualizar o simulador.")


# =====================================================
# ABA 6 - CLIENTES
# =====================================================

with aba6:
    st.subheader("👥 Cadastro de Clientes")

    novo_cliente = st.text_input("Nome do Cliente")
    novo_tecnico = st.text_input("Técnico Responsável")

    if st.button("Salvar Cliente"):
        conn = conectar()
        c = conn.cursor()
        c.execute("INSERT INTO clientes (nome, tecnico, data) VALUES (?, ?, ?)",
                  (novo_cliente, novo_tecnico, datetime.now().strftime("%d/%m/%Y")))
        conn.commit()
        conn.close()
        st.success("Cliente salvo com sucesso!")

    conn = conectar()
    df_clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()
    st.dataframe(df_clientes, use_container_width=True)


# =====================================================
# ABA 7 - PROJETOS
# =====================================================

with aba7:
    st.subheader("📁 Histórico de Projetos")

    conn = conectar()
    df_proj = pd.read_sql_query("SELECT * FROM projetos", conn)
    conn.close()

    st.dataframe(df_proj, use_container_width=True)


# =====================================================
# ABA 8 - ORÇAMENTO
# =====================================================

with aba8:
    st.subheader("💰 Orçamento Técnico")

    margem = st.slider("Margem de Lucro (%)", 0, 100, 30)

    valor_base = 0

    if "motor" in st.session_state and st.session_state["motor"]:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]
        valor_base += motor * 500

    if "res" in st.session_state and st.session_state["res"]:
        qtd, corrente_total, disj_res = st.session_state["res"]
        valor_base += qtd * 150

    valor_final = valor_base * (1 + margem/100)

    st.write(f"Valor Base Estimado: R$ {valor_base:,.2f}")
    st.write(f"Valor com Margem: R$ {valor_final:,.2f}")
