import streamlit as st
import math
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import sqlite3

st.set_page_config(page_title="AirSide PRO", layout="wide")
st.title("🌀 AirSide PRO - Sistema Profissional de Dimensionamento Elétrico")
st.divider()

# =====================================================
# BANCO DE DADOS
# =====================================================

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

# =====================================================
# FUNÇÕES DE CÁLCULO
# =====================================================

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
    corrente_unit = round((pot_unit*1000)/tensao,2)
    corrente_total = round(corrente_unit*qtd,2)
    disj_res = math.ceil(corrente_total*1.25)
    return qtd, corrente_total, disj_res

def calcular_resistencia_por_quantidade(qtd, pot_unit, tensao):
    corrente_unit = round((pot_unit*1000)/tensao,2)
    corrente_total = round(corrente_unit*qtd,2)
    disj_res = math.ceil(corrente_total*1.25)
    return qtd, corrente_total, disj_res

def gerar_cabecalho(cliente, tecnico, tensao, tipo, vazao=None, pressao=None):
    data = datetime.now().strftime("%d/%m/%Y")
    texto = f"Cliente: {cliente}\nTécnico: {tecnico}\nData: {data}\nTensão: {tensao}V\nTipo de Partida: {tipo}"
    if vazao:
        texto += f"\nVazão: {vazao} m³/h"
    if pressao:
        texto += f"\nPressão Total: {pressao} Pa"
    return texto+"\n"+"="*50+"\n"

def multifilar_motor(tipo, tensao, motor, disj_geral):
    if tipo=="Inversor":
        return f"\n--- Multifilar Motor (Inversor) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → Inversor → Motor {motor}CV\n"
    elif tipo=="Direta":
        return f"\n--- Multifilar Motor (Partida Direta) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → Contator → Motor {motor}CV\n"
    elif tipo=="Estrela-Triângulo":
        return f"\n--- Multifilar Motor (Estrela-Triângulo) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → 3 Contatores → Motor {motor}CV\n"
    elif tipo=="Softstarter":
        return f"\n--- Multifilar Motor (Softstarter) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → Softstarter → Motor {motor}CV\n"
    else:
        return ""

def multifilar_resistencia(tensao, qtd, pot_unit, corrente_total):
    return f"\n--- Multifilar Resistências ---\nL1/L2 → Disj Resistência → {qtd}x Resistências {pot_unit}kW → Total Corrente: {corrente_total}A\n"

# =====================================================
# ABAS
# =====================================================

aba1, aba2, aba3, aba4, aba5, aba6, aba7, aba8 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais", "🎛️ Simulador",
     "👥 Clientes", "📁 Projetos", "💰 Orçamento"]
)
