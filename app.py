import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="Diagnóstico", page_icon="🕵️")

st.title("🕵️ Diagnóstico de Modelos Google")

# 1. Intentamos leer la clave
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    st.success("✅ API Key encontrada y configurada.")
except Exception as e:
    st.error(f"❌ Error con la API Key: {e}")
    st.stop()

# 2. Preguntamos a Google la lista
st.write("---")
st.write("📡 Conectando con Google para ver tus modelos disponibles...")

try:
    # Esta es la función que pedía el error: list_models
    lista_modelos = []
    
    for m in genai.list_models():
        # Solo queremos ver los modelos que sirven para generar texto (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            lista_modelos.append(m.name)

    if lista_modelos:
        st.success(f"¡Éxito! Tienes acceso a {len(lista_modelos)} modelos:")
        # Mostramos la lista en un cuadro de código para que la leas bien
        st.code("\n".join(lista_modelos))
        
        st.info("👇 Copia uno de los nombres de arriba (ej: models/gemini-pro) y dímelo.")
    else:
        st.warning("⚠️ La conexión funciona, pero Google dice que no tienes modelos disponibles. Verifica tu API Key.")

except Exception as e:
    st.error(f"❌ Error fatal al pedir la lista: {e}")
    st.write("Posibles causas: API Key incorrecta o bloqueo regional.")
