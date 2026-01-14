import streamlit as st
import extract_msg
from email import policy
from email.parser import BytesParser
import time
import datetime

# --- FUNCIONES AUXILIARES ---
def leer_eml(f):
    try:
        b = f.getvalue(); msg = BytesParser(policy=policy.default).parsebytes(b)
        c = msg.get_body(preferencelist=('plain'))
        if c: return msg['from'], msg['subject'], c.get_content()
        return msg['from'], msg['subject'], "HTML/Imagen"
    except: return "?", "Error", "Error"

# --- LISTA DE CLASIFICACIONES ---
CATEGORIAS = [
    "Ascensores PARADOS", 
    "Amenazas de BAJAS", 
    "IPOS Inspecciones de industria", 
    "DINAMIZACIONES y MODERNIZACIONES", 
    "SUSTITUCION de Ascensor", 
    "Validación de Partes de Trabajo PRs", 
    "DEUDA de clientes", 
    "Subidas de IPC", 
    "RENEGOCIACION de Contratos", 
    "FACTURACIÓN de Clientes", 
    "VENTA NUEVA", 
    "OTROS"
]

# --- APP PRINCIPAL DEL MÓDULO ---
def app(model):
    st.title("📮 Suite CORREO")
    
    # Botón Volver
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()
    
    # PESTAÑAS (Nombre actualizado)
    tab1, tab2 = st.tabs(["📤 Análisis de Bandeja de Entrada", "📅 Calendario de Correos"])

    # ---------------------------------------------------------
    # PESTAÑA 1: SUBIDA Y ANÁLISIS AUTOMÁTICO
    # ---------------------------------------------------------
    with tab1:
        st.header("Analizar Nuevos Correos (IA)")
        st.info("Sube tus archivos .msg o .eml. La IA los clasificará automáticamente.")

        with st.form("mail_form", clear_on_submit=True):
            uploaded_files = st.file_uploader("Arrastra archivos aquí", type=['msg', 'eml'], accept_multiple_files=True)
            submitted = st.form_submit_button("⚡ ANALIZAR Y GUARDAR")

        if submitted and uploaded_files:
            st.write("---")
            progress_bar = st.progress(0)
            status_text = st.empty()
            resultados_tanda = []

            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Analizando {i+1}/{len(uploaded_files)}...")
                
                # Lectura del archivo
                if uploaded_file.name.lower().endswith(".msg"):
                    try: m = extract_msg.Message(uploaded_file); rem=m.sender; asu=m.subject; cue=m.body
                    except: rem="?"; asu="Error"; cue=""
                else:
                    rem, asu, cue = leer_eml(uploaded_file)
                
                if cue and len(cue)>15000: cue=cue[:15000]

                # Prompt para la IA
                prompt = f"""
                Actúa como mi Asistente Comercial experto. Analiza este correo:
                DE: {rem} | ASUNTO: {asu} | MENSAJE: {cue}
                
                Genera un reporte con esta estructura:
                1. Clasificación: Elige UNA de: {CATEGORIAS}
                2. Resumen: 1 frase.
                3. Acción: Qué debo hacer.
                4. Respuesta: Borrador de respuesta.
                """
                
                try:
                    # Llamada a la IA
                    res = model.generate_content(prompt)
                    analisis_texto = res.text
                except Exception as e:
                    analisis_texto = f"⚠️ Error IA: {str(e)}"

                # Guardamos resultado
                resultados_tanda.append({
                    "asunto": asu,
                    "analisis": analisis_texto,
                    "origen": "🤖 IA", # Para saber que vino de la IA
                    "hora": datetime.datetime.now().strftime("%H:%M")
                })
                
                progress_bar.progress((i+1)/len(uploaded_files))
            
            # Guardar en memoria (session_state)
            hoy_str = str(datetime.date.today())
            if hoy_str in st.session_state.db_correos:
                st.session_state.db_correos[hoy_str].extend(resultados_tanda)
            else:
                st.session_state.db_correos[hoy_str] = resultados_tanda

            status_text.empty()
            st.success(f"✅ {len(resultados_tanda)} correos analizados y guardados en el Calendario.")

    # ---------------------------------------------------------
    # PESTAÑA 2: CALENDARIO Y GESTIÓN MANUAL
    # ---------------------------------------------------------
    with tab2:
        col_cal, col_gestion = st.columns([1, 2])
        
        with col_cal:
            st.subheader("📅 Fecha")
            fecha_selec = st.date_input("Selecciona día:", datetime.date.today())
            fecha_str = str(fecha_selec)
            
            st.divider()
            
            # BOTÓN ELIMINAR TODO
            if st.button("🗑️ Borrar Todo este Día", type="primary"):
                st.session_state.db_correos[fecha_str] = []
                st.rerun()

        with col_gestion:
            st.subheader(f"Tareas del {fecha_str}")
            
            # --- FORMULARIO DE CREACIÓN MANUAL (POP-UP) ---
            with st.expander("➕ AÑADIR NUEVA TAREA MANUAL", expanded=False):
                with st.form("manual_form", clear_on_submit=True):
                    st.write("**Nuevo Registro Manual**")
                    
                    # Campos solicitados
                    clasif = st.selectbox("Clasificación", CATEGORIAS)
                    asunto_man = st.text_input("Asunto / Cliente")
                    resumen_man = st.text_area("Resumen")
                    accion_man = st.text_area("Acción a realizar")
                    resp_man = st.text_area("Borrador de Respuesta")
                    
                    enviar_manual = st.form_submit_button("💾 Guardar Tarea")
                    
                    if enviar_manual:
                        # Creamos el formato de texto similar al de la IA para mantener consistencia
                        texto_generado = f"""
                        **1. Clasificación:** {clasif}
                        **2. Resumen:** {resumen_man}
                        **3. Acción:** {accion_man}
                        **4. Respuesta:**
                        ```text
                        {resp_man}
                        ```
                        """
                        
                        nuevo_registro = {
                            "asunto": asunto_man if asunto_man else "Sin Asunto",
                            "analisis": texto_generado,
                            "origen": "👤 Manual",
                            "hora": datetime.datetime.now().strftime("%H:%M")
                        }
                        
                        # Guardar
                        if fecha_str in st.session_state.db_correos:
                            st.session_state.db_correos[fecha_str].append(nuevo_registro)
                        else:
                            st.session_state.db_correos[fecha_str] = [nuevo_registro]
                        
                        st.success("Tarea guardada.")
                        st.rerun()

            # --- LISTADO DE TAREAS ---
            st.divider()
            if fecha_str in st.session_state.db_correos and st.session_state.db_correos[fecha_str]:
                tareas = st.session_state.db_correos[fecha_str]
                st.info(f"Tienes {len(tareas)} registros para hoy.")
                
                for i, tarea in enumerate(tareas):
                    # Icono según origen
                    icono = "🤖" if tarea.get('origen') == "🤖 IA" else "👤"
                    
                    with st.expander(f"{icono} {tarea['hora']} | {tarea['asunto']}"):
                        st.markdown(tarea['analisis'])
                        # Botón para borrar tarea individual (Opcional, pero útil)
                        if st.button("Borrar tarea", key=f"del_{fecha_str}_{i}"):
                            st.session_state.db_correos[fecha_str].pop(i)
                            st.rerun()
            else:
                st.caption("No hay registros para este día.")
