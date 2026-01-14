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
    "Ascensores PARADOS", "Amenazas de BAJAS", "IPOS Inspecciones", 
    "DINAMIZACIONES", "SUSTITUCION", "Partes de Trabajo", 
    "DEUDA", "IPC", "RENEGOCIACION", "FACTURACIÓN", "VENTA NUEVA", "OTROS"
]

def app(model):
    st.title("📮 Suite CORREO")
    
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()
    
    tab1, tab2 = st.tabs(["📤 Análisis de Bandeja de Entrada", "📅 Calendario de Correos"])

    # --- PESTAÑA 1: ANÁLISIS ---
    with tab1:
        st.header("Analizar Nuevos Correos (IA)")
        with st.form("mail_form", clear_on_submit=True):
            uploaded_files = st.file_uploader("Arrastra archivos .msg o .eml", type=['msg', 'eml'], accept_multiple_files=True)
            submitted = st.form_submit_button("⚡ ANALIZAR Y GUARDAR")

        if submitted and uploaded_files:
            progress_bar = st.progress(0)
            resultados_tanda = []

            for i, uploaded_file in enumerate(uploaded_files):
                # Lectura de archivo
                if uploaded_file.name.lower().endswith(".msg"):
                    try: m = extract_msg.Message(uploaded_file); rem=m.sender; asu=m.subject; cue=m.body
                    except: rem="?"; asu="Error"; cue=""
                else:
                    rem, asu, cue = leer_eml(uploaded_file)
                if cue and len(cue)>15000: cue=cue[:15000]

                # IA
                prompt = f"""
                Analiza: DE: {rem} | ASUNTO: {asu} | MENSAJE: {cue}
                Reporte: 1. Clasificación ({CATEGORIAS}), 2. Resumen, 3. Acción, 4. Respuesta.
                """
                try: res = model.generate_content(prompt); analisis_texto = res.text
                except Exception as e: analisis_texto = f"Error IA: {e}"

                resultados_tanda.append({
                    "asunto": asu, "analisis": analisis_texto, "origen": "🤖 IA", 
                    "hora": datetime.datetime.now().strftime("%H:%M")
                })
                progress_bar.progress((i+1)/len(uploaded_files))
            
            hoy_str = str(datetime.date.today())
            if hoy_str in st.session_state.db_correos: st.session_state.db_correos[hoy_str].extend(resultados_tanda)
            else: st.session_state.db_correos[hoy_str] = resultados_tanda
            st.success(f"✅ {len(resultados_tanda)} correos guardados.")

    # --- PESTAÑA 2: CALENDARIO ---
    with tab2:
        col_cal, col_gestion = st.columns([1, 2.5])
        
        with col_cal:
            fecha_selec = st.date_input("Día:", datetime.date.today())
            fecha_str = str(fecha_selec)
            st.write("") # Espacio
            if st.button("🗑️ Borrar Todo el Día", type="primary"):
                st.session_state.db_correos[fecha_str] = []; st.rerun()

        with col_gestion:
            # --- CABECERA CON BOTÓN PEQUEÑO A LA DERECHA ---
            c_titulo, c_boton = st.columns([3, 1])
            with c_titulo:
                st.subheader(f"Correos del {fecha_str}")
            with c_boton:
                # Usamos popover para que sea un menú desplegable pequeño y limpio
                with st.popover("➕ Crear Manual", use_container_width=True):
                    st.markdown("### Nuevo Correo")
                    with st.form("manual_complete"):
                        # REQUISITO 1: CAMPOS COMPLETOS RESTAURADOS
                        clasif = st.selectbox("Clasificación", CATEGORIAS)
                        asunto = st.text_input("Asunto / Cliente")
                        resumen = st.text_area("Resumen")
                        accion = st.text_area("Acción a realizar")
                        respuesta = st.text_area("Borrador Respuesta")
                        
                        if st.form_submit_button("💾 Guardar"):
                            texto_generado = f"""
                            **1. Clasificación:** {clasif}
                            **2. Resumen:** {resumen}
                            **3. Acción:** {accion}
                            **4. Respuesta:**
                            ```text
                            {respuesta}
                            ```
                            """
                            nuevo = {"asunto": asunto, "analisis": texto_generado, "origen": "👤 Manual", "hora": datetime.datetime.now().strftime("%H:%M")}
                            
                            if fecha_str not in st.session_state.db_correos: st.session_state.db_correos[fecha_str] = []
                            st.session_state.db_correos[fecha_str].append(nuevo)
                            st.rerun()

            st.divider()

            # --- LISTADO ---
            if fecha_str in st.session_state.db_correos and st.session_state.db_correos[fecha_str]:
                lista = st.session_state.db_correos[fecha_str]
                for i, correo in enumerate(lista):
                    icono = "🤖" if correo.get('origen') == "🤖 IA" else "👤"
                    with st.expander(f"{icono} {correo['hora']} | {correo['asunto']}"):
                        st.markdown(correo['analisis'])
                        c1, c2 = st.columns(2)
                        if c1.button("🗑️ Borrar correo", key=f"del_{i}"):
                            st.session_state.db_correos[fecha_str].pop(i); st.rerun()
                        
                        if c2.button("✅ Generar tarea", key=f"gen_{i}"):
                            st.session_state.new_task_data = {"titulo": correo['asunto'], "descripcion": correo['analisis']}
                            st.session_state.show_task_popup = True
                            st.session_state.navegacion = "📋 Suite TAREAS" 
                            st.rerun()
            else:
                st.caption("No hay correos registrados hoy.")
