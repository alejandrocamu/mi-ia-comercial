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

# --- 2. SECRETOS Y NAVEGACIÓN ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Error: Configura los secretos en Streamlit Cloud.")
    st.stop()

# Inicializar estados
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "db_correos" not in st.session_state: st.session_state.db_correos = {} 
if "navegacion" not in st.session_state: st.session_state.navegacion = "🏠 Inicio"

def navegar_a(pagina):
    st.session_state.navegacion = pagina
    st.rerun()

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906343.png", width=80)
    st.title("Acceso Privado")
    
    if not st.session_state.authenticated:
        input_pass = st.text_input("Contraseña", type="password")
        if input_pass == PASSWORD_REAL:
            st.session_state.authenticated = True
            st.rerun()
        elif input_pass:
            st.warning("🔒 Incorrecta")
        st.stop()

    st.success("Hola, Comercial 👋")
    st.divider()
    
    opciones = ["🏠 Inicio", "📮 Suite CORREO", "🔧 Suite SUSTITUCIONES", "👥 Suite ADMINISTRADORES"]
    try: idx = opciones.index(st.session_state.navegacion)
    except: idx = 0
        
    seleccion = st.radio("Herramientas:", opciones, index=idx)
    
    if seleccion != st.session_state.navegacion:
        st.session_state.navegacion = seleccion
        st.rerun()
        
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()

# --- 4. CONEXIÓN IA (CONFIGURADO PARA GEMINI PRO) ---
genai.configure(api_key=API_KEY)

# Lista de modelos "Pro" (Versión 1.0 y 1.5 Pro)
# Estos suelen tener buenos límites y aparecían en tu lista.
CANDIDATOS = [
    'gemini-pro',          # El clásico 1.0 (Muy estable)
    'gemini-pro-latest',   # Variante que tenías en tu lista
    'models/gemini-pro',
    'gemini-1.5-pro',      # Versión potente (si la tienes activa)
    'gemini-1.5-pro-latest'
]

if "model_name" not in st.session_state:
    st.session_state.model_name = None
    # Buscamos cuál funciona
    for nombre in CANDIDATOS:
        try:
            test_model = genai.GenerativeModel(nombre)
            test_model.generate_content("Hola") # Prueba de conexión
            st.session_state.model_name = nombre
            break
        except:
            continue

if st.session_state.model_name:
    model = genai.GenerativeModel(st.session_state.model_name)
    # st.sidebar.success(f"Motor: {st.session_state.model_name}") # Descomenta si quieres ver cuál usas
else:
    st.error("❌ No se encuentra ningún modelo 'Gemini Pro' en tu cuenta.")
    st.warning("Intenta crear una API KEY nueva en un proyecto nuevo de Google AI Studio.")
    st.stop()

# =========================================================
#                 ZONA DE CONTENIDO
# =========================================================

# PANTALLA DE INICIO
if st.session_state.navegacion == "🏠 Inicio":
    st.title("🚀 Tu Centro de Mando")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.subheader("📮 Suite CORREO")
            st.write("Analizar emails y tareas.")
            if st.button("Ir al Correo", use_container_width=True):
                navegar_a("📮 Suite CORREO")
            
    with col2:
        with st.container(border=True):
            st.subheader("🔧 Sustituciones")
            st.write("Gestión técnica.")
            if st.button("Ir a Sustituciones", use_container_width=True):
                navegar_a("🔧 Suite SUSTITUCIONES")
            
    with col3:
        with st.container(border=True):
            st.subheader("👥 Administradores")
            st.write("Gestión de fincas.")
            if st.button("Ir a Administradores", use_container_width=True):
                navegar_a("👥 Suite ADMINISTRADORES")

# PANTALLAS DE HERRAMIENTAS
elif st.session_state.navegacion == "📮 Suite CORREO":
    try: suite_correo.app(model)
    except Exception as e: st.error(f"Error módulo correo: {e}")

elif st.session_state.navegacion == "🔧 Suite SUSTITUCIONES":
    try: suite_sustituciones.app()
    except Exception as e: st.error(f"Error módulo sustituciones: {e}")

elif st.session_state.navegacion == "👥 Suite ADMINISTRADORES":
    try: suite_administradores.app()
    except Exception as e: st.error(f"Error módulo administradores: {e}")
