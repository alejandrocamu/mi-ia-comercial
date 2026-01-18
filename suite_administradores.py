import streamlit as st
def app():
    st.title("👥 Suite ADMINISTRADORES")
    if st.button("⬅️ Volver"): st.session_state.navegacion = "🏠 Inicio"; st.rerun()
    st.write("Módulo en construcción...")
