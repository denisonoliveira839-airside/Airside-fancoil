import streamlit as st
import math
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AirSide PRO", layout="wide")

st.title("🌀 AirSide PRO")
st.markdown("### Sistema Profissional de Dimensionamento Elétrico")
st.divider()

# =====================================================
# CÁLCULO MOTOR - PADRÃO INDUSTRIAL
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
# MULTIFILAR MOTOR
# =====================================================
def multifilar_motor(tipo_partida, tensao, motor, disj_geral):
    if tipo_partida == "Inversor":
        return f"Inversor {motor}CV conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
    elif tipo_partida == "Direta":
        return f"Contator AC-3 e Relé Térmico conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
    elif tipo_partida == "Estrela-Triângulo":
        return f"3 Contatores AC-3 + Temporizador Y-Δ conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
    elif tipo_partida == "Softstarter":
        return f"Softstarter conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
    else:
        return ""

# =====================================================
# MULTIFILAR RESISTÊNCIA
# =====================================================
def multifilar_resistencia(tensao, qtd, pot_unit, corrente_res):
    return f"{qtd} Resistências {pot_unit}kW ligadas em {tensao}V, Corrente {corrente_res}A\n"

# =====================================================
# LISTA DE MATERIAIS
# =====================================================
def gerar_lista(motor, disj_motor, disj_geral, cabo, tipo_partida, res_data=None, pot_unit=None):
    lista = []
    if motor:
        motor_val, corrente, disj_motor_val, disj_geral_val, cabo_val = motor
        lista.append(("Disjuntor Geral", f"{disj_geral_val}A", "1 un"))
        lista.append(("Motor", f"{motor_val}CV", "1 un"))
        if tipo_partida == "Inversor":
            lista.append(("Inversor", f"{motor_val}CV", "1 un"))
        elif tipo_partida == "Direta":
            lista.append(("Contator", "AC-3", "1 un"))
            lista.append(("Relé Térmico", "Compatível", "1 un"))
        elif tipo_partida == "Estrela-Triângulo":
            lista.append(("3 Contatores", "AC-3", "3 un"))
            lista.append(("Temporizador Y-Δ", "-", "1 un"))
        elif tipo_partida == "Softstarter":
            lista.append(("Softstarter", f"{motor_val}CV", "1 un"))
    if res_data:
        qtd, corrente_res, disj_res = res_data
        lista.append(("Resistência", f"{pot_unit} kW", f"{qtd} un"))
        lista.append(("Disjuntor Resistência", f"{disj_res}A", "1 un"))
    return lista

# =====================================================
# CABEÇALHO MULTIFILAR
# =====================================================
def gerar_cabecalho(cliente, tecnico, tensao, tipo_partida, vazao=None, pressao=None):
    data = datetime.now().strftime("%d/%m/%Y")
    texto = f"""
====================================================
Cliente: {cliente}
Técnico: {tecnico}
Data: {data}
Tipo de Partida: {tipo_partida}
"""
    if vazao:
        texto += f"Vazão: {vazao} m³/h\nPressão: {pressao} Pa\n"
    return texto

# =====================================================
# FUNÇÕES RESISTÊNCIA
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
# ABAS (AGORA COM 5 ABAS)
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

    col3, col4, col5 = st.columns(3)
    tipo_partida = col3.selectbox(
        "Tipo de Partida",
        ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter", "Somente Resistência"]
    )
    tensao = col4.selectbox("Tensão (V)", [220, 380, 440])

    if tipo_partida != "Somente Resistência":
        vazao = col5.number_input("Vazão (m³/h)", value=5000.0)
        pressao = st.number_input("Pressão Total (Pa)", min_value=100.0, value=500.0)

    st.divider()
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
        st.metric("Motor (CV)", motor)
        st.metric("Corrente (A)", corrente)
        st.metric("DJ Motor (A)", disj_motor)
        st.metric("DJ Geral (A)", disj_geral)
        st.metric("Cabo (mm²)", cabo)
    if "res" in st.session_state and st.session_state.res:
        qtd, corrente_res, disj_res = st.session_state.res
        st.metric("Qtd Resistências", qtd)
        st.metric("Corrente Resistência (A)", corrente_res)
        st.metric("DJ Resistência (A)", disj_res)

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
    lista = gerar_lista(
        st.session_state.get("motor"),
        st.session_state.get("motor")[2] if st.session_state.get("motor") else None,
        st.session_state.get("motor")[3] if st.session_state.get("motor") else None,
        st.session_state.get("motor")[4] if st.session_state.get("motor") else None,
        st.session_state.get("tipo"),
        st.session_state.get("res"),
        st.session_state.get("pot_unit")
    )
    if lista:
        df = pd.DataFrame(lista, columns=["Item", "Especificação", "Quantidade"])
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "⬇ Exportar Lista em CSV",
            df.to_csv(index=False),
            file_name="lista_materiais.csv",
            mime="text/csv"
        )

# =====================================================
# ABA 5 - SIMULADOR
# =====================================================
with aba5:
    st.subheader("💨 Simulação de Pressostatos e Ventilador")

    nivel = st.slider("Nível de Sujidade do Filtro", 0, 500, 0)

    p1_ativar = st.number_input("Pressostato 1 - Ativar (nível)", 0, 500, 250)
    p1_desativar = st.number_input("Pressostato 1 - Desativar (nível)", 0, 500, 200)

    p2_ativar = st.number_input("Pressostato 2 - Ativar (nível)", 0, 500, 400)
    p2_desativar = st.number_input("Pressostato 2 - Desativar (nível)", 0, 500, 350)

    st.subheader("🔹 Status Atual")

    pressostato1 = nivel >= p1_ativar
    if nivel <= p1_desativar:
        pressostato1 = False

    pressostato2 = nivel >= p2_ativar
    if nivel <= p2_desativar:
        pressostato2 = False

    st.markdown(f"- Pressostato 1: {'🟢 Ativado' if pressostato1 else '🔴 Desligado'}")
    st.markdown(f"- Pressostato 2: {'🟢 Ativado' if pressostato2 else '🔴 Desligado'}")

    ventilador_status = "🟢 Ligado"
    if pressostato1 or pressostato2:
        ventilador_status = "🔴 Desligado"

    st.markdown(f"- Ventilador: {ventilador_status}")
