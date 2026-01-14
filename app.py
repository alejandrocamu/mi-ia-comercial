import streamlit as st
import google.generativeai as genai
import os

# --- IMPORTAMOS TUS MÓDULOS ---
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
        st.rerun()

# --- 4. CONEXIÓN IA (LISTA EXACTA DE TU DIAGNÓSTICO) ---
genai.configure(api_key=API_KEY)

# Esta lista contiene SOLO los modelos que salieron en tu diagnóstico.
# Priorizamos el "Lite" esperando que tenga menos restricciones.
CANDIDATOS = [
    'gemini-2.0-flash-lite-preview-02-05', # Intento 1: El ligero
    'gemini-2.0-flash-lite',                # Intento 2: Alias del ligero
    'gemini-2.0-flash',                     # Intento 3: El potente (Límite 20)
    'gemini-flash-latest'                   # Intento 4: El genérico
]

if "model_name" not in st.session_state:
    st.session_state.model_name = None
    
    # Buscamos desesperadamente uno que funcione
    for nombre in CANDIDATOS:
        try:
            t = genai.GenerativeModel(nombre)
            t.generate_content("Hola") # Prueba de vida
            st.session_state.model_name = nombre
            break
        except:
            continue

if st.session_state.model_name:
    model = genai.GenerativeModel(st.session_state.model_name)
    # st.sidebar.caption(f"Motor activo: {st.session_state.model_name}") 
else:
    st.error("⛔ BLOQUEO TOTAL DE GOOGLE")
    st.warning("""
    Tu API Key actual está bloqueada por exceso de uso (Límite 20/día) y no tiene acceso a los modelos ilimitados.
    
    SOLUCIÓN ÚNICA:
    1. Ve a aistudio.google.com
    2. Crea una API Key nueva en un PROYECTO NUEVO.
    3. Ponla en los Secrets de Streamlit.
    """)
    st.stop()

# =========================================================
#                 ZONA DE CONTENIDO
# =========================================================

# INICIO
if st.session_state.navegacion == "🏠 Inicio":
    st.title("🚀 Tu Centro de Mando")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.subheader("📮 Suite CORREO")
            st.write("Analizar emails.")
            if st.button("Ir al Correo", use_container_width=True): navegar_a("📮 Suite CORREO")
            
    with col2:
        with st.container(border=True):
            st.subheader("🔧 Sustituciones")
            st.write("Gestión técnica.")
            if st.button("Ir a Sustituciones", use_container_width=True): navegar_a("🔧 Suite SUSTITUCIONES")
            
    with col3:
        with st.container(border=True):
            st.subheader("👥 Administradores")
            st.write("Fincas y contratos.")
            if st.button("Ir a Administradores", use_container_width=True): navegar_a("👥 Suite ADMINISTRADORES")

# HERRAMIENTAS
elif st.session_state.navegacion == "📮 Suite CORREO":
    try: suite_correo.app(model)
    except Exception as e: st.error(f"Error Correo: {e}")

elif st.session_state.navegacion == "🔧 Suite SUSTITUCIONES":
    try: suite_sustituciones.app()
    except Exception as e: st.error(f"Error Sustituciones: {e}")

elif st.session_state.navegacion == "👥 Suite ADMINISTRADORES":
    try: suite_administradores.app()
    except Exception as e: st.error(f"Error Administradores: {e}")
