import streamlit as st

st.set_page_config(page_title="Projeto Elétrico", layout="wide")

st.title("🔌 Sistema de Geração de Projeto Elétrico")

# =============================
# ENTRADAS PRINCIPAIS
# =============================

st.sidebar.header("📋 Dados do Projeto")

cliente = st.sidebar.text_input("Nome do Cliente")
tecnico = st.sidebar.text_input("Nome do Técnico")
vazao = st.sidebar.number_input("Vazão (m³/h)", min_value=0.0)
pressao = st.sidebar.number_input("Pressão (Pa)", min_value=0.0)
potencia = st.sidebar.number_input("Potência do Motor (CV)", min_value=0.0)
tensao = st.sidebar.selectbox("Tensão", ["220V", "380V", "440V"])

st.sidebar.markdown("---")

corrente = st.sidebar.number_input("Corrente Nominal (A)", min_value=0.0)

modelo_disjuntor = st.sidebar.text_input("Modelo do Disjuntor")
modelo_contator = st.sidebar.text_input("Modelo do Contator")
modelo_rele = st.sidebar.text_input("Modelo do Relé Térmico")

# =============================
# ABAS
# =============================

aba1, aba2, aba3 = st.tabs(["📐 Multifilar", "🧾 Lista de Materiais", "📄 Dados do Projeto"])

# =============================
# ABA 1 - MULTIFILAR
# =============================

with aba1:

    st.subheader("Diagrama Multifilar")

    multifilar = f"""
ALIMENTAÇÃO TRIFÁSICA

L1 ───────────────┐
                  │
L2 ───────────────┼──────────────┐
                  │              │
L3 ───────────────┼──────────────┼──────────────┐
                  │              │              │
               (1)            (3)            (5)
            DISJUNTOR {modelo_disjuntor}
               (2)            (4)            (6)
                  │              │              │
                  │              │              │
               (1)            (3)            (5)
            CONTATOR {modelo_contator}
               (2)            (4)            (6)
                  │              │              │
                  │              │              │
                  U              V              W
                     MOTOR {potencia} CV
                     {tensao}
    """

    st.code(multifilar)

# =============================
# ABA 2 - LISTA DE MATERIAIS
# =============================

with aba2:

    st.subheader("Lista de Materiais")

    st.markdown(f"""
### ⚡ Potência
- 1x Disjuntor Tripolar - {modelo_disjuntor}
- 1x Contator Tripolar - {modelo_contator}
- 1x Relé Térmico - {modelo_rele}
- Cabos para {corrente} A
- Bornes
- Trilho DIN
- Canaletas

### ⚙ Sugestão de Inversores
- WEG CFW300
- WEG CFW500
- Schneider Altivar 12
- Schneider Altivar 320

### 🖥 Sugestão de CLP
- WEG CLIC02
- Siemens LOGO!
- Schneider Zelio
- Delta DVP
    """)

# =============================
# ABA 3 - DADOS DO PROJETO
# =============================

with aba3:

    st.subheader("Resumo do Projeto")

    st.write(f"**Cliente:** {cliente}")
    st.write(f"**Técnico:** {tecnico}")
    st.write(f"**Vazão:** {vazao} m³/h")
    st.write(f"**Pressão:** {pressao} Pa")
    st.write(f"**Potência:** {potencia} CV")
    st.write(f"**Tensão:** {tensao}")
    st.write(f"**Corrente:** {corrente} A")
