import streamlit as st
import extract_msg
import google.generativeai as genai
import email
from email import policy
from email.parser import BytesParser
import time
import os
import datetime # Nueva librería para manejar fechas

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

# --- 3. GESTIÓN DE ESTADO (MEMORIA) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Aquí creamos la "Base de Datos" temporal en memoria
if "db_correos" not in st.session_state:
    st.session_state.db_correos = {} 
    # Estructura: {'2023-10-27': [ {datos_correo_1}, {datos_correo_2} ] }

def ir_a(pagina):
    st.session_state.navegacion = pagina
    st.rerun()

# --- 4. BARRA LATERAL ---
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
        
    # MENU ACTUALIZADO
    menu_selection = st.radio(
        "Menú Principal:",
        ["🏠 Inicio", "📮 Suite CORREO", "🚧 Gestión de Obras", "📄 Redactor de Contratos"],
        key="navegacion"
    )
    
    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. MOTOR IA ---
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

# --- 6. FUNCIONES AUXILIARES ---
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
    st.markdown("### Selecciona una herramienta:")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.write("📮")
            st.subheader("Suite CORREO")
            st.write("Analiza bandeja de entrada y gestiona tareas diarias.")
            if st.button("Ir al Correo", use_container_width=True):
                ir_a("📮 Suite CORREO")

    with col2:
        with st.container(border=True):
            st.write("🚧")
            st.subheader("Gestión de Obras")
            st.write("Semáforo de estado y seguimiento.")
            if st.button("Gestionar Obras", use_container_width=True):
                ir_a("🚧 Gestión de Obras")

    with col3:
        with st.container(border=True):
            st.write("📄")
            st.subheader("Contratos")
            st.write("Redacción automática de documentos.")
            if st.button("Crear Documentos", use_container_width=True):
                ir_a("📄 Redactor de Contratos")

# --- PANTALLA 2: SUITE CORREO (NUEVA ESTRUCTURA) ---
elif st.session_state.navegacion == "📮 Suite CORREO":
    st.title("📮 Suite CORREO")
    if st.button("⬅️ Volver al Inicio"): ir_a("🏠 Inicio")
    
    # CREAMOS LAS PESTAÑAS
    tab1, tab2 = st.tabs(["📤 Análisis de Bandeja de Entrada", "📅 Tareas Diarias (Calendario)"])

    # --- PESTAÑA 1: SUBIDA Y ANÁLISIS ---
    with tab1:
        st.header("Analizar Nuevos Correos")
        st.info("Sube tus archivos .msg o .eml. Los resultados se guardarán en 'Tareas Diarias'.")

        with st.form("mail_form", clear_on_submit=True):
            uploaded_files = st.file_uploader("Arrastra archivos aquí", type=['msg', 'eml'], accept_multiple_files=True)
            submitted = st.form_submit_button("⚡ ANALIZAR Y GUARDAR")

        if submitted and uploaded_files:
            st.write("---")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Lista temporal para guardar los resultados de ESTA tanda
            resultados_tanda = []

            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Analizando correo {i+1} de {len(uploaded_files)}...")
                
                # Lectura
                if uploaded_file.name.lower().endswith(".msg"):
                    try: m = extract_msg.Message(uploaded_file); rem=m.sender; asu=m.subject; cue=m.body
                    except: rem="?"; asu="Error"; cue=""
                else:
                    rem, asu, cue = leer_eml(uploaded_file)
                
                if cue and len(cue)>15000: cue=cue[:15000]

                # Prompt Estricto
                prompt = f"""
                Actúa como mi Asistente Comercial experto. Analiza este correo:
                DE: {rem} | ASUNTO: {asu} | MENSAJE: {cue}
                
                Genera un reporte OBLIGATORIAMENTE con esta estructura exacta:

                1. **Clasificación**: Elige UNA de estas categorías exactas: 
                [Ascensores PARADOS, Amenazas de BAJAS, IPOS Inspecciones de industria, DINAMIZACIONES y MODERNIZACIONES, SUSTITUCION de Ascensor, Validación de Partes de Trabajo PRs, DEUDA de clientes, Subidas de IPC, RENEGOCIACION de Contratos, FACTURACIÓN de Clientes, VENTA NUEVA, OTROS].
                
                2. **Resumen del correo**: Resumen del problema en 1 frase.
                
                3. **Accion a realizar**: Acción concreta que debo realizar yo.

                4. **Respuesta**:
                (Pon la respuesta dentro de un bloque de código formato texto para copiar y pegar):
                ```text
                Hola...
                ```
                """
                
                try:
                    time.sleep(1)
                    res = model.generate_content(prompt)
                    
                    # Guardamos el resultado en memoria en vez de mostrarlo
                    resultados_tanda.append({
                        "asunto": asu,
                        "analisis": res.text,
                        "hora": datetime.datetime.now().strftime("%H:%M")
                    })
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                
                progress_bar.progress((i+1)/len(uploaded_files))
            
            # --- GUARDADO EN MEMORIA ---
            hoy_str = str(datetime.date.today()) # Ej: '2023-10-27'
            
            # Si ya había cosas hoy, añadimos las nuevas, si no, creamos la lista
            if hoy_str in st.session_state.db_correos:
                st.session_state.db_correos[hoy_str].extend(resultados_tanda)
            else:
                st.session_state.db_correos[hoy_str] = resultados_tanda

            status_text.empty()
            st.success("✅ Bandeja de entrada analizada y respuestas generadas.")
            st.info("👉 Ve a la pestaña **'Tareas Diarias'** para ver los resultados.")

    # --- PESTAÑA 2: CALENDARIO Y TAREAS ---
    with tab2:
        st.header("📅 Tareas Diarias")
        
        col_cal, col_info = st.columns([1, 3])
        
        with col_cal:
            # Selector de fecha (Calendario)
            fecha_selec = st.date_input("Sele
