import streamlit as st
import google.generativeai as genai
import os

# --- IMPORTAMOS LOS MÓDULOS ---
import suite_correo
import suite_sustituciones
import suite_administradores

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="Suite Comercial IA",
    page_icon="🏢",
    layout="wide"
)

# --- DEFINICIÓN DE CONSTANTES (Para evitar errores de texto) ---
MENU_HOME = "🏠 Inicio"
MENU_MAIL = "📮 Suite CORREO"
MENU_OBRAS = "🔧 Suite SUSTITUCIONES"
MENU_ADMIN = "👥 Suite ADMINISTRADORES"

OPCIONES_MENU = [MENU_HOME, MENU_MAIL, MENU_OBRAS, MENU_ADMIN]

# --- 2. SECRETOS ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Error: Configura los secretos en Streamlit Cloud.")
    st.stop()

# --- 3. INICIALIZACIÓN DE ESTADOS ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "navegacion" not in st.session_state: st.session_state.navegacion = MENU_HOME
if "db_correos" not in st.session_state: st.session_state.db_correos = {} 
if "model
