import streamlit as st
import extract_msg
import google.generativeai as genai
import email
from email import policy
from email.parser import BytesParser
import time
import os

# --- 1. CONFIGURACIÓN GLOBAL ---
st.set_page_config(
    page_title="Suite Comercial IA",
    page_icon="🏢",
    layout="wide"
)

# --- 2. GESTIÓN DE SECRETOS ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Error: Configura los secretos en Streamlit Cloud.")
    st.stop()

# --- 3. LOGIN Y NAVEGACIÓN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Función para cambiar de página desde los botones del inicio
def ir_a(pagina):
    st.session_state.navegacion = pagina
    st.rerun()

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906343.png", width=80)
    st.title("Acceso Privado")
    
    # Login
    if not st.session_state.authenticated:
        input_pass = st.text_input("Contraseña", type="password")
        if input_pass == PASSWORD_REAL:
            st.session_state.authenticated = True
            st.rerun()
        elif input_pass:
            st.warning("🔒 Clave incorrecta")
        st.stop()

    st.success(f"Hola, Comercial 👋")
    st.divider()
    
    # MENÚ LATERAL (Conectado al estado 'navegacion')
    # Si no existe la variable, la iniciamos en Inicio
    if "navegacion" not in st.session_state:
        st.session_state.navegacion = "🏠 Inicio"
        
    menu_selection = st.radio(
        "Herramientas:",
        ["🏠 Inicio", "📧 Análisis de bandeja de entrada", "🚧 Gestión de Obras", "📄 Redactor de Contratos"],
        key="navegacion" # Esto conecta el menú con los botones del dashboard
    )
    
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

# --- 4. MOTOR IA ---
genai.configure(api_key=API_KEY)
# Lista de candidatos (Tu "Llave maestra")
CANDIDATOS = ['gemini-flash-latest', 'gemini-1.5-flash-latest', 'gemini-pro-latest', 'models/gemini-1.5-flash-001']

if "model_name" not in st.session_state:
    for nombre in CANDIDATOS:
        try:
            t = genai.GenerativeModel(nombre); t.generate_content("Hola")
            st.session_state.model_name = nombre; break
        except: continue

if "model_name" in st.session_state:
    model = genai.GenerativeModel(st.session_state.model_name)
else:
    st.error("❌ Error conectando IA.")
    st.stop
