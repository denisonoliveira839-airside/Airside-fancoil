# app_airside.py
import streamlit as st
from datetime import datetime
from calculos import calcular_motor, calcular_disjuntor_cabo
from gerador_pdf import gerar_pdf
from gerador_multifilar import gerar_multifilar

st.set_page_config(page_title="Projeto Executivo Fancoil", layout="centered")

# =============================
# CABEÇALHO PROFISSIONAL
# =============================

st.markdown("""
# 🏭 PROJETO EXECUTIVO – FANCOIL
### Sistema de Dimensionamento Técnico
---
""")

col1, col2 = st.columns(2)

with col1:
    cliente = st.text_input("Nome do Cliente")
    engenheiro = st.text_input("Responsável Técnico")

with col2:
    revisao = st.text_input("Número da Revisão", value="REV-00")
    data_atual = datetime.now().strftime("%d/%m/%Y")
    st.write(f"📅 Data: {data_atual}")

st.divider()

# =============================
# ENTRADAS TÉCNICAS
# =============================

st.subheader("🔧 Dados Técnicos")

vazao = st.number_input("Vazão (m³/h)", min_value=100.0, step=100.0)
tensao = st.selectbox("Tensão de Alimentação (V)", ["220", "380"])
pot_banco = st.number_input("Potência Banco de Resistência (kW)", min_value=0.0, step=1.0)

st.divider()

# =============================
# GERAR PROJETO
# =============================

if st.button("⚡ Gerar Projeto Executivo Completo"):

    motor, partida, corrente, disj_motor, cabo_motor = calcular_motor(vazao, tensao)

    if pot_banco > 0:
        corrente_banco, disj_banco = calcular_disjuntor_cabo(pot_banco, tensao)
    else:
        corrente_banco, disj_banco = 0, 0

    st.success("Projeto Gerado com Sucesso!")

    st.subheader("📊 Dimensionamento do Motor")

    st.info(f"""
    **Cliente:** {cliente}  
    **Responsável:** {engenheiro}  
    **Revisão:** {revisao}  
    **Data:** {data_atual}
    """)

    st.write(f"**Potência do Motor:** {motor} CV")
    st.write(f"**Tipo de Partida:** {partida}")
    st.write(f"**Corrente Nominal:** {corrente} A")
    st.write(f"**Disjuntor do Motor:** {disj_motor} A")
    st.write(f"**Cabo do Motor:** {cabo_motor} mm²")

    if pot_banco > 0:
        st.subheader("🔥 Banco de Resistência")
        st.write(f"Potência Total: {pot_banco} kW")
        st.write(f"Corrente Banco: {corrente_banco} A")
        st.write(f"Disjuntor Banco: {disj_banco} A")

    gerar_pdf(vazao, tensao, motor, partida, corrente, disj_motor,
              cabo_motor, pot_banco, corrente_banco, disj_banco)

    gerar_multifilar(vazao, tensao, motor, partida, pot_banco)

    with open("Projeto_Executivo_Fancoil_FINAL.pdf", "rb") as file:
        st.download_button("📄 Baixar Projeto em PDF",
                           file,
                           file_name="Projeto_Executivo_Fancoil.pdf")

    with open("Multifilar_Fancoil.png", "rb") as file:
        st.download_button("🖼️ Baixar Diagrama Multifilar",
                           file,
                           file_name="Multifilar_Fancoil.png")

st.markdown("---")
st.caption("Sistema Técnico Automatizado | Engenharia HVAC | Versão Corporativa")
