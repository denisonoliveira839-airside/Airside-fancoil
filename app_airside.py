import streamlit as st
import math
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3

=====================================================

CONFIG

=====================================================

st.set_page_config(page_title="AirSide PRO", layout="wide")
st.title("🌀 AirSide PRO - Sistema Profissional de Dimensionamento Elétrico")
st.divider()

=====================================================

BANCO DE DADOS

=====================================================

def conectar():
return sqlite3.connect("airside.db")

def criar_tabelas():
conn = conectar()
c = conn.cursor()

c.execute("""  
CREATE TABLE IF NOT EXISTS clientes (  
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    nome TEXT,  
    tecnico TEXT,  
    data TEXT  
)  
""")  

c.execute("""  
CREATE TABLE IF NOT EXISTS projetos (  
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    cliente TEXT,  
    tecnico TEXT,  
    tipo TEXT,  
    tensao INTEGER,  
    motor REAL,  
    corrente REAL,  
    data TEXT  
)  
""")  

conn.commit()  
conn.close()

criar_tabelas()

=====================================================

FUNÇÕES DE CÁLCULO

=====================================================

def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):
potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
potencia_kw *= 1.15
potencia_cv = potencia_kw / 0.736
potencia_motor = max(1, math.ceil(potencia_cv))

corrente = round((potencia_kw*1000)/(math.sqrt(3)*tensao*0.85),2)  
disj_motor = math.ceil(corrente*1.25)  
disj_geral = max(10, math.ceil(disj_motor*1.3))  

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

def calcular_resistencia_por_potencia(pot_total, pot_unit, tensao):
qtd = math.ceil(pot_total / pot_unit)
corrente_unit = round((pot_unit1000)/tensao,2)
corrente_total = round(corrente_unitqtd,2)
disj_res = math.ceil(corrente_total*1.25)
return qtd, corrente_total, disj_res

def calcular_resistencia_por_quantidade(qtd, pot_unit, tensao):
corrente_unit = round((pot_unit1000)/tensao,2)
corrente_total = round(corrente_unitqtd,2)
disj_res = math.ceil(corrente_total*1.25)
return qtd, corrente_total, disj_res

=====================================================

ABAS

=====================================================

aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8 = st.tabs(
["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais",
"🎛️ Simulador", "👥 Clientes", "📁 Projetos", "💰 Orçamento"]
)

=====================================================

ABA 1 - DADOS

=====================================================

with aba1:

col1, col2 = st.columns(2)  
cliente = col1.text_input("Nome do Cliente", key="cliente_dados")  
tecnico = col2.text_input("Nome do Técnico", key="tecnico_dados")  

st.divider()  

tipo_partida = st.selectbox(  
    "Tipo de Partida",  
    ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter", "Somente Resistência"],  
    key="tipo_partida"  
)  

tensao = st.selectbox("Tensão (V)", [220, 380, 440], key="tensao")  

if tipo_partida != "Somente Resistência":  
    vazao = st.number_input("Vazão (m³/h)", value=5000.0, key="vazao")  
    pressao = st.number_input("Pressão Total (Pa)", value=500.0, key="pressao")  
else:  
    vazao = None  
    pressao = None  

st.divider()  
st.subheader("🔥 Resistência (Opcional)")  

usar_resistencia = st.checkbox("Adicionar Resistência", key="usar_res")  

if usar_resistencia:  
    modo_res = st.radio(  
        "Modo de Cálculo",  
        ["Informar Potência Total", "Informar Quantidade"],  
        key="modo_res"  
    )  

    pot_unit = st.number_input("Potência Unitária (kW)", value=1.75, key="pot_unit")  

    if modo_res == "Informar Potência Total":  
        pot_total = st.number_input("Potência Total (kW)", value=10.5, key="pot_total")  
    else:  
        qtd_res = st.number_input("Quantidade", value=6, key="qtd_res")  

calcular = st.button("🔎 Gerar Projeto", use_container_width=True, key="btn_calcular")

=====================================================

PROCESSAMENTO

=====================================================

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

st.session_state["motor"] = motor_data  
st.session_state["res"] = res_data  
st.session_state["cliente"] = cliente  
st.session_state["tecnico"] = tecnico  
st.session_state["tipo"] = tipo_partida  
st.session_state["tensao"] = tensao

=====================================================

ABA 2 - RESULTADO

=====================================================

with aba2:

if "motor" in st.session_state and st.session_state["motor"]:  

    motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]  

    st.success("Projeto calculado com sucesso!")  

    st.write(f"**Motor:** {motor} CV")  
    st.write(f"**Corrente:** {corrente} A")  
    st.write(f"**Disjuntor Motor:** {disj_motor} A")  
    st.write(f"**Disjuntor Geral:** {disj_geral} A")  
    st.write(f"**Cabo Sugerido:** {cabo} mm²")  

else:  
    st.info("Nenhum cálculo realizado ainda.")

=====================================================

ABA 3 - MULTIFILAR

=====================================================

with aba3:

st.subheader("📑 Diagrama Multifilar")  

