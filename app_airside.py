# app.py
import streamlit as st
from calculos import calcular_motor, calcular_disjuntor_cabo
from gerador_pdf import gerar_pdf
from gerador_multifilar import gerar_multifilar

st.set_page_config(page_title="Projeto Fancoil", layout="centered")

st.title("🔧 Gerador de Projeto Executivo - Fancoil")

st.markdown("Preencha os dados abaixo para gerar o projeto completo.")

# =========================
# ENTRADAS
# =========================

vazao = st.number_input("Vazão (m³/h)", min_value=100.0, step=100.0)
tensao = st.selectbox("Tensão de Alimentação (V)", ["220", "380"])
pot_banco = st.number_input("Potência do Banco de Resistência (kW) - se houver", min_value=0.0, step=1.0)

# =========================
# BOTÃO GERAR PROJETO
# =========================

if st.button("⚡ Gerar Projeto Executivo"):

    # Cálculos Motor
    motor, partida, corrente, disj_motor, cabo_motor = calcular_motor(vazao, tensao)

    # Cálculo Banco
    if pot_banco > 0:
        corrente_banco, disj_banco = calcular_disjuntor_cabo(pot_banco, tensao)
    else:
        corrente_banco, disj_banco = 0, 0

    # =========================
    # RESULTADOS NA TELA
    # =========================

    st.success("Projeto Gerado com Sucesso!")

    st.subheader("📊 Dimensionamento do Motor")
    st.write(f"**Potência do Motor:** {motor} CV")
    st.write(f"**Tipo de Partida:** {partida}")
    st.write(f"**Corrente Nominal:** {corrente} A")
    st.write(f"**Disjuntor do Motor:** {disj_motor} A")
    st.write(f"**Cabo do Motor:** {cabo_motor} mm²")

    if pot_banco > 0:
        st.subheader("🔥 Banco de Resistência")
        st.write(f"**Potência Total:** {pot_banco} kW")
        st.write(f"**Corrente Banco:** {corrente_banco} A")
        st.write(f"**Disjuntor Banco:** {disj_banco} A")

    # =========================
    # GERAR ARQUIVOS
    # =========================

    gerar_pdf(vazao, tensao, motor, partida, corrente, disj_motor,
              cabo_motor, pot_banco, corrente_banco, disj_banco)

    gerar_multifilar(vazao, tensao, motor, partida, pot_banco)

    # =========================
    # DOWNLOADS
    # =========================

    with open("Projeto_Executivo_Fancoil_FINAL.pdf", "rb") as file:
        st.download_button("📄 Baixar Projeto em PDF",
                           file,
                           file_name="Projeto_Executivo_Fancoil.pdf")

    with open("Multifilar_Fancoil.png", "rb") as file:
        st.download_button("🖼️ Baixar Diagrama Multifilar",
                           file,
                           file_name="Multifilar_Fancoil.png")
