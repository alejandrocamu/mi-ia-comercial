import streamlit as st

def app():
    st.title("📄 Redactor de Contratos")
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()
    st.info("Aquí irán los generadores de PDF.")
