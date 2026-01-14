import streamlit as st
import extract_msg
import google.generativeai as genai
import email
from email import policy
from email.parser import BytesParser
import time
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(
    page_title="Asistente Comercial",
    page_icon="🛡️",
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

# --- 4. CONFIGURACIÓN DEL MOTOR ---
genai.configure(api_key=API_KEY)

# Usamos gemini-1.5-flash que es la versión estable y gratuita
MODEL_NAME = 'gemini-1.5-flash' 
model = genai.GenerativeModel(MODEL_NAME)

st.sidebar.info(f"✅ Motor activo: {MODEL_NAME}")

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
        if html_part:
            return remitente, asunto, "Contenido HTML (imágenes/formato complejo)."
            
        return remitente, asunto, "Sin contenido texto"
    except:
        return "Desconocido", "Error lectura", "No se pudo leer el archivo"

# --- 6. INTERFAZ ---
st.title("🛡️ El Filtro: Tu Asistente de Operaciones")
st.markdown("Arrastra tus correos **(.eml o .msg)**.")

uploaded_files = st.file_uploader("Zona de carga", type=['msg', 'eml'], accept_multiple_files=True)

if uploaded_files:
    st.info(f"Analizando {len(uploaded_files)} correos...")
    
    # Barra de progreso
    progress_bar = st.progress(0)
    
    for i, uploaded_file in enumerate(uploaded_files):
        # 1. Leer archivo
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

        # 2. Recortar texto para no saturar
        if cuerpo and len(cuerpo) > 20000: cuerpo = cuerpo[:20000]

        # 3. Prompt (Instrucciones para la IA)
        # NOTA: Asegúrate de copiar las tres comillas del final """
        prompt = f"""
        Actúa como mi asistente comercial personal.
        He recibido este correo. Analízalo:
        
        - DE: {remitente}
        - ASUNTO: {asunto}
        - MENSAJE: {cuerpo}
        
        GENERA UN REPORTE EN MARKDOWN:
        1. **CLASIFICACIÓN**: Elige UNA [VENTA 💰 / TRÁMITE 📄 / OBRA 🏗️ / BASURA 🗑️].
        2. **RESUMEN**: ¿Qué pasa? (Máximo 15 palabras).
        3. **ACCIÓN RECOMENDADA**: ¿Qué tengo que hacer yo?
        4. **BORRADOR DE RESPUESTA**: Escribe el email de respuesta ideal.
        """

        try:
            # Pausa de seguridad
            time.sleep(2) 
            
            response = model.generate_content(prompt)
            
            with st.expander(f"📩 {asunto}", expanded=True):
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Error con '{asunto}': {e}")
            if "429" in str(e):
                st.warning("⏳ Límite de velocidad. Espera un poco.")
        
        # Actualizar barra
        progress_bar.progress((i + 1) / len(uploaded_files))

else:
    st.caption("Bandeja limpia. Esperando archivos...")
