import streamlit as st
import google.generativeai as genai
import os

# --- IMPORTAMOS LOS MÓDULOS ---
import suite_correo
import suite_sustituciones
import suite_administradores

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Suite Comercial IA", page_icon="🏢", layout="wide")

MENU_INICIO = "🏠 Inicio"
MENU_CORREO = "📮 Suite CORREO"
MENU_SUSTITUCIONES = "🔧 Suite SUSTITUCIONES"
MENU_ADMINISTRADORES = "👥 Suite ADMINISTRADORES"
OPCIONES_MENU = [MENU_INICIO, MENU_CORREO, MENU_SUSTITUCIONES, MENU_ADMINISTRADORES]

# --- 2. SECRETOS ---
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
    st.session_state.navegacion = pagina; st.rerun()

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906343.png", width=80)
    st.title("Acceso Privado")
    if not st.session_state.authenticated:
        input_pass = st.text_input("Contraseña", type="password")
        if input_pass == PASSWORD_REAL:
            st.session_state.authenticated = True; st.rerun()
        elif input_pass: st.warning("🔒 Clave incorrecta"); st.stop()
        else: st.stop()

    st.success(f"Hola, Comercial 👋")
    st.divider()
    
    try: indice = OPCIONES_MENU.index(st.session_state.navegacion)
    except: indice = 0; st.session_state.navegacion = MENU_INICIO
    seleccion = st.radio("Herramientas:", OPCIONES_MENU, index=indice)
    if seleccion != st.session_state.navegacion:
        st.session_state.navegacion = seleccion; st.rerun()
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False; st.rerun()

# --- 4. MOTOR IA (Configuración Estándar) ---
genai.configure(api_key=API_KEY)

# Con la llave nueva, ESTE modelo funcionará seguro.
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    # Hacemos una llamada muda para confirmar que la llave nueva funciona
    model.generate_content("test")
except Exception as e:
    st.error("❌ Error conectando con la IA.")
    st.error(f"Detalle: {e}")
    st.info("💡 Asegúrate de haber cambiado la API Key en los 'Secrets' por una creada en un PROYECTO NUEVO.")
    st.stop()

# --- ROUTER ---
if st.session_state.navegacion == MENU_INICIO:
    st.title("🚀 Tu Centro de Mando")
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.write("📮"); st.subheader("Suite CORREO")
            if st.button("Ir al Correo", use_container_width=True): ir_a(MENU_CORREO)
    with col2:
        with st.container(border=True):
            st.write("🔧"); st.subheader("Sustituciones")
            if st.button("Ir a Sustituciones", use_container_width=True): ir_a(MENU_SUSTITUCIONES)
    with col3:
        with st.container(border=True):
            st.write("👥"); st.subheader("Administradores")
            if st.button("Ir a Administradores", use_container_width=True): ir_a(MENU_ADMINISTRADORES)

elif st.session_state.navegacion == MENU_CORREO: suite_correo.app(model) 
elif st.session_state.navegacion == MENU_SUSTITUCIONES: suite_sustituciones.app() 
elif st.session_state.navegacion == MENU_ADMINISTRADORES: suite_administradores.app()
