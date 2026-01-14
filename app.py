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

# --- 2. GESTIÓN DE SECRETOS ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Error: Configura los secretos en Streamlit Cloud.")
    st.stop()

# --- 3. LOGIN Y NAVEGACIÓN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def ir_a(pagina):
    st.session_state.navegacion = pagina
    st.rerun()

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
    
    if "navegacion" not in st.session_state:
        st.session_state.navegacion = "🏠 Inicio"
        
    menu_selection = st.radio(
        "Herramientas:",
        ["🏠 Inicio", "📧 Análisis de bandeja de entrada", "🚧 Gestión de Obras", "📄 Redactor de Contratos"],
        key="navegacion"
    )
    
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

# --- 4. MOTOR IA ---
genai.configure(api_key=API_KEY)
CANDIDATOS = ['gemini-flash-latest', 'gemini-1.5-flash-latest', 'gemini-pro-latest', 'models/gemini-1.5-flash-001']

if "model_name" not in st.session_state:
    for nombre in CANDIDATOS:
        try:
            t = genai.GenerativeModel(nombre); t.generate_content("Hola")
            st.session_state.model_name = nombre; break
        except: continue

if "model_name" in st.session_state:
    model = genai.GenerativeModel(st.session_state.model_name)
else:
    st.error("❌ Error conectando IA.")
    st.stop()

# --- 5. FUNCIONES ---
def leer_eml(f):
    try:
        b = f.getvalue(); msg = BytesParser(policy=policy.default).parsebytes(b)
        c = msg.get_body(preferencelist=('plain'))
        if c: return msg['from'], msg['subject'], c.get_content()
        return msg['from'], msg['subject'], "HTML/Imagen"
    except: return "?", "Error", "Error"

# =========================================================
#                 ZONA DE CONTENIDO
# =========================================================

# --- PANTALLA 1: DASHBOARD ---
if st.session_state.navegacion == "🏠 Inicio":
    st.title("🚀 Tu Centro de Mando")
    st.markdown("### Selecciona una herramienta para empezar:")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.write("📧")
            st.subheader("Bandeja de Entrada")
            st.write("Analiza y clasifica tus correos diarios masivamente con IA.")
            if st.button("Abrir Analizador", use_container_width=True):
                ir_a("📧 Análisis de bandeja de entrada")

    with col2:
        with st.container(border=True):
            st.write("🚧")
            st.subheader("Gestión de Obras")
            st.write("Semáforo de estado y seguimiento de incidencias técnicas.")
            if st.button("Gestionar Obras", use_container_width=True):
                ir_a("🚧 Gestión de Obras")

    with col3:
        with st.container(border=True):
            st.write("📄")
            st.subheader("Contratos")
            st.write("Redacción automática de contratos y renovaciones.")
            if st.button("Crear Documentos", use_container_width=True):
                ir_a("📄 Redactor de Contratos")

# --- PANTALLA 2: ANÁLISIS DE CORREOS ---
elif st.session_state.navegacion == "📧 Análisis de bandeja de entrada":
    st.title("📧 Análisis de Bandeja de Entrada")
    if st.button("⬅️ Volver al Inicio"):
        ir_a("🏠 Inicio")
        
    st.info("Sube tus archivos .msg o .eml para procesarlos.")

    with st.form("mail_form", clear_on_submit=True):
        uploaded_files = st.file_uploader("Arrastra archivos aquí", type=['msg', 'eml'], accept_multiple_files=True)
        submitted = st.form_submit_button("⚡ ANALIZAR AHORA")

    if submitted and uploaded_files:
        st.write("---")
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Lectura
            if uploaded_file.name.lower().endswith(".msg"):
                try: m = extract_msg.Message(uploaded_file); rem=m.sender; asu=m.subject; cue=m.body
                except: rem="?"; asu="Error"; cue=""
            else:
                rem, asu, cue = leer_eml(uploaded_file)
            
            if cue and len(cue)>15000: cue=cue[:15000]

            # --- AQUI ESTA EL CAMBIO IMPORTANTE: EL PROMPT ---
            prompt = f"""
            Actúa como mi Asistente Comercial experto. Analiza este correo:
            DE: {rem} | ASUNTO: {asu} | MENSAJE: {cue}
            
            Genera un reporte OBLIGATORIAMENTE con esta estructura exacta:

            1. **Clasificación**: Elige UNA de estas categorías exactas (copia el nombre tal cual): 
               [Ascensores PARADOS, Amenazas de BAJAS, IPOS Inspecciones de industria, DINAMIZACIONES y MODERNIZACIONES, SUSTITUCION de Ascensor, Validación de Partes de Trabajo PRs, DEUDA de clientes, Subidas de IPC, RENEGOCIACION de Contratos, FACTURACIÓN de Clientes, VENTA NUEVA, OTROS].
            
            2. **Resumen del correo**: Resumen del problema en 1 frase.
            
            3. **Accion a realizar**: Acción concreta que debo realizar yo.

            4. **Respuesta**:
            (Pon la respuesta dentro de un bloque de código para que se vea diferente, así:)
            ```text
            Hola [Nombre],
            ...cuerpo del mensaje...
            Saludos.
            ```
            """
            
            try:
                time.sleep(1)
                res = model.generate_content(prompt)
                with st.expander(f"📩 {asu}", expanded=True):
                    st.markdown(res.text)
            except Exception as e:
                st.error(f"Error: {e}")
            
            progress_bar.progress((i+1)/len(uploaded_files))
        st.success("✅ ¡Trabajo terminado!")

# --- OTRAS PANTALLAS ---
elif st.session_state.navegacion == "🚧 Gestión de Obras":
    st.title("🚧 Gestión de Obras")
    if st.button("⬅️ Volver"): ir_a("🏠 Inicio")
    st.warning("🛠️ Módulo en construcción.")

elif st.session_state.navegacion == "📄 Redactor de Contratos":
    st.title("📄 Redactor de Contratos")
    if st.button("⬅️ Volver"): ir_a("🏠 Inicio")
    st.warning("🛠️ Módulo en construcción.")