if "motor" in st.session_state and st.session_state["motor"]:  

    motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]  
    tipo = st.session_state["tipo"]  

    st.markdown("### Estrutura Elétrica")  

    if tipo == "Inversor":  
        st.write("Rede → Disjuntor Geral → Inversor → Motor")  
    elif tipo == "Direta":  
        st.write("Rede → Disjuntor → Contator → Relé Térmico → Motor")  
    elif tipo == "Estrela-Triângulo":  
        st.write("Rede → Disjuntor → 3 Contatores → Relé Térmico → Motor")  
    elif tipo == "Softstarter":  
        st.write("Rede → Disjuntor → Softstarter → Motor")  

    st.write(f"Cabo Potência: {cabo} mm²")  
    st.write(f"Disjuntor Geral: {disj_geral} A")  

else:  
    st.info("Execute um cálculo primeiro.")

=====================================================

ABA 4 - MATERIAIS

=====================================================

with aba4:

st.subheader("📦 Lista de Materiais")  

if "motor" in st.session_state and st.session_state["motor"]:  

    motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]  

    materiais = {  
        "Item": [  
            "Disjuntor Geral",  
            "Disjuntor Motor",  
            "Cabo Potência (mm²)",  
            "Motor (CV)"  
        ],  
        "Especificação": [  
            f"{disj_geral} A",  
            f"{disj_motor} A",  
            f"{cabo} mm²",  
            f"{motor} CV"  
        ]  
    }  

    df_mat = pd.DataFrame(materiais)  
    st.dataframe(df_mat, use_container_width=True)  

else:  
    st.info("Execute um cálculo primeiro.")

=====================================================

ABA 5 - SIMULADOR

=====================================================

with aba5:

st.subheader("🎛️ Simulação de Operação do Motor")  

if "motor" in st.session_state and st.session_state["motor"]:  

    motor, corrente, _, _, _ = st.session_state["motor"]  

    tempo = np.linspace(0, 10, 100)  
    corrente_sim = corrente * (1 - np.exp(-tempo))  

    fig, ax = plt.subplots()  
    ax.plot(tempo, corrente_sim)  
    ax.set_xlabel("Tempo (s)")  
    ax.set_ylabel("Corrente (A)")  
    ax.set_title("Partida do Motor")  

    st.pyplot(fig)  

else:  
    st.info("Execute um cálculo primeiro.")

=====================================================

ABA 6 - CLIENTES

=====================================================

with aba6:

st.subheader("👥 Cadastro de Clientes")  

novo_cliente = st.text_input("Nome do Cliente", key="cliente_cadastro")  
novo_tecnico = st.text_input("Nome do Técnico", key="tecnico_cadastro")  

if st.button("Salvar Cliente", key="btn_salvar_cliente"):  

    conn = conectar()  
    c = conn.cursor()  

    c.execute(  
        "INSERT INTO clientes (nome, tecnico, data) VALUES (?, ?, ?)",  
        (novo_cliente, novo_tecnico, datetime.now().strftime("%d/%m/%Y"))  
    )  

    conn.commit()  
    conn.close()  

    st.success("Cliente salvo com sucesso!")  

conn = conectar()  
df = pd.read_sql("SELECT * FROM clientes", conn)  
conn.close()  

st.dataframe(df, use_container_width=True)

=====================================================

ABA 7 - PROJETOS

=====================================================

with aba7:

st.subheader("📁 Projetos Salvos")  

if "motor" in st.session_state and st.session_state["motor"]:  

    if st.button("Salvar Projeto", key="btn_salvar_projeto"):  

        motor, corrente, _, _, _ = st.session_state["motor"]  

        conn = conectar()  
        c = conn.cursor()  

        c.execute("""  
        INSERT INTO projetos (cliente, tecnico, tipo, tensao, motor, corrente, data)  
        VALUES (?, ?, ?, ?, ?, ?, ?)  
        """, (  
            st.session_state["cliente"],  
            st.session_state["tecnico"],  
            st.session_state["tipo"],  
            st.session_state["tensao"],  
            motor,  
            corrente,  
            datetime.now().strftime("%d/%m/%Y")  
        ))  

        conn.commit()  
        conn.close()  

        st.success("Projeto salvo com sucesso!")  

conn = conectar()  
df_proj = pd.read_sql("SELECT * FROM projetos", conn)  
conn.close()  

st.dataframe(df_proj, use_container_width=True)

=====================================================

ABA 8 - ORÇAMENTO

=====================================================

with aba8:

st.subheader("💰 Orçamento")  

if "motor" in st.session_state and st.session_state["motor"]:  

    motor, corrente, disj_motor, disj_geral, cabo = st.session_state["motor"]  

    valor_motor = motor * 300  
    valor_disj = disj_geral * 5  
    valor_cabo = cabo * 20  

    total = valor_motor + valor_disj + valor_cabo  

    margem = st.slider("Margem (%)", 0, 100, 30)  
    total_final = total * (1 + margem/100)  

    st.write(f"Valor Base: R$ {round(total,2)}")  
    st.write(f"Valor Final com Margem: R$ {round(total_final,2)}")  

else:  
    st.info("Execute um cálculo primeiro.")
