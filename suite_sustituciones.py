import streamlit as st

def app():
    st.title("🔧 Suite SUSTITUCIONES")
    
    # Botón de volver
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()

    st.info("🛠️ Aquí irá el panel de gestión de Sustituciones de Ascensores.")
    st.write("Próximamente: Semáforo de estado, cronograma y materiales.")
