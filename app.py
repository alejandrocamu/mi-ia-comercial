import streamlit as st
import google.generativeai as genai
import os

# --- IMPORTAMOS LOS MÓDULOS ---
import suite_correo
import suite_sustituciones
import suite_administradores

# --- 1. CONFIGURACIÓN GLOBAL ---
st.set_page_config(
    page_title="Suite Comercial IA",
    page_icon="🏢",
    layout="wide"
)

# --- LISTA MAESTRA DE NAVEGACIÓN ---
MENU_INICIO = "🏠 Inicio"
MENU_CORREO = "📮 Suite CORREO"
MENU_SUSTITUCIONES = "🔧 Suite SUSTITUCIONES"
MENU_ADMINISTRADORES = "👥 Suite ADMINISTRADORES"

OPCIONES_MENU = [MENU_INICIO, MENU_CORREO, MENU_SUSTITUCIONES, MENU_ADMINISTRADORES]

# --- 2. GESTIÓN DE SECRETOS Y MEMORIA ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Configura los secretos en Streamlit Cloud.")
    st.stop()

if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "db_correos" not in st.session_state: st.session_state.db_correos = {} 
if "navegacion" not in st.session_state: st.session_state.navegacion = MENU_INICIO

def ir_a(pagina):
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
            st.warning("🔒 Clave incorrecta")
        st.stop()

    st.success(f"Hola, Comercial 👋")
    st.divider()
    
    # Sincronización del menú
    try: indice = OPCIONES_MENU.index(st.session_state.navegacion)
    except: indice = 0; st.session_state.navegacion = MENU_INICIO

    seleccion = st.radio("Herramientas:", OPCIONES_MENU, index=indice)

    if seleccion != st.session_state.navegacion:
        st.session_state.navegacion = seleccion
        st.rerun()
    
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

# --- 4. MOTOR IA (CORREGIDO PARA EVITAR LÍMITE 20/DÍA) ---
genai.configure(api_key=API_KEY)

# HEMOS CAMBIADO EL ORDEN AQUÍ:
# Ponemos primero 'gemini-1.5-flash' explícitamente.
# Este modelo tiene 1500 peticiones diarias gratis.
# Quitamos los 'latest' para que no nos cuele el modelo 2.5 experimental.
CANDIDATOS = [
    'gemini-1.5-flash',      # PRIORIDAD 1: El estable y generoso
    'models/gemini-1.5-flash-001',
    'gemini-1.5-pro',
    'gemini-pro'
]

if "model_name" not in st.session_state:
    for nombre in CANDIDATOS:
        try:
            t = genai.GenerativeModel(nombre); t.generate_content("Hola")
            st.session_state.model_name = nombre; break
        except: continue

if "model_name" in st.session_state:
    model = genai.GenerativeModel(st.session_state.model_name)
    # st.sidebar.caption(f"Motor: {st.session_state.model_name}") # Descomenta para ver cuál usa
else:
    st.error("❌ Error IA."); st.stop()

# =========================================================
#                 ROUTER (CONTROLADOR DE PÁGINAS)
# =========================================================

# PANTALLA DE INICIO
if st.session_state.navegacion == MENU_INICIO:
    st.title("🚀 Tu Centro de Mando")
    st.markdown("### Selecciona una herramienta:")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    
    # TARJETA 1: CORREO
    with col1:
        with st.container(border=True):
            st.write("📮"); st.subheader("Suite CORREO")
            st.write("Análisis de emails y tareas.")
            if st.button("Ir al Correo", use_container_width=True): ir_a(MENU_CORREO)
            
    # TARJETA 2: SUSTITUCIONES
    with col2:
        with st.container(border=True):
            st.write("🔧"); st.subheader("Sustituciones")
            st.write("Gestión técnica de cambios.")
            if st.button("Ir a Sustituciones", use_container_width=True): ir_a(MENU_SUSTITUCIONES)
            
    # TARJETA 3: ADMINISTRADORES
    with col3:
        with st.container(border=True):
            st.write("👥"); st.subheader("Administradores")
            st.write("Gestión de fincas y contratos.")
            if st.button("Ir a Administradores", use_container_width=True): ir_a(MENU_ADMINISTRADORES)

# PANTALLAS DE HERRAMIENTAS
elif st.session_state.navegacion == MENU_CORREO:
    suite_correo.app(model) 

elif st.session_state.navegacion == MENU_SUSTITUCIONES:
    suite_sustituciones.app() 

elif st.session_state.navegacion == MENU_ADMINISTRADORES:
    suite_administradores.app()
