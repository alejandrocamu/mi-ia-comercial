import streamlit as st
import extract_msg
import google.generativeai as genai
import email
from email import policy
from email.parser import BytesParser
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="Asistente Comercial 2.0",
    page_icon="🚀",
    layout="wide"
)

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

# --- 4. MODELO (USAMOS EL NUEVO GEMINI 2.0) ---
genai.configure(api_key=API_KEY)

# Usamos 'gemini-2.0-flash' que aparece explícitamente en tu lista
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    st.sidebar.caption("✅ Motor: Gemini 2.0 Flash")
except Exception as e:
    st.error(f"Error configurando el modelo: {e}")

# --- 5. FUNCIONES ---
def leer_eml(uploaded_file):
    try:
        bytes_data = uploaded_file.getvalue()
        msg = BytesParser(policy=policy.default).parsebytes(bytes_data)
        asunto = msg['subject']
        remitente = msg['from']
        
        # Extraer texto plano si existe
        cuerpo = msg.get_body(preferencelist=('plain'))
        if cuerpo:
            return remitente, asunto, cuerpo.get_content()
        
        # Si no, buscar HTML
        html_part = msg.get_body(preferencelist=('html'))
        if html_part:
            return remitente, asunto, "El correo solo tiene contenido HTML (posiblemente imágenes o diseño)."
            
        return remitente, asunto, "Sin contenido legible"
    except:
        return "Desconocido", "Error lectura", "No se pudo leer el archivo"

# --- 6. INTERFAZ ---
st.title("🚀 El Filtro: Tu Asistente de Operaciones")
st.markdown("Arrastra tus correos **(.eml o .msg)**. Usando IA de última generación.")

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

        # Recortar para no saturar (Gemini 2.0 aguanta mucho, subimos el límite)
        if cuerpo and len(cuerpo) > 10000: cuerpo = cuerpo[:10000]

        # Prompt
        prompt = f"""
        Actúa como mi secretario ejecutivo eficiente. Analiza este email:
        
        DE: {remitente}
        ASUNTO: {asunto}
        MENSAJE: {cuerpo}
        
        TUS TAREAS:
        1. Clasifica en una categoría: [VENTAS 💰] / [ADMINISTRATIVO 📋] / [OBRA 🏗️] / [BASURA 🗑️].
        2. Resume el problema en 1 frase directa.
        3. Dime qué acción debo tomar yo (ej: "Reenviar a X", "Nada", "Responder urgente").
        4. Redacta un borrador de respuesta profesional. Si es una queja, sé empático pero firme. Si es venta, sé proactivo.
        """

        try:
            response = model.generate_content(prompt)
            
            # Usamos un color diferente según el éxito
            with st.expander(f"📩 {asunto}", expanded=True):
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Error analizando {asunto}: {e}")

else:
    st.caption("Bandeja limpia. Esperando archivos...")
