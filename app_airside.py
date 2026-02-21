import streamlit as st
import math

st.set_page_config(layout="wide")

st.title("🏭 Plataforma Interna - Engenharia Fancoil")

# =========================
# FUNÇÕES DE CÁLCULO
# =========================

def corrente_trifasica(potencia_kw, tensao):
    return (potencia_kw * 1000) / (math.sqrt(3) * tensao)

def corrente_monofasica(potencia_kw, tensao):
    return (potencia_kw * 1000) / tensao

def bitola_cabo(corrente):
    if corrente <= 10:
        return "1,5 mm²"
    elif corrente <= 16:
        return "2,5 mm²"
    elif corrente <= 25:
        return "4 mm²"
    elif corrente <= 32:
        return "6 mm²"
    elif corrente <= 40:
        return "10 mm²"
    elif corrente <= 63:
        return "16 mm²"
    else:
        return "Acima de 16 mm² (verificar projeto)"

def calcular_cabeamento(altura, largura, profundidade):
    comprimento = (altura + largura + profundidade) / 1000
    return round(comprimento * 1.2, 2)

def dimensionar_painel(largura_componentes, altura_componentes, profundidade_max):
    largura = largura_componentes * 1.3
    altura = altura_componentes * 1.4
    profundidade = profundidade_max + 50
    return round(altura), round(largura), round(profundidade)

# =========================
# ABAS
# =========================

tabs = st.tabs([
    "📋 Projeto",
    "🌀 Máquina",
    "🔥 Resistência",
    "⚡ Motor/Inversor",
    "🔌 Cabeamento",
    "📦 Painel"
])

# =========================
# ABA PROJETO
# =========================
with tabs[0]:
    st.header("Cadastro do Projeto")
    cliente = st.text_input("Cliente")
    os = st.text_input("Número da OS")
    engenheiro = st.text_input("Responsável Técnico")

# =========================
# ABA MÁQUINA
# =========================
with tabs[1]:
    st.header("Dimensões da Máquina")
    altura = st.number_input("Altura (mm)", value=1000)
    largura = st.number_input("Largura (mm)", value=800)
    profundidade = st.number_input("Profundidade (mm)", value=600)

# =========================
# ABA RESISTÊNCIA
# =========================
with tabs[2]:
    st.header("Banco de Resistência")
    potencia_total = st.number_input("Potência total (kW)", value=10.0)
    tensao_res = st.selectbox("Tensão", [220, 380])
    estagios = st.number_input("Número de estágios", min_value=1, value=2)

    potencia_estagio = potencia_total / estagios

    if tensao_res == 220:
        corrente_estagio = corrente_monofasica(potencia_estagio, tensao_res)
    else:
        corrente_estagio = corrente_trifasica(potencia_estagio, tensao_res)

    st.write(f"Potência por estágio: {round(potencia_estagio,2)} kW")
    st.write(f"Corrente por estágio: {round(corrente_estagio,2)} A")
    st.write(f"Bitola recomendada: {bitola_cabo(corrente_estagio)}")

# =========================
# ABA MOTOR
# =========================
with tabs[3]:
    st.header("Motor / Inversor")
    potencia_motor = st.number_input("Potência do motor (kW)", value=5.5)
    tensao_motor = st.selectbox("Tensão Motor", [220, 380, 440])

    corrente_motor = corrente_trifasica(potencia_motor, tensao_motor)

    st.write(f"Corrente estimada: {round(corrente_motor,2)} A")
    st.write(f"Bitola recomendada: {bitola_cabo(corrente_motor)}")

# =========================
# ABA CABEAMENTO
# =========================
with tabs[4]:
    st.header("Cabeamento Interno")

    comprimento = calcular_cabeamento(altura, largura, profundidade)
    st.write(f"Comprimento estimado por circuito: {comprimento} m")

# =========================
# ABA PAINEL
# =========================
with tabs[5]:
    st.header("Dimensionamento do Painel")

    largura_componentes = st.number_input("Soma largura componentes (mm)", value=400)
    altura_componentes = st.number_input("Soma altura ocupada (mm)", value=300)
    profundidade_max = st.number_input("Profundidade maior componente (mm)", value=200)

    alt, lar, prof = dimensionar_painel(
        largura_componentes,
        altura_componentes,
        profundidade_max
    )

    st.write(f"Dimensão mínima sugerida: {alt} x {lar} x {prof} mm")
