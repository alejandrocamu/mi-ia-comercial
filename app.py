import streamlit as st
import google.generativeai as genai
import os

# --- IMPORTAMOS LOS MÓDULOS ---
import suite_correo
import suite_sustituciones
import suite_administradores

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Suite Comercial IA", page_icon="🏢", layout="wide")

# --- 2. SECRETOS ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Error crítico: No se encuentran los secretos.")
    st.stop()

# --- 3. ESTADOS DE SESIÓN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "navegacion" not in st.session_state: st.session_state.navegacion = "🏠 Inicio"
if "db_correos" not in st.session_state: st.session_state.db_correos = {} 

def navegar_a(pagina):
    st.session_state.navegacion = pagina
    st.rerun()

# --- 4. BARRA LATERAL (Limpia de errores) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906343.png", width=80)
    st.title("Acceso Privado")
    
    if not st.session_state.authenticated:
        input_pass = st.text_input("Contraseña", type="password")
        if input_pass == PASSWORD_REAL:
            st.session_state.authenticated = True
            st.rerun()
        elif input_pass:
            st.warning("🔒 Clave incorrecta")
        st.stop()

    st.success("Hola, Comercial 👋")
    st.divider()
    
    opciones = ["🏠 Inicio", "📮 Suite CORREO", "🔧 Suite SUSTITUCIONES", "👥 Suite ADMINISTRADORES"]
    try: idx = opciones.index
