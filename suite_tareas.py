import streamlit as st
import datetime

# --- CONFIGURACIÓN DEL PIPELINE ---
FASES = [
    "1. Tarea Generada",
    "2. Contacto Cliente",
    "3. Espera de Respuesta",
    "4. Presupuesto Realizado",
    "5. Presupuesto Aceptado",
    "6. Tarea Finalizada"
]

def app():
    st.title("📋 Suite TAREAS")
    
    # Botón Volver
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()

    # --- GESTIÓN DE ESTADO ---
    if "db_tareas" not in st.session_state:
        st.session_state.db_tareas = []

    # --- LÓGICA DEL POP-UP (FORMULARIO DE CREACIÓN) ---
    # Este bloque se activa si le das al botón manual O si vienes del Correo
    if st.session_state.get("show_task_popup", False):
        with st.container(border=True):
            st.markdown("### ✨ Nueva Tarea")
            
            # Recuperamos datos pre-cargados (si vienen del correo)
            pre_datos = st.session_state.get("new_task_data", {})
            
            with st.form("form_nueva_tarea"):
                col1, col2 = st.columns(2)
                with col1:
                    titulo = st.text_input("Título / Cliente", value=pre_datos.get("titulo", ""))
                    prioridad = st.selectbox("Prioridad", ["Alta 🔥", "Media ⚠️", "Baja 🧊"])
                with col2:
                    fase = st.selectbox("Fase Inicial", FASES)
                    fecha = st.date_input("Fecha Límite", datetime.date.today())
                
                descripcion = st.text_area("Descripción / Detalles", value=pre_datos.get("descripcion", ""))
                
                # Botonera del formulario
                c_guardar, c_cancelar = st.columns([1, 1])
                with c_guardar:
                    submitted = st.form_submit_button("💾 Guardar Tarea", type="primary")
                with c_cancelar:
                    cancelado = st.form_submit_button("❌ Cancelar")

                if submitted:
                    nueva_tarea = {
                        "id": len(st.session_state.db_tareas) + 1,
                        "titulo": titulo,
                        "fase": fase,
                        "prioridad": prioridad,
                        "fecha": str(fecha),
                        "descripcion": descripcion,
                        "creado_el": str(datetime.date.today())
                    }
                    st.session_state.db_tareas.append(nueva_tarea)
                    # Limpiamos el estado del popup
                    st.session_state.show_task_popup = False
                    st.session_state.new_task_data = {} # Limpiar datos temporales
                    st.success("Tarea creada correctamente.")
                    st.rerun()
                
                if cancelado:
                    st.session_state.show_task_popup = False
                    st.session_state.new_task_data = {}
                    st.rerun()
        st.divider()

    # --- BOTÓN MANUAL PARA ABRIR EL POP-UP ---
    if not st.session_state.get("show_task_popup", False):
        if st.button("➕ Nueva Tarea Manual"):
            st.session_state.show_task_popup = True
            st.session_state.new_task_data = {} # Vacío porque es manual
            st.rerun()

    # --- VISUALIZACIÓN DEL PIPELINE (KANBAN SIMPLIFICADO) ---
    st.subheader("Pipeline de Trabajo")
    
    # Creamos pestañas para las fases (es más limpio que 6 columnas estrechas)
    tabs = st.tabs([f.split(". ")[1] for f in FASES]) # Quitamos el número para el nombre del tab

    for i, tab in enumerate(tabs):
        fase_actual = FASES[i]
        
        with tab:
            # Filtramos tareas de esta fase
            tareas_fase = [t for t in st.session_state.db_tareas if t["fase"] == fase_actual]
            
            if not tareas_fase:
                st.caption("No hay tareas en esta fase.")
            
            for tarea in tareas_fase:
                with st.expander(f"{tarea['prioridad']} | {tarea['titulo']}"):
                    st.write(f"**Descripción:** {tarea['descripcion']}")
                    st.write(f"📅 **Límite:** {tarea['fecha']}")
                    
                    st.divider()
                    
                    # MOVER DE FASE
                    c1, c2 = st.columns(2)
                    with c1:
                        # Botón para avanzar fase
                        if i < len(FASES) - 1:
                            if st.button(f"➡️ Avanzar a {FASES[i+1].split('. ')[1]}", key=f"av_{tarea['id']}"):
                                tarea["fase"] = FASES[i+1]
                                st.rerun()
                    with c2:
                         # Botón para borrar
                        if st.button("🗑️ Eliminar", key=f"del_t_{tarea['id']}"):
                            st.session_state.db_tareas.remove(tarea)
                            st.rerun()
