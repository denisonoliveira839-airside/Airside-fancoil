import streamlit as st
import math
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AirSide PRO", layout="wide")
st.title("🌀 AirSide PRO - Dimensionamento Elétrico")
st.markdown("### Sistema Profissional de Dimensionamento Elétrico")
st.divider()

# ==============================
# FUNÇÕES DE CÁLCULO
# ==============================
def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):
    potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
    potencia_kw *= 1.15
    potencia_cv = potencia_kw / 0.736
    potencia_motor = max(1, math.ceil(potencia_cv))

    corrente = round((potencia_kw * 1000) / (math.sqrt(3) * tensao * 0.85), 2)
    disj_motor = math.ceil(corrente * 1.25)
    disj_geral = max(10, math.ceil(disj_motor * 1.3))

    # Cabo simplificado
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

def calcular_resistencias(corrente_total, corrente_unit=1750):
    qtd = math.ceil(corrente_total / corrente_unit)
    return qtd, corrente_unit

def gerar_multifilar(tensao, motor, corrente, cliente, tecnico, tipo_partida, qtd_res, corrente_unit):
    data = datetime.now().strftime("%d/%m/%Y")
    multifilar = f"""
====================================================
               DIAGRAMA MULTIFILAR
====================================================

Cliente: {cliente}
Técnico: {tecnico}
Data: {data}

================ POTÊNCIA =================
REDE TRIFÁSICA {tensao}V
Motor: {motor} CV
Corrente Nominal: {corrente} A
Tipo de Partida: {tipo_partida}

"""
    if tipo_partida == "Inversor":
        multifilar += f"""
L1 ── Disj Geral ── Contator ── Inversor → Motor U
L2 ── Disj Geral ── Contator ── Inversor → Motor V
L3 ── Disj Geral ── Contator ── Inversor → Motor W
"""
    elif tipo_partida == "Estrela-Triângulo":
        multifilar += f"""
L1 ── Disj Geral ── Contator Estrela ── Motor
L2 ── Disj Geral ── Contator Estrela ── Motor
L3 ── Disj Geral ── Contator Estrela ── Motor

Após tempo definido:
Contator Triângulo liga Motor em Triângulo
"""
    else:  # Direta ou SoftStart
        multifilar += f"""
L1 ── Disj Geral ── Motor
L2 ── Disj Geral ── Motor
L3 ── Disj Geral ── Motor
"""

    if qtd_res > 0:
        multifilar += f"""
================ RESISTÊNCIAS =================
Quantidade: {qtd_res} un
Potência Unitária: {corrente_unit} W
Ligação de acordo com tensão {tensao}V
"""
    multifilar += "===================================================="
    return multifilar

def gerar_lista(motor, disj_motor, disj_geral, cabo, qtd_res, corrente_unit):
    lista = [
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
    if qtd_res > 0:
        lista.append(("Resistência", f"{corrente_unit} W", f"{qtd_res} un"))
    return lista

# ==============================
# ABAS
# ==============================
aba1, aba2, aba3, aba4 = st.tabs(["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais"])

# ==============================
# ABA 1 - DADOS
# ==============================
with aba1:
    col1, col2 = st.columns(2)
    cliente = col1.text_input("Nome do Cliente")
    tecnico = col2.text_input("Nome do Técnico")
    st.divider()
    col3, col4, col5 = st.columns(3)
    vazao = col3.number_input("Vazão (m³/h)", min_value=100.0, value=5000.0)
    tensao = col4.selectbox("Tensão (V)", [220, 380, 440])
    pressao = col5.number_input("Pressão Total (Pa)", min_value=100.0, value=500.0)
    tipo_partida = st.selectbox("Tipo de Partida", ["Direta", "Estrela-Triângulo", "SoftStart", "Inversor"])
    pot_resistencia = st.number_input("Total Resistências (W)", min_value=0, value=0)
    corrente_unit = st.number_input("Potência Unitária (W)", min_value=0, value=1750)
    calcular = st.button("🔎 Calcular Sistema", use_container_width=True)

if "resultado" not in st.session_state:
    st.session_state.resultado = None

if calcular:
    motor, corrente, disj_motor, disj_geral, cabo = calcular_motor(vazao, tensao, pressao)
    qtd_res, corrente_unit_calc = calcular_resistencias(pot_resistencia, corrente_unit)
    st.session_state.resultado = (motor, corrente, disj_motor, disj_geral, cabo, qtd_res, corrente_unit_calc)
    st.session_state.cliente = cliente
    st.session_state.tecnico = tecnico
    st.session_state.tensao = tensao
    st.session_state.tipo_partida = tipo_partida

# ==============================
# ABA 2 - RESULTADO
# ==============================
with aba2:
    if st.session_state.resultado:
        motor, corrente, disj_motor, disj_geral, cabo, qtd_res, corrente_unit_calc = st.session_state.resultado
        st.success("✅ Sistema dimensionado com padrão industrial")
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        col1.metric("⚙ Motor", f"{motor} CV")
        col2.metric("🔌 Corrente", f"{corrente} A")
        col3.metric("🛡 DJ Motor", f"{disj_motor} A")
        col4.metric("⚡ DJ Geral", f"{disj_geral} A")
        col5.metric("🧵 Cabo", f"{cabo} mm²")
        col6.metric("🔥 Qtd Resistências", f"{qtd_res} un")
        col7.metric("💡 Potência Unitária", f"{corrente_unit_calc} W")

# ==============================
# ABA 3 - MULTIFILAR
# ==============================
with aba3:
    if st.session_state.resultado:
        motor, corrente, disj_motor, disj_geral, cabo, qtd_res, corrente_unit_calc = st.session_state.resultado
        st.code(
            gerar_multifilar(
                st.session_state.tensao,
                motor,
                corrente,
                st.session_state.cliente,
                st.session_state.tecnico,
                st.session_state.tipo_partida,
                qtd_res,
                corrente_unit_calc
            ),
            language="text"
        )

# ==============================
# ABA 4 - MATERIAIS
# ==============================
with aba4:
    if st.session_state.resultado:
        motor, corrente, disj_motor, disj_geral, cabo, qtd_res, corrente_unit_calc = st.session_state.resultado
        lista = gerar_lista(motor, disj_motor, disj_geral, cabo, qtd_res, corrente_unit_calc)
        df = pd.DataFrame(lista, columns=["Item", "Especificação", "Quantidade"])
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇ Exportar Lista em CSV",
            df.to_csv(index=False),
            file_name="lista_materiais.csv",
            mime="text/csv"
        )
