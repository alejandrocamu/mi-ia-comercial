import streamlit as st
import google.generativeai as genai
import os

# --- IMPORTAMOS MÓDULOS ---
import suite_correo
import suite_sustituciones
import suite_administradores
import suite_tareas  # <--- IMPORTANTE

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Suite Comercial IA", page_icon="🏢", layout="wide")

# --- CONSTANTES DE MENÚ ---
MENU_HOME = "🏠 Inicio"
MENU_MAIL = "📮 Suite CORREO"
MENU_TAREAS = "📋 Suite TAREAS" # <--- NUEVO
MENU_OBRAS = "🔧 Suite SUSTITUCIONES"
MENU_ADMIN = "👥 Suite ADMINISTRADORES"

OPCIONES_MENU = [MENU_HOME, MENU_MAIL, MENU_TAREAS, MENU_OBRAS, MENU_ADMIN]

# --- SECRETOS ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Error Secretos"); st.stop()

# --- ESTADOS ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "navegacion" not in st.session_state: st.session_state.navegacion = MENU_HOME
if "db_correos" not in st.session_state: st.session_state.db_correos = {}
if "db_tareas" not in st.session_state: st.session_state.db_tareas = [] # Memoria para tareas
if "model_name" not in st.session_state: st.session_state.model_name = None

def navegar_a(pagina):
    st.session_state.navegacion = pagina; st.rerun()

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906343.png", width=80)
    st.title("Acceso Privado")
    
    if not st.session_state.authenticated:
        input_pass = st.text_input("Contraseña", type="password")
        if input_pass == PASSWORD_REAL: st.session_state.authenticated = True; st.rerun()
        else: st.stop()

    st.success("Hola, Comercial 👋")
    st.divider()
    
    try: idx = OPCIONES_MENU.index(st.session_state.navegacion)
    except: idx = 0; st.session_state.navegacion = MENU_HOME
    
    seleccion = st.radio("Herramientas:", OPCIONES_MENU, index=idx)
    if seleccion != st.session_state.navegacion: st.session_state.navegacion = seleccion; st.rerun()
        
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False; st.rerun()

# --- CONEXIÓN IA ---
genai.configure(api_key=API_KEY)
# Intentamos conectar si hace falta
if not st.session_state.model_name:
    try: 
        genai.GenerativeModel('gemini-2.0-flash-exp').generate_content("T")
        st.session_state.model_name = 'gemini-2.0-flash-exp'
    except: pass

model = genai.GenerativeModel(st.session_state.model_name) if st.session_state.model_name else None

# --- ROUTER ---
pagina = st.session_state.navegacion

if pagina == MENU_HOME:
    st.title("🚀 Tu Centro de Mando")
    col1, col2, col3, col4 = st.columns(4) # Ahora son 4 columnas
    
    with col1:
        with st.container(border=True):
            st.subheader("📮 Correo")
            if st.button("Ir a Correo", use_container_width=True): navegar_a(MENU_MAIL)
    with col2:
        with st.container(border=True):
            st.subheader("📋 Tareas") # Nueva tarjeta
            if st.button("Ir a Tareas", use_container_width=True): navegar_a(MENU_TAREAS)
    with col3:
        with st.container(border=True):
            st.subheader("🔧 Obras")
            if st.button("Ir a Obras", use_container_width=True): navegar_a(MENU_OBRAS)
    with col4:
        with st.container(border=True):
            st.subheader("👥 Admin")
            if st.button("Ir a Admin", use_container_width=True): navegar_a(MENU_ADMIN)

elif pagina == MENU_MAIL:
    if model: suite_correo.app(model)
    else: st.error("Error IA")

elif pagina == MENU_TAREAS:
    suite_tareas.app() # Llamada al nuevo módulo

elif pagina == MENU_OBRAS: suite_sustituciones.app()
elif pagina == MENU_ADMIN: suite_administradores.app()
