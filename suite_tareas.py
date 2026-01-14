import streamlit as st
import datetime

# --- CONFIGURACIÓN DEL PIPELINE ---
# Definimos las fases en una lista ordenada
FASES = [
    "Generada",
    "Contacto",
    "Espera",
    "Presupuesto",
    "Aceptado",
    "Finalizada"
]

def app():
    st.title("📋 Suite TAREAS (Kanban)")
    
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()

    # Inicializar memoria de tareas
    if "db_tareas" not in st.session_state: st.session_state.db_tareas = []

    # --- POP-UP DE CREACIÓN DE TAREA (Se activa manualmente o desde correo) ---
    if st.session_state.get("show_task_popup", False):
        with st.container(border=True):
            st.markdown("### ✨ Nueva Tarea")
            pre_datos = st.session_state.get("new_task_data", {})
            
            with st.form("form_nueva_tarea"):
                c1, c2 = st.columns(2)
                titulo = c1.text_input("Cliente / Título", value=pre_datos.get("titulo", ""))
                prioridad = c1.selectbox("Prioridad", ["🔥 Alta", "⚠️ Media", "🧊 Baja"])
                fase = c2.selectbox("Fase Inicial", FASES)
                fecha = c2.date_input("Límite", datetime.date.today())
                desc = st.text_area("Detalles", value=pre_datos.get("descripcion", ""))
                
                guardar = st.form_submit_button("💾 Crear Tarea", type="primary")
                cancelar = st.form_submit_button("❌ Cancelar")

                if guardar:
                    nueva = {
                        "id": int(datetime.datetime.now().timestamp()), # ID único basado en tiempo
                        "titulo": titulo, "fase": fase, "prioridad": prioridad,
                        "fecha": str(fecha), "descripcion": desc
                    }
                    st.session_state.db_tareas.append(nueva)
                    st.session_state.show_task_popup = False
                    st.session_state.new_task_data = {}
                    st.rerun()
                
                if cancelar:
                    st.session_state.show_task_popup = False
                    st.rerun()
        st.divider()
    else:
        # Botón normal para abrir el formulario
        if st.button("➕ Nueva Tarea Manual"):
            st.session_state.show_task_popup = True
            st.session_state.new_task_data = {}
            st.rerun()

    st.write("") # Espacio

    # --- TABLERO KANBAN (6 COLUMNAS) ---
    # Creamos las 6 columnas visuales
    cols = st.columns(len(FASES))

    # Iteramos por cada fase para pintar su columna
    for i, fase_nombre in enumerate(FASES):
        with cols[i]:
            # Cabecera de la columna
            st.markdown(f"**{fase_nombre}**")
            st.markdown("---")
            
            # Filtramos las tareas que están en ESTA fase
            tareas_en_fase = [t for t in st.session_state.db_tareas if t["fase"] == fase_nombre]
            
            # Pintamos cada tarea como una tarjeta
            for tarea in tareas_en_fase:
                with st.container(border=True):
                    # Título y Prioridad
                    st.markdown(f"**{tarea['titulo']}**")
                    st.caption(f"{tarea['prioridad']} | 📅 {tarea['fecha']}")
                    
                    # Descripción colapsable para ahorrar espacio
                    with st.expander("Ver info"):
                        st.caption(tarea['descripcion'])
                        if st.button("🗑️", key=f"del_{tarea['id']}"):
                            st.session_state.db_tareas.remove(tarea)
                            st.rerun()
                    
                    # --- BOTONES DE MOVIMIENTO (FLECHAS) ---
                    c_izq, c_der = st.columns(2)
                    
                    # Botón Mover Izquierda (si no es la primera fase)
                    with c_izq:
                        if i > 0:
                            if st.button("⬅️", key=f"prev_{tarea['id']}"):
                                tarea["fase"] = FASES[i-1]
                                st.rerun()
                    
                    # Botón Mover Derecha (si no es la última fase)
                    with c_der:
                        if i < len(FASES) - 1:
                            if st.button("➡️", key=f"next_{tarea['id']}"):
                                tarea["fase"] = FASES[i+1]
                                st.rerun()
