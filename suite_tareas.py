import streamlit as st
import datetime

FASES = ["Generada", "Contacto", "Espera", "Presupuesto", "Aceptado", "Finalizada"]

def app():
    st.title("📋 Suite TAREAS (Kanban)")
    
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()

    if "db_tareas" not in st.session_state: st.session_state.db_tareas = []

    # --- POPUP CREACIÓN ---
    if st.session_state.get("show_task_popup", False):
        with st.container(border=True):
            st.markdown("### ✨ Nueva Tarea")
            pre = st.session_state.get("new_task_data", {})
            with st.form("form_nueva_tarea"):
                c1, c2 = st.columns(2)
                tit = c1.text_input("Cliente / Título", value=pre.get("titulo", ""))
                prio = c1.selectbox("Prioridad", ["🔥 Alta", "⚠️ Media", "🧊 Baja"])
                fase = c2.selectbox("Fase Inicial", FASES)
                fecha = c2.date_input("Límite", datetime.date.today())
                desc = st.text_area("Detalles", value=pre.get("descripcion", ""))
                
                if st.form_submit_button("💾 Guardar"):
                    st.session_state.db_tareas.append({
                        "id": int(datetime.datetime.now().timestamp()),
                        "titulo": tit, "fase": fase, "prioridad": prio,
                        "fecha": str(fecha), "descripcion": desc
                    })
                    st.session_state.show_task_popup = False; st.session_state.new_task_data = {}; st.rerun()
                
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.show_task_popup = False; st.rerun()
        st.divider()
    else:
        if st.button("➕ Nueva Tarea Manual"):
            st.session_state.show_task_popup = True; st.session_state.new_task_data = {}; st.rerun()

    st.write("") 

    # --- KANBAN BOARD ---
    cols = st.columns(len(FASES))
    for i, fase in enumerate(FASES):
        with cols[i]:
            st.markdown(f"**{fase}**"); st.markdown("---")
            tareas = [t for t in st.session_state.db_tareas if t["fase"] == fase]
            
            for t in tareas:
                with st.container(border=True):
                    st.markdown(f"**{t['titulo']}**")
                    st.caption(f"{t['prioridad']} | {t['fecha']}")
                    with st.expander("Info"):
                        st.write(t['descripcion'])
                        if st.button("🗑️", key=f"d{t['id']}"): st.session_state.db_tareas.remove(t); st.rerun()
                    
                    c_izq, c_der = st.columns(2)
                    with c_izq:
                        if i > 0 and st.button("⬅️", key=f"l{t['id']}"): t["fase"] = FASES[i-1]; st.rerun()
                    with c_der:
                        if i < len(FASES)-1 and st.button("➡️", key=f"r{t['id']}"): t["fase"] = FASES[i+1]; st.rerun()
