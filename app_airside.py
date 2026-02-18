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
    corrente = round((potencia_kw * 1000) / (math.sqrt(3) * tensao * 0.85), 2)
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
# CÁLCULO RESISTÊNCIA
# =====================================================
def calcular_resistencia_por_potencia(pot_total, pot_unit, tensao):
    qtd = math.ceil(pot_total / pot_unit)
    corrente_res = round((pot_unit * 1000) / tensao, 2)
    disj_res = math.ceil(corrente_res * 1.25)
    return qtd, corrente_res, disj_res

def calcular_resistencia_por_quantidade(qtd, pot_unit, tensao):
    corrente_res = round((pot_unit * 1000) / tensao, 2)
    disj_res = math.ceil(corrente_res * 1.25)
    return qtd, corrente_res, disj_res

# =====================================================
# MULTIFILAR
# =====================================================
def gerar_cabecalho(cliente, tecnico, tensao, tipo, vazao, pressao):
    data = datetime.now().strftime("%d/%m/%Y")
    return f"Cliente: {cliente}\nTécnico: {tecnico}\nData: {data}\nTensão: {tensao}V\nTipo: {tipo}\nVazão: {vazao} m³/h\nPressão: {pressao} Pa\n\n"

def multifilar_motor(tipo, tensao, motor, disj_geral):
    if tipo == "Inversor":
        return f"Diagrama Motor com Inversor {motor}CV, DJ Geral {disj_geral}A\n"
    elif tipo == "Direta":
        return f"Diagrama Motor Partida Direta {motor}CV, DJ Geral {disj_geral}A\n"
    elif tipo == "Estrela-Triângulo":
        return f"Diagrama Motor Estrela-Triângulo {motor}CV, DJ Geral {disj_geral}A\n"
    elif tipo == "Softstarter":
        return f"Diagrama Motor Softstarter {motor}CV, DJ Geral {disj_geral}A\n"
    return ""

def multifilar_resistencia(tensao, qtd, pot_unit, corrente_res):
    return f"Diagrama Resistência {qtd}x{pot_unit}kW, Corrente {corrente_res}A\n"

# =====================================================
# ABAS
# =====================================================
aba1, aba2, aba3, aba4, aba5 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais", "🎛️ Simulador"]
)

# =====================================================
# ABA 1 - DADOS
# =====================================================
with aba1:
    col1, col2 = st.columns(2)
    cliente = col1.text_input("Nome do Cliente")
    tecnico = col2.text_input("Nome do Técnico")

    tipo_partida = st.selectbox(
        "Tipo de Partida",
        ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter", "Somente Resistência"]
    )

    tensao = st.selectbox("Tensão (V)", [220, 380, 440])

    if tipo_partida != "Somente Resistência":
        vazao = st.number_input("Vazão (m³/h)", value=5000.0)
        pressao = st.number_input("Pressão Total (Pa)", value=500.0)

    st.subheader("🔥 Resistência (Opcional)")
    usar_resistencia = st.checkbox("Adicionar Resistência ao Sistema")

    if usar_resistencia:
        modo_res = st.radio("Modo de Cálculo", ["Informar Potência Total", "Informar Quantidade"])
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
        "vazao": vazao if tipo_partida != "Somente Resistência" else None,
        "pressao": pressao if tipo_partida != "Somente Resistência" else None,
        "motor": motor_data,
        "res": res_data,
        "pot_unit": pot_unit if usar_resistencia else None
    })

# =====================================================
# ABA 2 - RESULTADO
# =====================================================
with aba2:
    if "motor" in st.session_state and st.session_state.motor:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.motor
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Motor (CV)", motor)
        col2.metric("Corrente (A)", corrente)
        col3.metric("DJ Motor (A)", disj_motor)
        col4.metric("DJ Geral (A)", disj_geral)
        col5.metric("Cabo (mm²)", cabo)

    if "res" in st.session_state and st.session_state.res:
        qtd, corrente_res, disj_res = st.session_state.res
        col1, col2, col3 = st.columns(3)
        col1.metric("Qtd Resistências", qtd)
        col2.metric("Corrente Resistência (A)", corrente_res)
        col3.metric("DJ Resistência (A)", disj_res)

# =====================================================
# ABA 3 - MULTIFILAR
# =====================================================
with aba3:
    if "tipo" in st.session_state:
        cabecalho = gerar_cabecalho(
            st.session_state.cliente,
            st.session_state.tecnico,
            st.session_state.tensao,
            st.session_state.tipo,
            st.session_state.vazao,
            st.session_state.pressao
        )
        texto = cabecalho
        if st.session_state.motor:
            motor, corrente, disj_motor, disj_geral, cabo = st.session_state.motor
            texto += multifilar_motor(st.session_state.tipo, st.session_state.tensao, motor, disj_geral)
        if st.session_state.res:
            qtd, corrente_res, disj_res = st.session_state.res
            texto += multifilar_resistencia(st.session_state.tensao, qtd, st.session_state.pot_unit, corrente_res)
        st.code(texto, language="text")

# =====================================================
# ABA 4 - MATERIAIS
# =====================================================
with aba4:
    lista = []
    if "motor" in st.session_state and st.session_state.motor:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.motor
        lista.append(("Disjuntor Geral", f"{disj_geral}A", "1 un"))
        lista.append(("Motor", f"{motor}CV", "1 un"))
        if st.session_state.tipo == "Inversor":
            lista.append(("Inversor", f"{motor}CV", "1 un"))
        elif st.session_state.tipo == "Direta":
            lista.append(("Contator", "AC-3", "1 un"))
            lista.append(("Relé Térmico", "Compatível", "1 un"))
        elif st.session_state.tipo == "Estrela-Triângulo":
            lista.append(("3 Contatores", "AC-3", "3 un"))
            lista.append(("Temporizador Y-Δ", "-", "1 un"))
        elif st.session_state.tipo == "Softstarter":
            lista.append(("Softstarter", f"{motor}CV", "1 un"))
    if "res" in st.session_state and st.session_state.res:
        qtd, corrente_res, disj_res = st.session_state.res
        lista.append(("Resistência", f"{st.session_state.pot_unit} kW", f"{qtd} un"))
        lista.append(("Disjuntor Resistência", f"{disj_res}A", "1 un"))
    if lista:
        df = pd.DataFrame(lista, columns=["Item", "Especificação", "Quantidade"])
        st.dataframe(df, use_container_width=True)

# =====================================================
# ABA 5 - SIMULADOR CLP PRESSOSTATOS
# =====================================================
with aba5:
    st.subheader("💨 Simulação de Pressostatos e Ventilador")
    nivel = st.slider("Nível de Sujidade do Filtro (0-500)", 0, 500, 0)
    p1_atu = st.number_input("Pressostato 1 Atuação (%)", min_value=0, max_value=100, value=80)
    p2_atu = st.number_input("Pressostato 2 Atuação (%)", min_value=0, max_value=100, value=90)

    st.subheader("🔹 Status Atual")
    if nivel >= p1_atu * 5:
        st.markdown("- Pressostato 1: 🟢 Ativado")
    else:
        st.markdown("- Pressostato 1: 🔴 Desligado")

    if nivel >= p2_atu * 5:
        st.markdown("- Pressostato 2: 🟢 Ativado")
    else:
        st.markdown("- Pressostato 2: 🔴 Desligado")

    ventilador_status = "🟢 Ligado" if nivel < 500 else "🔴 Desligado"
    st.markdown(f"- Ventilador: {ventilador_status}")
