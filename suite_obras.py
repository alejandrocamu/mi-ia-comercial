import streamlit as st

def app():
    st.title("🚧 Gestión de Obras")
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()
    st.info("Aquí irá el semáforo de obras.")
