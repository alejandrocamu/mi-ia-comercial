import streamlit as st
import extract_msg
import google.generativeai as genai
import email
from email import policy
from email.parser import BytesParser
import time
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Asistente Comercial", page_icon="🛡️", layout="wide")

# --- 2. SECRETOS ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Error: Configura los secretos en Streamlit Cloud.")
    st.stop()

# --- 3. LOGIN ---
with st.sidebar:
    st.title("Acceso Privado")
    input_pass = st.text_input("Contraseña", type="password")
    if input_pass != PASSWORD_REAL:
        st.warning("🔒 Bloqueado")
        st.stop()
    else:
        st.success("🔓 Acceso OK")

# --- 4. SELECCIÓN AUTOMÁTICA DE MODELO (MODO TODOTERRENO) ---
genai.configure(api_key=API_KEY)

# Lista de nombres posibles según tu catálogo personal.
# El código probará uno por uno hasta que conecte.
CANDIDATOS = [
    'gemini-flash-latest',       # El que salía en tu lista
    'gemini-1.5-flash-latest',   # Otra variante común
    'gemini-pro-latest',         # Versión estándar
    'models/gemini-1.5-flash-001' # Nombre técnico completo
]

model = None
model_name_usado = ""

# Probamos conectar con el primer modelo que funcione
for nombre in CANDIDATOS:
    try:
        test_model = genai.GenerativeModel(nombre)
        # Hacemos una prueba muda para ver si responde sin error 404
        test_model.generate_content("Hola") 
        model = test_model
        model_name_usado = nombre
        break # ¡Si funciona, dejamos de buscar!
    except Exception:
        continue # Si falla, probamos el siguiente

if model is None:
    st.error("❌ No se pudo conectar con ningún modelo gratuito. Revisa tu API Key.")
    st.stop()
else:
    st.sidebar.success(f"✅ Conectado a: {model_name_usado}")

# --- 5. FUNCIONES ---
def leer_eml(uploaded_file):
    try:
        bytes_data = uploaded_file.getvalue()
        msg = BytesParser(policy=policy.default).parsebytes(bytes_data)
        asunto = msg['subject']
        remitente = msg['from']
        cuerpo = msg.get_body(preferencelist=('plain'))
        if cuerpo:
            return remitente, asunto, cuerpo.get_content()
        html_part = msg.get_body(preferencelist=('html'))
        if html_part: return remitente, asunto, "Solo contenido HTML/Imágenes."
        return remitente, asunto, "Sin contenido texto"
    except:
        return "Desconocido", "Error lectura", "No se pudo leer"

# --- 6. INTERFAZ ---
st.title("🛡️ El Filtro: Tu Asistente de Operaciones")
st.markdown("Arrastra tus correos **(.eml o .msg)**.")

uploaded_files = st.file_uploader("Zona de carga", type=['msg', 'eml'], accept_multiple_files=True)

if uploaded_files:
    st.info(f"Analizando {len(uploaded_files)} correos...")
    progress_bar = st.progress(0)
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Leer archivo
        if uploaded_file.name.lower().endswith(".msg"):
            try:
                msg = extract_msg.Message(uploaded_file)
                asunto = msg.subject; remitente = msg.sender; cuerpo = msg.body
            except:
                asunto = "Error MSG"; remitente = "?"; cuerpo = ""
        else:
            remitente, asunto, cuerpo = leer_eml(uploaded_file)

        # Recortar
        if cuerpo and len(cuerpo) > 15000: cuerpo = cuerpo[:15000]

        # Prompt
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
            time.sleep(1.5) # Pausa anti-bloqueo
            response = model.generate_content(prompt)
            with st.expander(f"📩 {asunto}", expanded=True):
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
            if "429" in str(e): st.warning("⏳ Espera un momento (Límite de velocidad).")
        
        progress_bar.progress((i + 1) / len(uploaded_files))
