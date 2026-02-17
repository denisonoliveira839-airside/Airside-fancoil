import streamlit as st
import math
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AirSide PRO", layout="wide")

st.title("🌀 AirSide PRO")
st.markdown("### Sistema Profissional de Dimensionamento Elétrico")
st.divider()

# =====================================================
# FUNÇÕES DE CÁLCULO
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


def calcular_resistencias(total_kw, unidade_kw):
    qtd = math.ceil(total_kw / unidade_kw)
    corrente_total = round((total_kw * 1000) / 380, 2)  # Corrente trifásica simplificada
    disj_resistencia = math.ceil(corrente_total * 1.25)
    return qtd, corrente_total, disj_resistencia


def gerar_multifilar(tipo_partida, tensao, motor, corrente, cliente, tecnico, qtd_res=0, unidade_res_kw=0):
    data = datetime.now().strftime("%d/%m/%Y")
    res_linha = ""
    if qtd_res > 0:
        res_linha = f"\nResistências: {qtd_res} x {unidade_res_kw}kW\nDJ Resistência: Calculado automaticamente\n"

    if tipo_partida == "Inversor":
        diagrama = f"""
====================================================
               DIAGRAMA MULTIFILAR
====================================================
Cliente: {cliente}
Técnico: {tecnico}
Data: {data}

REDE {tensao}V ── DJ Geral ── Inversor ── Motor {motor}CV
U ── Motor U
V ── Motor V
W ── Motor W
{res_linha}
====================================================
"""
    elif tipo_partida == "Partida Direta":
        diagrama = f"""
====================================================
               DIAGRAMA MULTIFILAR
====================================================
Cliente: {cliente}
Técnico: {tecnico}
Data: {data}

REDE {tensao}V ── DJ Geral ── Contator ── Motor {motor}CV
Termostato de Segurança em Série
{res_linha}
====================================================
"""
    elif tipo_partida == "Estrela-Triângulo":
        diagrama = f"""
====================================================
               DIAGRAMA MULTIFILAR
====================================================
Cliente: {cliente}
Técnico: {tecnico}
Data: {data}

REDE {tensao}V ── DJ Geral
          ├─ Contator Principal
          ├─ Contator Estrela
          ├─ Contator Triângulo
          └─ Temporizador Y-Δ
          └─ Motor {motor}CV
{res_linha}
====================================================
"""
    elif tipo_partida == "Softstarter":
        diagrama = f"""
====================================================
               DIAGRAMA MULTIFILAR
====================================================
Cliente: {cliente}
Técnico: {tecnico}
Data: {data}

REDE {tensao}V ── DJ Geral ── Softstarter ── Contator Bypass ── Motor {motor}CV
{res_linha}
====================================================
"""
    else:
        diagrama = "Tipo de partida inválido."

    return diagrama


def gerar_lista(motor, disj_motor, disj_geral, cabo, qtd_res=0, unidade_res_kw=0):
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
        lista.append(("Resistência", f"{unidade_res_kw}kW", f"{qtd_res} un"))
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
    tipo_partida = st.selectbox("Tipo de Partida", ["Inversor", "Partida Direta", "Estrela-Triângulo", "Softstarter"])
    st.divider()

    col6, col7 = st.columns(2)
    total_res = col6.number_input("Potência Total Resistências (kW)", min_value=0.0, value=0.0)
    unidade_res = col7.number_input("Potência Unitária Resistência (kW)", min_value=0.0, value=0.0)

    calcular = st.button("🔎 Calcular Sistema", use_container_width=True)

if "resultado" not in st.session_state:
    st.session_state.resultado = None

if calcular:
    st.session_state.resultado = calcular_motor(vazao, tensao, pressao)
    st.session_state.cliente = cliente
    st.session_state.tecnico = tecnico
    st.session_state.tensao = tensao
    st.session_state.tipo_partida = tipo_partida
    if total_res > 0 and unidade_res > 0:
        st.session_state.qtd_res, st.session_state.corrente_res, st.session_state.dj_res = calcular_resistencias(total_res, unidade_res)
        st.session_state.total_res = total_res
        st.session_state.unidade_res = unidade_res
    else:
        st.session_state.qtd_res, st.session_state.corrente_res, st.session_state.dj_res = 0,0,0
        st.session_state.total_res, st.session_state.unidade_res = 0,0

# =====================================================
# ABA 2 - RESULTADO
# =====================================================
with aba2:
    if st.session_state.resultado:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.resultado
        st.success("✅ Sistema dimensionado com padrão industrial")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("⚙ Motor", f"{motor} CV")
        col2.metric("🔌 Corrente", f"{corrente} A")
        col3.metric("🛡 DJ Motor", f"{disj_motor} A")
        col4.metric("⚡ DJ Geral", f"{disj_geral} A")
        col5.metric("🧵 Cabo", f"{cabo} mm²")
        if st.session_state.qtd_res > 0:
            st.metric("🔥 Resistências", f"{st.session_state.qtd_res} un | {st.session_state.total_res} kW")

# =====================================================
# ABA 3 - MULTIFILAR
# =====================================================
with aba3:
    if st.session_state.resultado:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.resultado
        st.code(
            gerar_multifilar(
                st.session_state.tipo_partida,
                st.session_state.tensao,
                motor,
                corrente,
                st.session_state.cliente,
                st.session_state.tecnico,
                st.session_state.qtd_res,
                st.session_state.unidade_res
            ),
            language="text"
        )

# =====================================================
# ABA 4 - MATERIAIS
# =====================================================
with aba4:
    if st.session_state.resultado:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.resultado
        lista = gerar_lista(
            motor, disj_motor, disj_geral, cabo,
            st.session_state.qtd_res, st.session_state.unidade_res
        )
        df = pd.DataFrame(lista, columns=["Item", "Especificação", "Quantidade"])
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇ Exportar Lista em CSV",
            df.to_csv(index=False),
            file_name="lista_materiais.csv",
            mime="text/csv"
        )
