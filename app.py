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

# --- 4. CONEXIÓN IA (Modo PRO) ---
genai.configure(api_key=API_KEY)

# Usamos DIRECTAMENTE el modelo 1.5 Flash.
# Al tener la facturación activada, este modelo vuela y no tiene límites diarios.
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    # Pequeña prueba silenciosa para asegurar conexión
    model.generate_content("test")
except Exception as e:
    st.error("❌ Error de conexión.")
    st.info("Asegúrate de que la API Key en 'Secrets' pertenece a tu proyecto con facturación activada.")
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
            st.write("Analizar emails masivamente.")
            if st.button("Ir al Correo", use_container_width=True): navegar_a("📮 Suite CORREO")
            
    with col2:
        with st.container(border=True):
            st.subheader("🔧 Sustituciones")
            st.write("Gestión técnica y obras.")
            if st.button("Ir a Sustituciones", use_container_width=True): navegar_a("🔧 Suite SUSTITUCIONES")
            
    with col3:
        with st.container(border=True):
            st.subheader("👥 Administradores")
            st.write("Gestión de fincas.")
            if st.button("Ir a Administradores", use_container_width=True): navegar_a("👥 Suite ADMINISTRADORES")

# HERRAMIENTAS
elif st.session_state.navegacion == "📮 Suite CORREO":
    try: suite_correo.app(model)
    except Exception as e: st.error(f"Error: {e}")

elif st.session_state.navegacion == "🔧 Suite SUSTITUCIONES":
    try: suite_sustituciones.app()
    except Exception as e: st.error(f"Error: {e}")

elif st.session_state.navegacion == "👥 Suite ADMINISTRADORES":
    try: suite_administradores.app()
    except Exception as e: st.error(f"Error: {e}")
