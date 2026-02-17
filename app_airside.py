import streamlit as st
import math
from datetime import datetime

st.set_page_config(page_title="AirSide - Ventilação Industrial", layout="centered")

st.title("🌀 AirSide - Dimensionamento Elétrico de Ventiladores")

# =====================================================
# FUNÇÕES
# =====================================================

def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):

    try:
        vazao = float(vazao)
        pressao_total = float(pressao_total)
        rendimento = float(rendimento)
        tensao_int = int(tensao)

        if vazao <= 0:
            vazao = 100

        if pressao_total <= 0:
            pressao_total = 500

        if rendimento <= 0:
            rendimento = 0.65

        potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
        potencia_kw *= 1.15

        potencia_cv = potencia_kw / 0.736
        potencia_motor = max(1, math.ceil(potencia_cv))

        corrente = round(
            (potencia_kw * 1000) / (math.sqrt(3) * tensao_int * 0.85),
            2
        )

        disj_motor = max(2, math.ceil(corrente * 1.25))
        disj_geral = max(6, math.ceil(disj_motor * 1.2))

        if corrente <= 18:
            cabo_motor = 2.5
        elif corrente <= 28:
            cabo_motor = 4
        elif corrente <= 36:
            cabo_motor = 6
        elif corrente <= 50:
            cabo_motor = 10
        else:
            cabo_motor = 16

        return potencia_motor, corrente, disj_motor, disj_geral, cabo_motor

    except:
        return 1, 0, 10, 16, 2.5


def gerar_unifilar(tensao, disj_geral, disj_motor, motor, cliente, tecnico):

    data = datetime.now().strftime("%d/%m/%Y")

    return f"""
==============================
      DIAGRAMA UNIFILAR
==============================

Cliente: {cliente}
Técnico: {tecnico}
Data: {data}

REDE TRIFÁSICA {tensao}V
        │
   Disjuntor Geral {disj_geral}A
        │
   Inversor de Frequência
        │
   Disjuntor Motor {disj_motor}A
        │
      Motor {motor} CV
"""


def gerar_multifilar(tensao, motor, corrente, cliente, tecnico):

    data = datetime.now().strftime("%d/%m/%Y")

    return f"""
==========================================
          DIAGRAMA MULTIFILAR
==========================================

Cliente: {cliente}
Técnico: {tecnico}
Data: {data}

ALIMENTAÇÃO {tensao}V

L1 ─── Disj Geral ─── Inversor ─── Disj Motor ───┐
L2 ─── Disj Geral ─── Inversor ─── Disj Motor ───┼── Motor {motor} CV
L3 ─── Disj Geral ─── Inversor ─── Disj Motor ───┘

Corrente Nominal: {corrente} A

COMANDO 24Vcc

Fonte 24Vcc
   ├── CLP
   │     ├── Pressostato 1
   │     ├── Pressostato 2
   │     └── RUN → Inversor
"""


# =====================================================
# ABAS
# =====================================================

aba1, aba2, aba3 = st.tabs(["📋 Dados", "📊 Resultado", "📑 Diagramas"])

# =========================
# ABA 1 - DADOS
# =========================
with aba1:

    cliente = st.text_input("Nome do Cliente")
    tecnico = st.text_input("Nome do Técnico")

    vazao = st.number_input("Vazão (m³/h)", min_value=100.0, value=5000.0)
    tensao = st.selectbox("Tensão (V)", [220, 380, 440])
    pressao = st.number_input("Pressão Total (Pa)", min_value=100.0, value=500.0)

    calcular = st.button("🔎 Calcular Sistema")


# =========================
# PROCESSAMENTO
# =========================
if "resultado" not in st.session_state:
    st.session_state.resultado = None

if calcular:
    st.session_state.resultado = calcular_motor(vazao, tensao, pressao)
    st.session_state.cliente = cliente
    st.session_state.tecnico = tecnico
    st.session_state.tensao = tensao


# =========================
# ABA 2 - RESULTADO
# =========================
with aba2:

    if st.session_state.resultado:

        motor, corrente, disj_motor, disj_geral, cabo_motor = st.session_state.resultado

        st.markdown("## 🔧 Resultado Técnico")
        st.write(f"**Motor:** {motor} CV")
        st.write(f"**Corrente:** {corrente} A")
        st.write(f"**Disjuntor Motor:** {disj_motor} A")
        st.write(f"**Disjuntor Geral:** {disj_geral} A")
        st.write(f"**Cabo:** {cabo_motor} mm²")
        st.write("**Sistema:** Inversor de Frequência")
        st.write("**Automação:** CLP + 2 Pressostatos")
    else:
        st.info("Preencha os dados na aba 'Dados' e clique em Calcular.")


# =========================
# ABA 3 - DIAGRAMAS
# =========================
with aba3:

    if st.session_state.resultado:

        motor, corrente, disj_motor, disj_geral, cabo_motor = st.session_state.resultado

        st.markdown("## 📊 Unifilar")
        st.text(
            gerar_unifilar(
                st.session_state.tensao,
                disj_geral,
                disj_motor,
                motor,
                st.session_state.cliente,
                st.session_state.tecnico,
            )
        )

        st.markdown("## 📊 Multifilar")
        st.text(
            gerar_multifilar(
                st.session_state.tensao,
                motor,
                corrente,
                st.session_state.cliente,
                st.session_state.tecnico,
            )
        )
    else:
        st.info("Calcule o sistema primeiro.")
