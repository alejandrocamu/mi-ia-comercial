import streamlit as st
import extract_msg
import google.generativeai as genai
import email
from email import policy
from email.parser import BytesParser
import time
import os
import datetime

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

# --- 3. GESTIÓN DE ESTADO (MEMORIA) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "db_correos" not in st.session_state:
    st.session_state.db_correos = {} 

if "navegacion" not in st.session_state:
    st.session_state.navegacion = "🏠 Inicio"

# Función para cambiar de página (sin conflictos)
def ir_a(pagina):
    st.session_state.navegacion = pagina
    st.rerun()

# --- 4. BARRA LATERAL ---
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

    st.success(f"Hola, Comercial 👋")
    st.divider()
    
    # --- MENÚ DE NAVEGACIÓN ---
    OPCIONES_MENU = ["🏠 Inicio", "📮 Suite CORREO", "🚧 Gestión de Obras", "📄 Redactor de Contratos"]
    
    # Buscamos en qué página estamos para marcarla en el menú
    try:
        indice_actual = OPCIONES_MENU.index(st.session_state.navegacion)
    except:
        indice_actual = 0
        
    # Dibujamos el menú
    seleccion_usuario = st.radio(
        "Menú Principal:",
        OPCIONES_MENU,
        index=indice_actual
    )
    
    # Si el usuario cambia el menú manualmente, actual
