import streamlit as st

def app():
    st.title("👥 Suite ADMINISTRADORES")
    
    # Botón de volver
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()

    st.info("📄 Aquí irá la gestión con Administradores de Fincas.")
    st.write("Próximamente: Redactor de contratos, historial de reuniones y CRM.")
