import streamlit as st
import extract_msg
import google.generativeai as genai
import email
from email import policy
from email.parser import BytesParser
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

# --- 4. MODELO (CAMBIO IMPORTANTE: Usamos gemini-pro) ---
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro') 

# --- 5. FUNCIONES ---
def leer_eml(uploaded_file):
    try:
        bytes_data = uploaded_file.getvalue()
        msg = BytesParser(policy=policy.default).parsebytes(bytes_data)
        asunto = msg['subject']
        remitente = msg['from']
        cuerpo = msg.get_body(preferencelist=('plain')).get_content()
        if not cuerpo: cuerpo = "Sin contenido texto"
        return remitente, asunto, cuerpo
    except:
        return "Desconocido", "Error lectura", "No se pudo leer el archivo"

# --- 6. INTERFAZ ---
st.title("🛡️ El Filtro: Tu Asistente de Operaciones")
st.markdown("Arrastra tus correos (.eml o .msg).")

uploaded_files = st.file_uploader("Zona de carga", type=['msg', 'eml'], accept_multiple_files=True)

if uploaded_files:
    st.info(f"Analizando {len(uploaded_files)} correos...")
    
    for uploaded_file in uploaded_files:
        # Detectar formato
        if uploaded_file.name.lower().endswith(".msg"):
            try:
                msg = extract_msg.Message(uploaded_file)
                asunto = msg.subject
                remitente = msg.sender
                cuerpo = msg.body
            except:
                asunto = "Error MSG"; remitente = "?"; cuerpo = ""
        else:
            remitente, asunto, cuerpo = leer_eml(uploaded_file)

        # Recortar para no saturar
        if cuerpo and len(cuerpo) > 4000: cuerpo = cuerpo[:4000]

        # Prompt
        prompt = f"""
        Actúa como mi secretario. Analiza este email:
        DE: {remitente} | ASUNTO: {asunto} | MENSAJE: {cuerpo}
        
        DAME ESTA RESPUESTA (Formato Markdown):
        1. **CATEGORÍA**: [VENTAS / ADMIN / OBRA / BASURA]
        2. **RESUMEN**: 1 línea.
        3. **ACCIÓN**: Qué hago.
        4. **RESPUESTA**: Borrador de email para responder.
        """

        try:
            response = model.generate_content(prompt)
            with st.expander(f"📩 {asunto}", expanded=True):
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Error con este correo: {e}")
