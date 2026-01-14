import streamlit as st
import extract_msg
from email import policy
from email.parser import BytesParser
import time
import datetime

# Función auxiliar para leer EML (Local para este archivo)
def leer_eml(f):
    try:
        b = f.getvalue(); msg = BytesParser(policy=policy.default).parsebytes(b)
        c = msg.get_body(preferencelist=('plain'))
        if c: return msg['from'], msg['subject'], c.get_content()
        return msg['from'], msg['subject'], "HTML/Imagen"
    except: return "?", "Error", "Error"

# --- ESTA ES LA FUNCIÓN PRINCIPAL QUE LLAMARÁ APP.PY ---
def app(model):
    st.title("📮 Suite CORREO")
    
    # Botón para volver (Usamos el estado de session del archivo principal)
    if st.button("⬅️ Volver al Inicio"): 
        st.session_state.navegacion = "🏠 Inicio"
        st.rerun()
    
    tab1, tab2 = st.tabs(["📤 Análisis de Bandeja de Entrada", "📅 Tareas Diarias (Calendario)"])

    # --- PESTAÑA 1: SUBIDA ---
    with tab1:
        st.header("Analizar Nuevos Correos")
        st.info("Sube tus archivos .msg o .eml.")

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
                
                # Leer archivo
                if uploaded_file.name.lower().endswith(".msg"):
                    try: m = extract_msg.Message(uploaded_file); rem=m.sender; asu=m.subject; cue=m.body
                    except: rem="?"; asu="Error"; cue=""
                else:
                    rem, asu, cue = leer_eml(uploaded_file)
                
                if cue and len(cue)>15000: cue=cue[:15000]

                # PROMPT
                prompt = f"""
                Actúa como mi Asistente Comercial experto. Analiza este correo:
                DE: {rem} | ASUNTO: {asu} | MENSAJE: {cue}
                
                Genera un reporte OBLIGATORIAMENTE con esta estructura exacta:

                1. **Clasificación**: Elige UNA categoría exacta: 
                [Ascensores PARADOS, Amenazas de BAJAS, IPOS Inspecciones, DINAMIZACIONES, SUSTITUCION, Partes de Trabajo, DEUDA, IPC, RENEGOCIACION, FACTURACIÓN, VENTA NUEVA, OTROS].
                
                2. **Resumen**: 1 frase.
                3. **Accion**: Qué debo hacer.
                4. **Respuesta**:
                ```text
                Hola...
                ```
                """
                
                try:
                    time.sleep(1)
                    res = model.generate_content(prompt)
                    
                    resultados_tanda.append({
                        "asunto": asu,
                        "analisis": res.text,
                        "hora": datetime.datetime.now().strftime("%H:%M")
                    })
                except Exception as e:
                    st.error(f"Error: {e}")
                
                progress_bar.progress((i+1)/len(uploaded_files))
            
            # Guardar en memoria
            hoy_str = str(datetime.date.today())
            if hoy_str in st.session_state.db_correos:
                st.session_state.db_correos[hoy_str].extend(resultados_tanda)
            else:
                st.session_state.db_correos[hoy_str] = resultados_tanda

            status_text.empty()
            st.success("✅ Análisis guardado en Tareas Diarias.")

    # --- PESTAÑA 2: CALENDARIO ---
    with tab2:
        st.header("📅 Tareas Diarias")
        col_cal, col_info = st.columns([1, 3])
        with col_cal:
            fecha_selec = st.date_input("Selecciona día:", datetime.date.today())
            fecha_str = str(fecha_selec)
        
        with col_info:
            if fecha_str in st.session_state.db_correos:
                tareas = st.session_state.db_correos[fecha_str]
                st.markdown(f"### {fecha_str} ({len(tareas)} correos)")
                for tarea in tareas:
                    with st.expander(f"🕒 {tarea['hora']} | {tarea['asunto']}", expanded=False):
                        st.markdown(tarea['analisis'])
            else:
                st.warning(f"Sin registros el {fecha_str}")
