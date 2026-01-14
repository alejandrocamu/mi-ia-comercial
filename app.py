import streamlit as st
import extract_msg
import google.generativeai as genai
import email
from email import policy
from email.parser import BytesParser
import time
import os

# --- 1. CONFIGURACIÓN GLOBAL ---
st.set_page_config(
    page_title="Suite Comercial IA",
    page_icon="🏢",
    layout="wide"
)

# --- 2. GESTIÓN DE SECRETOS (Login) ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Error: Configura los secretos (API Key o Password) en Streamlit Cloud.")
    st.stop()

# --- 3. BARRA LATERAL (LOGIN Y MENÚ) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/906/906343.png", width=80)
    st.title("Acceso Privado")
    
    # Login persistente (para que no te pida la clave al cambiar de menú)
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        input_pass = st.text_input("Contraseña", type="password")
        if input_pass == PASSWORD_REAL:
            st.session_state.authenticated = True
            st.rerun() # Recarga para mostrar el menú
        elif input_pass:
            st.warning("🔒 Clave incorrecta")
        st.stop() # Detiene todo si no está logueado

    # --- SI LLEGAMOS AQUÍ, ES QUE ESTÁ LOGUEADO ---
    st.success(f"Hola, Comercial 👋")
    st.divider()
    
    # MENÚ DE NAVEGACIÓN
    st.header("Herramientas")
    menu_selection = st.radio(
        "Selecciona una opción:",
        ["🏠 Inicio", "📧 Análisis de bandeja de entrada", "🚧 Gestión de Obras (Pronto)", "📄 Redactor de Contratos (Pronto)"]
    )
    
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

# --- 4. CONEXIÓN IA (Modo Todoterreno) ---
# Se ejecuta una vez y queda lista para cualquier herramienta
genai.configure(api_key=API_KEY)

CANDIDATOS = [
    'gemini-flash-latest', 
    'gemini-1.5-flash-latest', 
    'gemini-pro-latest',
    'models/gemini-1.5-flash-001'
]

# Buscamos modelo (cacheamos para no buscar cada vez)
if "model_name" not in st.session_state:
    for nombre in CANDIDATOS:
        try:
            test_model = genai.GenerativeModel(nombre)
            test_model.generate_content("Hola")
            st.session_state.model_name = nombre
            break
        except:
            continue

if "model_name" in st.session_state:
    model = genai.GenerativeModel(st.session_state.model_name)
    # st.sidebar.caption(f"✅ Motor: {st.session_state.model_name}") # (Opcional: ver motor)
else:
    st.error("❌ No se pudo conectar con la IA. Revisa tu API Key.")
    st.stop()


# --- 5. FUNCIONES AUXILIARES (Globales) ---
def leer_eml(uploaded_file):
    try:
        bytes_data = uploaded_file.getvalue()
        msg = BytesParser(policy=policy.default).parsebytes(bytes_data)
        asunto = msg['subject']
        remitente = msg['from']
        cuerpo = msg.get_body(preferencelist=('plain'))
        if cuerpo: return remitente, asunto, cuerpo.get_content()
        html_part = msg.get_body(preferencelist=('html'))
        if html_part: return remitente, asunto, "Solo HTML/Imágenes."
        return remitente, asunto, "Sin contenido texto"
    except:
        return "Desconocido", "Error lectura", "Error"

# =========================================================
#                 ZONA DE HERRAMIENTAS
# =========================================================

# --- OPCIÓN 1: PANTALLA DE INICIO ---
if menu_selection == "🏠 Inicio":
    st.title("🏢 Tu Centro de Comando")
    st.markdown("""
    Bienvenido a tu aplicación de optimización comercial.
    
    Selecciona una herramienta en el menú de la izquierda para empezar:
    
    * **📧 Análisis de bandeja de entrada:** Limpia tu correo diario con IA.
    * **🚧 Gestión de Obras:** (En desarrollo) Semáforo de estado de proyectos.
    * **📄 Redactor de Contratos:** (En desarrollo) Generación automática de docs.
    """)

# --- OPCIÓN 2: ANÁLISIS DE CORREOS (Tu herramienta actual) ---
elif menu_selection == "📧 Análisis de bandeja de entrada":
    st.title("📧 Análisis de bandeja de entrada")
    st.markdown("Sube aquí tus correos diarios para procesarlos masivamente.")

    with st.form("my-form", clear_on_submit=True):
        uploaded_files = st.file_uploader("Arrastra archivos .msg o .eml", type=['msg', 'eml'], accept_multiple_files=True)
        submitted = st.form_submit_button("ANALIZAR CORREOS")

    if submitted and uploaded_files:
        st.info(f"Procesando {len(uploaded_files)} correos con IA...")
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # 1. Leer
            if uploaded_file.name.lower().endswith(".msg"):
                try:
                    msg = extract_msg.Message(uploaded_file)
                    asunto = msg.subject; remitente = msg.sender; cuerpo = msg.body
                except:
                    asunto = "Error MSG"; remitente = "?"; cuerpo = ""
            else:
                remitente, asunto, cuerpo = leer_eml(uploaded_file)

            # 2. Recortar
            if cuerpo and len(cuerpo) > 15000: cuerpo = cuerpo[:15000]

            # 3. Prompt
            prompt = f"""
            Actúa como mi asistente comercial. Analiza:
            - DE: {remitente}
            - ASUNTO: {asunto}
            - MENSAJE: {cuerpo}
            
            GENERA REPORTE (Markdown):
            1. **CLASIFICACIÓN**: [VENTA 💰 / TRÁMITE 📄 / OBRA 🏗️ / BASURA 🗑️].
            2. **RESUMEN**: 1 frase.
            3. **ACCIÓN**: Qué debo hacer.
            4. **RESPUESTA**: Borrador de email.
            """

            try:
                time.sleep(1) # Pausa técnica
                response = model.generate_content(prompt)
                with st.expander(f"📩 {asunto}", expanded=True):
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        st.success("✅ Análisis completado.")

# --- OTRAS OPCIONES (Futuras) ---
else:
    st.title(f"{menu_selection}")
    st.info("🛠️ Esta herramienta está en construcción. ¡Pronto disponible!")
