import streamlit as st
import math

from core.resistencia import calcular_banco
from core.cabos import bitola_cabo, calcular_cabeamento
from core.painel import dimensionar_painel
from core.materiais import gerar_lista_materiais

st.set_page_config(layout="wide")
st.title("🏭 Plataforma Interna de Engenharia - Fancoil")

# =============================
# ABAS
# =============================

tabs = st.tabs([
    "📋 Projeto",
    "🌀 Máquina",
    "🔥 Resistência",
    "⚡ Motor",
    "🔌 Cabeamento",
    "📦 Painel",
    "📑 Materiais"
])

# =============================
# 1️⃣ PROJETO
# =============================
with tabs[0]:
    st.header("Cadastro do Projeto")
    cliente = st.text_input("Cliente")
    os = st.text_input("Ordem de Serviço")
    responsavel = st.text_input("Responsável Técnico")
    norma = st.text_input("Norma Aplicável")

# =============================
# 2️⃣ MÁQUINA
# =============================
with tabs[1]:
    st.header("Dimensões da Máquina")

    altura = st.number_input("Altura (mm)", value=1000)
    largura = st.number_input("Largura (mm)", value=800)
    profundidade = st.number_input("Profundidade (mm)", value=600)

# =============================
# 3️⃣ RESISTÊNCIA
# =============================
with tabs[2]:
    st.header("Banco de Resistência")

    potencia_total = st.number_input("Potência total do banco (kW)", value=12.0)
    tensao_res = st.selectbox("Tensão do banco", [220, 380])
    estagios = st.number_input("Número de estágios", min_value=1, value=3)

    banco = calcular_banco(potencia_total, tensao_res, estagios)

    st.subheader("Resultado por Estágio")
    st.write(f"Potência por estágio: {banco['potencia_estagio']} kW")
    st.write(f"Corrente por estágio: {banco['corrente_estagio']} A")

    bitola_res = bitola_cabo(banco["corrente_estagio"])
    st.write(f"Bitola recomendada: {bitola_res} mm²")

# =============================
# 4️⃣ MOTOR
# =============================
with tabs[3]:
    st.header("Motor / Inversor")

    potencia_motor = st.number_input("Potência do motor (kW)", value=5.5)
    tensao_motor = st.selectbox("Tensão do motor", [220, 380, 440])

    corrente_motor = (potencia_motor * 1000) / (math.sqrt(3) * tensao_motor)

    st.write(f"Corrente estimada: {round(corrente_motor,2)} A")

    bitola_motor = bitola_cabo(corrente_motor)
    st.write(f"Bitola recomendada: {bitola_motor} mm²")

# =============================
# 5️⃣ CABEAMENTO
# =============================
with tabs[4]:
    st.header("Cabeamento Interno")

    comprimento_estimado = calcular_cabeamento(altura, largura, profundidade)

    st.write(f"Comprimento estimado por circuito: {comprimento_estimado} m")

# =============================
# 6️⃣ PAINEL
# =============================
with tabs[5]:
    st.header("Dimensionamento do Painel")

    largura_componentes = st.number_input("Soma das larguras dos componentes (mm)", value=400)
    altura_componentes = st.number_input("Altura ocupada (mm)", value=300)
    profundidade_max = st.number_input("Profundidade maior componente (mm)", value=200)

    alt, lar, prof = dimensionar_painel(
        largura_componentes,
        altura_componentes,
        profundidade_max
    )

    st.write("Dimensão mínima sugerida:")
    st.write(f"Altura: {alt} mm")
    st.write(f"Largura: {lar} mm")
    st.write(f"Profundidade: {prof} mm")

# =============================
# 7️⃣ LISTA DE MATERIAIS
# =============================
with tabs[6]:
    st.header("Resumo de Materiais")

    if "bitola_res" in locals():
        materiais_res = gerar_lista_materiais(bitola_res, comprimento_estimado)
        st.subheader("Materiais Resistência")
        st.write(materiais_res)

    if "bitola_motor" in locals():
        materiais_motor = gerar_lista_materiais(bitola_motor, comprimento_estimado)
        st.subheader("Materiais Motor")
        st.write(materiais_motor)
