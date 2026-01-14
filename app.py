import streamlit as st
import extract_msg
import google.generativeai as genai
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Asistente Comercial",
    page_icon="🛡️",
    layout="wide"
)

# --- 2. GESTIÓN DE SECRETOS (Contraseña y API Key) ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    PASSWORD_REAL = st.secrets["APP_PASSWORD"]
except:
    st.error("⚠️ Falta configurar los secretos (API Key o Password).")
    st.stop()

# --- 3. PANTALLA DE LOGIN ---
with st.sidebar:
    st.title("Acceso Privado")
    input_pass = st.text_input("Introduce tu contraseña", type="password")
    
    if input_pass != PASSWORD_REAL:
        st.warning("🔒 El sistema está bloqueado.")
        st.stop()
    else:
        st.success("🔓 Acceso concedido")

# --- 4. CONFIGURACIÓN DE GEMINI ---
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 5. INTERFAZ PRINCIPAL ---
st.title("🛡️ El Filtro: Tu Asistente de Operaciones")
st.markdown("Sube aquí los correos **(.msg)**. La IA redactará la respuesta.")

uploaded_files = st.file_uploader("Arrastra tus correos aquí", type=['msg'], accept_multiple_files=True)

if uploaded_files:
    st.info(f"Procesando {len(uploaded_files)} correos...")
    
    for uploaded_file in uploaded_files:
        try:
            msg = extract_msg.Message(uploaded_file)
            asunto = msg.subject
            remitente = msg.sender
            cuerpo = msg.body
            
            # Limitar tamaño texto si es gigante
            if cuerpo and len(cuerpo) > 5000: cuerpo = cuerpo[:5000]

            prompt = f"""
            Analiza este correo:
            REMITENTE: {remitente}
            ASUNTO: {asunto}
            CUERPO: {cuerpo}

            GENERA:
            1. **Categoría**: [ADMINISTRATIVO, OBRA, VENTA, URGENTE].
            2. **Resumen**: 1 frase.
            3. **Acción**: Qué debo hacer.
            4. **Borrador de Respuesta**: Email profesional listo para copiar.
            """
            
            response = model.generate_content(prompt)
            
            with st.expander(f"📩 {asunto}", expanded=True):
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Error en {uploaded_file.name}: {e}")
