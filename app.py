import streamlit as st
import extract_msg
import google.generativeai as genai
import email
from email import policy
from email.parser import BytesParser
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente Comercial",
    page_icon="🛡️",
    layout="wide"
)

# --- 2. GESTIÓN DE SECRETOS ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Falta configurar los secretos (API Key o Password).")
    st.stop()

# --- 3. LOGIN ---
with st.sidebar:
    st.title("Acceso Privado")
    input_pass = st.text_input("Introduce tu contraseña", type="password")
    
    if input_pass != PASSWORD_REAL:
        st.warning("🔒 El sistema está bloqueado.")
        st.stop()
    else:
        st.success("🔓 Acceso concedido")

# --- 4. CONFIGURACIÓN GEMINI ---
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 5. LÓGICA INTERNA ---
def leer_eml(uploaded_file):
    """Función para leer archivos .eml"""
    try:
        bytes_data = uploaded_file.getvalue()
        msg = BytesParser(policy=policy.default).parsebytes(bytes_data)
        
        asunto = msg['subject']
        remitente = msg['from']
        
        # Intentar sacar el texto plano
        cuerpo = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    cuerpo = part.get_content()
                    break # Encontramos texto, salimos
            # Si no hay texto plano, buscamos lo que haya
            if not cuerpo:
                 for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                         cuerpo = "Contenido HTML (resumido)" 
        else:
            cuerpo = msg.get_content()
            
        return remitente, asunto, cuerpo
    except Exception as e:
        return "Error", "Error", f"No se pudo leer el .eml: {str(e)}"

# --- 6. INTERFAZ ---
st.title("🛡️ El Filtro: Tu Asistente de Operaciones")
st.markdown("Arrastra tus correos **(.msg o .eml)**. La IA redactará la respuesta.")

# Aceptamos ambos formatos
uploaded_files = st.file_uploader(
    "Arrastra tus correos aquí", 
    type=['msg', 'eml'], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Procesando {len(uploaded_files)} correos...")
    
    for uploaded_file in uploaded_files:
        
        # DETECTAR SI ES MSG O EML
        nombre_archivo = uploaded_file.name.lower()
        
        if nombre_archivo.endswith(".msg"):
            # Lógica para .msg (Outlook antiguo)
            try:
                msg = extract_msg.Message(uploaded_file)
                asunto = msg.subject
                remitente = msg.sender
                cuerpo = msg.body
            except:
                asunto = "Error leyendo .msg"
                remitente = "Desc."
                cuerpo = "Error"
                
        elif nombre_archivo.endswith(".eml"):
            # Lógica para .eml (Outlook nuevo / Web)
            remitente, asunto, cuerpo = leer_eml(uploaded_file)
            
        else:
            continue # Si no es ninguno, saltamos

        # Limitar tamaño
        if cuerpo and len(cuerpo) > 5000: cuerpo = cuerpo[:5000]

        # --- CEREBRO: LLAMADA A GEMINI ---
        prompt = f"""
        Analiza este correo recibido por un comercial:
        
        REMITENTE: {remitente}
        ASUNTO: {asunto}
        CUERPO: {cuerpo}

        GENERA ESTA SALIDA:
        1. **Categoría**: [ADMINISTRATIVO, OBRA, VENTA, URGENTE, BASURA].
        2. **Resumen**: Qué pasa en 1 frase.
        3. **Acción**: Qué debo hacer yo.
        4. **Borrador de Respuesta**: Email profesional y amable listo para copiar.
        """
        
        try:
            response = model.generate_content(prompt)
            with st.expander(f"📩 {asunto}", expanded=True):
                st.markdown(response.text)
        except Exception as e:
            st.error(f"Error conectando con la IA: {e}")

else:
    st.info("Bandeja vacía. Sube archivos .eml o .msg")
