# app_airside.py
import streamlit as st
from datetime import datetime
from calculos import calcular_motor, calcular_disjuntor_cabo
from gerador_pdf import gerar_pdf
from gerador_multifilar import gerar_multifilar

# =============================
# CONFIGURAÇÃO DA PÁGINA
# =============================

st.set_page_config(
    page_title="Projeto Executivo Fancoil",
    layout="wide"
)

# =============================
# CABEÇALHO
# =============================

st.markdown("""
# 🏭 PROJETO EXECUTIVO – FANCOIL
### Sistema de Dimensionamento Técnico
---
""")

# =============================
# ABAS PRINCIPAIS
# =============================

tab1, tab2, tab3 = st.tabs([
    "🔧 Dimensionamento",
    "🤖 Automação",
    "📄 Relatório"
])

# =============================
# ABA 1 — DIMENSIONAMENTO
# =============================

with tab1:

    col1, col2 = st.columns(2)

    with col1:
        cliente = st.text_input("Nome do Cliente")
        engenheiro = st.text_input("Responsável Técnico")

    with col2:
        revisao = st.text_input("Número da Revisão", value="REV-00")
        data_atual = datetime.now().strftime("%d/%m/%Y")
        st.write(f"📅 Data: {data_atual}")

    st.divider()

    st.subheader("🔧 Dados Técnicos")

    vazao = st.number_input("Vazão (m³/h)", min_value=100.0, step=100.0)

    pressao_total = st.number_input(
        "Pressão Total do Sistema (Pa)",
        min_value=100,
        value=500,
        step=50
    )

    tensao = st.selectbox("Tensão de Alimentação (V)", ["220", "380"])

    pot_banco = st.number_input(
        "Potência Banco de Resistência (kW)",
        min_value=0.0,
        step=1.0
    )

    gerar = st.button("⚡ Gerar Projeto Executivo Completo")

    if gerar:

        # =============================
        # MOTOR
        # =============================

        motor, partida, corrente, disj_motor, cabo_motor = calcular_motor(
            float(vazao),
            str(tensao),
            float(pressao_total)
        )

        # =============================
        # BANCO DE RESISTÊNCIA
        # =============================

        if pot_banco > 0:
            corrente_banco, disj_banco, cabo_banco = calcular_disjuntor_cabo(
                float(pot_banco),
                str(tensao)
            )
        else:
            corrente_banco, disj_banco, cabo_banco = 0, 0, 0

        # =============================
        # SALVAR SESSION
        # =============================

        st.session_state["dados_projeto"] = {
            "cliente": cliente,
            "engenheiro": engenheiro,
            "revisao": revisao,
            "data": data_atual,
            "vazao": vazao,
            "pressao_total": pressao_total,
            "tensao": tensao,
            "motor": motor,
            "partida": partida,
            "corrente": corrente,
            "disj_motor": disj_motor,
            "cabo_motor": cabo_motor,
            "pot_banco": pot_banco,
            "corrente_banco": corrente_banco,
            "disj_banco": disj_banco,
            "cabo_banco": cabo_banco
        }

        st.success("✅ Projeto Gerado com Sucesso!")

# =============================
# ABA 2 — AUTOMAÇÃO
# =============================

with tab2:

    st.subheader("🤖 Lógica de Automação")

    tipo_filtro = st.selectbox("Tipo de Filtro", ["G4", "F7", "HEPA"])
    sensor_pressao = st.selectbox("Sensor de Pressão Diferencial", ["Sim", "Não"])
    controle = st.selectbox("Controle de Motor", ["Contator", "Inversor de Frequência"])

    st.info(f"""
    **Configuração Selecionada:**

    - Filtro: {tipo_filtro}  
    - Sensor ΔP: {sensor_pressao}  
    - Tipo de Controle: {controle}
    """)

# =============================
# ABA 3 — RELATÓRIO
# =============================

with tab3:

    st.subheader("📄 Geração de Relatórios")

    if "dados_projeto" in st.session_state:

        dados = st.session_state["dados_projeto"]

        st.write("### 📊 Resumo do Projeto")
        st.write(f"Cliente: {dados['cliente']}")
        st.write(f"Motor: {dados['motor']} CV")
        st.write(f"Corrente: {dados['corrente']} A")
        st.write(f"Disjuntor: {dados['disj_motor']} A")
        st.write(f"Cabo Motor: {dados['cabo_motor']} mm²")

        gerar_pdf(
            dados["vazao"],
            dados["tensao"],
            dados["motor"],
            dados["partida"],
            dados["corrente"],
            dados["disj_motor"],
            dados["cabo_motor"],
            dados["pot_banco"],
            dados["corrente_banco"],
            dados["disj_banco"]
        )

        gerar_multifilar(
            dados["vazao"],
            dados["tensao"],
            dados["motor"],
            dados["partida"],
            dados["pot_banco"]
        )

        with open("Projeto_Executivo_Fancoil_FINAL.pdf", "rb") as file:
            st.download_button(
                "📄 Baixar Projeto em PDF",
                file,
                file_name="Projeto_Executivo_Fancoil.pdf"
            )

        with open("Multifilar_Fancoil.png", "rb") as file:
            st.download_button(
                "🖼️ Baixar Diagrama Multifilar",
                file,
                file_name="Multifilar_Fancoil.png"
            )

    else:
        st.warning("⚠️ Gere o projeto na aba Dimensionamento primeiro.")

st.markdown("---")
st.caption("Sistema Técnico Automatizado | Engenharia HVAC | Versão Corporativa")
