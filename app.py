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
if "model_name" not in st.session_state: st.session_state.model_name = None

# Función para navegar de forma segura
def navegar_a(pagina):
    st.session_state.navegacion = pagina
    st.rerun()

# --- 4. BARRA LATERAL ---
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

    st.success("Hola, Comercial 👋")
    st.divider()
    
    # Lógica del menú robusta
    try:
        idx = OPCIONES_MENU.index(st.session_state.navegacion)
    except:
        idx = 0
        st.session_state.navegacion = MENU_HOME # Forzar corrección si hay error
    
    seleccion = st.radio("Herramientas:", OPCIONES_MENU, index=idx)
    
    if seleccion != st.session_state.navegacion:
        st.session_state.navegacion = seleccion
        st.rerun()
        
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. CONEXIÓN IA (Modelos 2.0 / Latest) ---
# Solo intentamos conectar si NO estamos en el inicio, para agilizar la carga
# O si ya tenemos el modelo cargado
genai.configure(api_key=API_KEY)
CANDIDATOS = ['gemini-2.0-flash-exp', 'gemini-2.0-flash', 'gemini-flash-latest']

if st.session_state.model_name is None:
    for nombre in CANDIDATOS:
        try:
            test_model = genai.GenerativeModel(nombre)
            test_model.generate_content("Test")
            st.session_state.model_name = nombre
            break
        except: continue

if st.session_state.model_name:
    model = genai.GenerativeModel(st.session_state.model_name)
else:
    # Si falla la IA, no rompemos toda la app, solo avisamos
    model = None 

# =========================================================
#                 ZONA DE CONTENIDO
# =========================================================

# Usamos una variable auxiliar para limpiar el código
pagina_actual = st.session_state.navegacion

# --- PANTALLA 1: INICIO ---
if pagina_actual == MENU_HOME:
    st.title("🚀 Tu Centro de Mando")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.subheader("📮 Suite CORREO")
            st.write("Analizar emails.")
            if st.button("Ir al Correo", use_container_width=True): navegar_a(MENU_MAIL)
            
    with col2:
        with st.container(border=True):
            st.subheader("🔧 Sustituciones")
            st.write("Gestión técnica.")
            if st.button("Ir a Sustituciones", use_container_width=True): navegar_a(MENU_OBRAS)
            
    with col3:
        with st.container(border=True):
            st.subheader("👥 Administradores")
            st.write("Fincas.")
            if st.button("Ir a Administradores", use_container_width=True): navegar_a(MENU_ADMIN)

# --- PANTALLAS DE HERRAMIENTAS ---
elif pagina_actual == MENU_MAIL:
    if model:
        try: suite_correo.app(model)
        except Exception as e: st.error(f"Error interno: {e}")
    else:
        st.error("❌ La IA no está disponible (Límite de cuota alcanzado).")

elif pagina_actual == MENU_OBRAS:
    suite_sustituciones.app()

elif pagina_actual == MENU_ADMIN:
    suite_administradores.app()

# --- RED DE SEGURIDAD (Si todo falla, muestra esto) ---
else:
    st.warning("⚠️ Página no encontrada. Redirigiendo...")
    if st.button("Volver al Inicio Seguro"):
        navegar_a(MENU_HOME)
