import streamlit as st
import math
from datetime import datetime

st.set_page_config(page_title="AirSide PRO", layout="centered")

st.title("🌀 AirSide PRO - Dimensionamento Elétrico")

# =====================================================
# CÁLCULO MOTOR
# =====================================================
def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):

    potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
    potencia_kw *= 1.15

    potencia_cv = potencia_kw / 0.736
    potencia_motor = max(1, math.ceil(potencia_cv))

    corrente = round(
        (potencia_kw * 1000) / (math.sqrt(3) * tensao * 0.85),
        2
    )

    disj_motor = max(2, math.ceil(corrente * 1.25))
    disj_geral = max(6, math.ceil(disj_motor * 1.2))

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
# MULTIFILAR TÉCNICO COMPLETO
# =====================================================
def gerar_multifilar(tensao, motor, corrente, cliente, tecnico):

    data = datetime.now().strftime("%d/%m/%Y")

    return f"""
====================================================
               DIAGRAMA MULTIFILAR
====================================================

Cliente: {cliente}
Técnico: {tecnico}
Data: {data}

================ POTÊNCIA =================

REDE TRIFÁSICA {tensao}V

L1 ───── Disj Geral ───── Contator (1)
                                  (2) ───── Inversor R
L2 ───── Disj Geral ───── Contator (3)
                                  (4) ───── Inversor S
L3 ───── Disj Geral ───── Contator (5)
                                  (6) ───── Inversor T

Inversor de Frequência

U ───────────────────────── Motor U
V ───────────────────────── Motor V
W ───────────────────────── Motor W

Motor Trifásico {motor} CV
Corrente Nominal: {corrente} A

================ COMANDO 24Vcc =================

Fase ─── Disjuntor Comando ─── Fonte 24Vcc

+24V ─── Botão LIGA (NA) ───┐
                              ├── Entrada I1 CLP
+24V ─── Pressostato 1 ──────┤
+24V ─── Pressostato 2 ──────┘

CLP Saída Q1 ─── Contator A1
Neutro/0V ─────── Contator A2

Contato Auxiliar Contator 13-14 → Realimentação CLP

====================================================
"""


# =====================================================
# LISTA DE MATERIAIS COM SUGESTÃO
# =====================================================
def gerar_lista(motor, disj_motor, disj_geral, cabo):

    return [
        ("Disjuntor Geral", f"{disj_geral}A Tripolar", "1 un"),
        ("Disjuntor Motor", f"{disj_motor}A Curva C", "1 un"),
        ("Contator", f"{motor}CV categoria AC-3", "1 un"),
        ("Inversor Sugerido", f"WEG CFW300 {motor}CV", "1 un"),
        ("Alternativa Inversor", f"Siemens V20 {motor}CV", "1 un"),
        ("CLP Sugerido", "WEG CLIC02 24Vcc", "1 un"),
        ("Alternativa CLP", "Siemens LOGO 24RCE", "1 un"),
        ("Fonte 24Vcc", "2A ou superior", "1 un"),
        ("Pressostato Industrial", "Contato NA/NF", "2 un"),
        ("Cabo Potência", f"{cabo} mm²", "Conforme projeto"),
        ("Cabo Comando", "1,5 mm²", "Conforme projeto"),
        ("Bornes 2,5mm", "Trilho DIN", "Conforme necessidade"),
        ("Painel IP54", "Metálico", "1 un"),
    ]


# =====================================================
# ABAS
# =====================================================
aba1, aba2, aba3, aba4 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais"]
)

with aba1:

    cliente = st.text_input("Nome do Cliente")
    tecnico = st.text_input("Nome do Técnico")

    vazao = st.number_input("Vazão (m³/h)", min_value=100.0, value=5000.0)
    tensao = st.selectbox("Tensão (V)", [220, 380, 440])
    pressao = st.number_input("Pressão Total (Pa)", min_value=100.0, value=500.0)

    calcular = st.button("🔎 Calcular Sistema")

if "resultado" not in st.session_state:
    st.session_state.resultado = None

if calcular:
    st.session_state.resultado = calcular_motor(vazao, tensao, pressao)
    st.session_state.cliente = cliente
    st.session_state.tecnico = tecnico
    st.session_state.tensao = tensao


with aba2:

    if st.session_state.resultado:

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.resultado

        st.write(f"Motor: {motor} CV")
        st.write(f"Corrente: {corrente} A")
        st.write(f"Disjuntor Motor: {disj_motor} A")
        st.write(f"Disjuntor Geral: {disj_geral} A")
        st.write(f"Cabo Potência: {cabo} mm²")


with aba3:

    if st.session_state.resultado:

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.resultado

        st.text(
            gerar_multifilar(
                st.session_state.tensao,
                motor,
                corrente,
                st.session_state.cliente,
                st.session_state.tecnico,
            )
        )


with aba4:

    if st.session_state.resultado:

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.resultado

        lista = gerar_lista(motor, disj_motor, disj_geral, cabo)

        for item in lista:
            st.write(f"🔹 {item[0]} | {item[1]} | {item[2]}")
