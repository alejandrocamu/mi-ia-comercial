import streamlit as st
import google.generativeai as genai
import os

# --- IMPORTAMOS MÓDULOS ---
import suite_correo
import suite_sustituciones
import suite_administradores

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Suite Comercial IA", page_icon="🏢", layout="wide")

# --- LISTAS ---
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
    st.error("⚠️ Configura los secretos."); st.stop()

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

# --- 4. MOTOR IA (MODO SUPERVIVENCIA) ---
genai.configure(api_key=API_KEY)

# Lista ampliada para encontrar ALGO que funcione en tu cuenta
CANDIDATOS = [
    'gemini-1.5-flash',          # El ideal (1500 usos)
    'gemini-1.5-flash-001',      # Variante nombre
    'models/gemini-1.5-flash',   # Variante con prefijo
    'gemini-2.0-flash-lite-preview-02-05', # Tu modelo 'Lite' (quizás tenga cupo)
    'models/gemini-2.0-flash-lite-preview-02-05',
    'gemini-2.0-flash',          # El que te dio error 429 (último recurso)
    'gemini-pro'                 # El clásico
]

if "model_name" not in st.session_state or st.sidebar.button("♻️ Reiniciar IA"):
    st.session_state.model_name = None
    errores_log = []
    
    # Probamos uno por uno
    for nombre in CANDIDATOS:
        try:
            t = genai.GenerativeModel(nombre)
            t.generate_content("Test") # Prueba real
            st.session_state.model_name = nombre
            break # ¡Encontramos uno!
        except Exception as e:
            errores_log.append(f"{nombre}: {str(e)}")
            continue

if st.session_state.model_name:
    model = genai.GenerativeModel(st.session_state.model_name)
    # st.sidebar.caption(f"✅ Conectado a: {st.session_state.model_name}")
else:
    st.error("❌ ERROR CRÍTICO: Ningún modelo funciona con tu API Key.")
    st.write("Detalle de errores:")
    st.code("\n".join(errores_log))
    st.warning("👉 SOLUCIÓN: Crea una NUEVA API Key en un NUEVO PROYECTO en Google AI Studio.")
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
