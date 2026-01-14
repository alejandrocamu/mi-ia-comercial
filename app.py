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

# --- 2. SECRETOS ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Error crítico: No se encuentran los secretos.")
    st.stop()

# --- 3. ESTADOS DE SESIÓN ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "navegacion" not in st.session_state: st.session_state.navegacion = "🏠 Inicio"
if "db_correos" not in st.session_state: st.session_state.db_correos = {} 

def navegar_a(pagina):
    st.session_state.navegacion = pagina
    st.rerun()

# --- 4. BARRA LATERAL (Limpia) ---
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

    st.success("Hola, Comercial 👋")
    st.divider()
    
    # MENÚ
    opciones = ["🏠 Inicio", "📮 Suite CORREO", "🔧 Suite SUSTITUCIONES", "👥 Suite ADMINISTRADORES"]
    
    # --- AQUÍ ESTABA EL ERROR ---
    # Ahora está completo: try + except
    try:
        idx = opciones.index(st.session_state.navegacion)
    except:
        idx = 0
    # ----------------------------
    
    seleccion = st.radio("Herramientas:", opciones, index=idx)
    
    if seleccion != st.session_state.navegacion:
        st.session_state.navegacion = seleccion
        st.rerun()
        
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. CONEXIÓN IA (MODO DIAGNÓSTICO) ---
genai.configure(api_key=API_KEY)

try:
    # Usamos Gemini 1.5 Flash (requiere facturación o proyecto nuevo)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prueba de conexión
    # model.generate_content("Hola") # Descomentar para probar silenciosamente

except Exception as e:
    st.error("❌ ERROR DE CONEXIÓN")
    st.code(str(e)) # Muestra el error técnico real
    st.stop()

# =========================================================
#                 ZONA DE CONTENIDO
# =========================================================

if st.session_state.navegacion == "🏠 Inicio":
    st.title("🚀 Tu Centro de Mando")
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.subheader("📮 Suite CORREO")
            if st.button("Ir al Correo", use_container_width=True): navegar_a("📮 Suite CORREO")
    with col2:
        with st.container(border=True):
            st.subheader("🔧 Sustituciones")
            if st.button("Ir a Sustituciones", use_container_width=True): navegar_a("🔧 Suite SUSTITUCIONES")
    with col3:
        with st.container(border=True):
            st.subheader("👥 Administradores")
            if st.button("Ir a Administradores", use_container_width=True): navegar_a("👥 Suite ADMINISTRADORES")

elif st.session_state.navegacion == "📮 Suite CORREO":
    suite_correo.app(model)

elif st.session_state.navegacion == "🔧 Suite SUSTITUCIONES":
    suite_sustituciones.app()

elif st.session_state.navegacion == "👥 Suite ADMINISTRADORES":
    suite_administradores.app()
