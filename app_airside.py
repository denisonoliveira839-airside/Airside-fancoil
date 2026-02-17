import streamlit as st
import math
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AirSide PRO", layout="wide")

st.title("🌀 AirSide PRO")
st.markdown("### Sistema Profissional de Dimensionamento Elétrico")
st.divider()

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

    disj_motor = math.ceil(corrente * 1.25)
    disj_geral = math.ceil(disj_motor * 1.3)

    if disj_geral < 10:
        disj_geral = 10

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
# CÁLCULO RESISTÊNCIAS
# =====================================================
def calcular_resistencias(pot_total_kw, tensao, pot_res_individual_kw):

    if pot_total_kw <= 0 or pot_res_individual_kw <= 0:
        return 0, 0, 0

    quantidade = math.ceil(pot_total_kw / pot_res_individual_kw)

    corrente_total = round(
        (pot_total_kw * 1000) / (math.sqrt(3) * tensao),
        2
    )

    disj_res = math.ceil(corrente_total * 1.25)

    return quantidade, corrente_total, disj_res


# =====================================================
# MULTIFILAR
# =====================================================
def gerar_multifilar(tensao, motor, corrente, disj_geral, cliente, tecnico):

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

L1 ── Disj Geral {disj_geral}A ── Contator 1 ──┐
L2 ── Disj Geral {disj_geral}A ── Contator 3 ──┼── Inversor
L3 ── Disj Geral {disj_geral}A ── Contator 5 ──┘

Contator 2 ───────── Inversor R
Contator 4 ───────── Inversor S
Contator 6 ───────── Inversor T

Inversor U ───────── Motor U
Inversor V ───────── Motor V
Inversor W ───────── Motor W

Motor Trifásico {motor} CV
Corrente Nominal: {corrente} A

================ COMANDO 24Vcc =================

Fase ── Disj Comando ── Fonte 24Vcc

+24V ── Botão LIGA (NA) ──┐
                          ├─ I1 CLP
+24V ── Pressostato 1 ────┤
+24V ── Pressostato 2 ────┘

Q1 CLP ── A1 Contator
0V ─────── A2 Contator

Contato 13-14 → Realimentação CLP

====================================================
"""


# =====================================================
# LISTA DE MATERIAIS
# =====================================================
def gerar_lista(motor, disj_motor, disj_geral, cabo,
                qtd_res, disj_res, corrente_res):

    lista = [
        ("Disjuntor Geral", f"{disj_geral}A Tripolar", "1 un"),
        ("Disjuntor Motor", f"{disj_motor}A Curva C", "1 un"),
        ("Contator", f"{motor}CV categoria AC-3", "1 un"),
        ("Inversor Sugerido", f"WEG CFW300 {motor}CV", "1 un"),
        ("CLP", "WEG CLIC02 24Vcc", "1 un"),
        ("Fonte 24Vcc", "2A ou superior", "1 un"),
        ("Pressostato Industrial", "Contato NA/NF", "2 un"),
        ("Cabo Potência Motor", f"{cabo} mm²", "Conforme projeto"),
    ]

    if qtd_res > 0:
        lista.extend([
            ("Resistência Elétrica", f"{qtd_res} unidades", f"{qtd_res} un"),
            ("Disjuntor Resistência", f"{disj_res}A Tripolar", "1 un"),
            ("Corrente Total Resistências", f"{corrente_res} A", "-"),
        ])

    return lista


# =====================================================
# ABAS
# =====================================================
aba1, aba2, aba3, aba4 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais"]
)

# =====================================================
# ABA 1 - DADOS
# =====================================================
with aba1:

    col1, col2 = st.columns(2)
    cliente = col1.text_input("Nome do Cliente")
    tecnico = col2.text_input("Nome do Técnico")

    st.divider()

    col3, col4, col5 = st.columns(3)
    vazao = col3.number_input("Vazão (m³/h)", min_value=100.0, value=5000.0)
    tensao = col4.selectbox("Tensão (V)", [220, 380, 440])
    pressao = col5.number_input("Pressão Total (Pa)", min_value=100.0, value=500.0)

    st.divider()
    st.subheader("🔥 Resistências Elétricas (Opcional)")

    col6, col7 = st.columns(2)
    pot_total_res = col6.number_input("Potência Total Necessária (kW)", min_value=0.0, value=0.0)
    pot_individual = col7.number_input("Potência por Resistência (kW)", min_value=0.0, value=0.0)

    calcular = st.button("🔎 Calcular Sistema", use_container_width=True)


if "resultado" not in st.session_state:
    st.session_state.resultado = None

if calcular:
    st.session_state.resultado = calcular_motor(vazao, tensao, pressao)
    st.session_state.resistencias = calcular_resistencias(
        pot_total_res, tensao, pot_individual
    )
    st.session_state.cliente = cliente
    st.session_state.tecnico = tecnico
    st.session_state.tensao = tensao


# =====================================================
# ABA 2 - RESULTADO
# =====================================================
with aba2:

    if st.session_state.resultado:

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.resultado
        qtd_res, corrente_res, disj_res = st.session_state.resistencias

        st.success("✅ Sistema dimensionado com padrão industrial")

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("⚙ Motor", f"{motor} CV")
        col2.metric("🔌 Corrente", f"{corrente} A")
        col3.metric("🛡 DJ Motor", f"{disj_motor} A")
        col4.metric("⚡ DJ Geral", f"{disj_geral} A")
        col5.metric("🧵 Cabo", f"{cabo} mm²")

        if qtd_res > 0:
            st.divider()
            st.subheader("🔥 Resistências")

            col6, col7, col8 = st.columns(3)
            col6.metric("Qtd Resistências", qtd_res)
            col7.metric("Corrente Total", f"{corrente_res} A")
            col8.metric("DJ Resistência", f"{disj_res} A")


# =====================================================
# ABA 3 - MULTIFILAR
# =====================================================
with aba3:

    if st.session_state.resultado:

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.resultado

        st.code(
            gerar_multifilar(
                st.session_state.tensao,
                motor,
                corrente,
                disj_geral,
                st.session_state.cliente,
                st.session_state.tecnico,
            ),
            language="text"
        )


# =====================================================
# ABA 4 - MATERIAIS
# =====================================================
with aba4:

    if st.session_state.resultado:

        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.resultado
        qtd_res, corrente_res, disj_res = st.session_state.resistencias

        lista = gerar_lista(
            motor, disj_motor, disj_geral, cabo,
            qtd_res, disj_res, corrente_res
        )

        df = pd.DataFrame(lista, columns=["Item", "Especificação", "Quantidade"])

        st.dataframe(df, use_container_width=True)

        st.download_button(
            "⬇ Exportar Lista em CSV",
            df.to_csv(index=False),
            file_name="lista_materiais.csv",
            mime="text/csv"
        )
