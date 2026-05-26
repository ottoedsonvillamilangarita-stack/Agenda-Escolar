import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_notas_curso
from modulos.features.asistencia import mostrar_asistencia_director

def mostrar(data):
    st.title("🧭 Director de Grupo")
    
    documento_docente = data.get('documento')
    st.write(f"Bienvenido, {data.get('username', 'Director')}")
    
    headers = get_headers()
    
    # Buscar curso que dirige
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=eq.Dirección de Curso"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar la información")
        return
    
    direccion = response.json()
    
    if not direccion:
        st.warning("No eres director de ningún curso")
        return
    
    curso_dirige = direccion[0].get('curso')
    st.success(f"🎓 Director del curso: **{curso_dirige}**")
    
    # Pestañas
    tab1, tab2, tab3 = st.tabs(["📋 Estudiantes", "📖 Notas del Curso", "📋 Asistencia"])
    
    with tab1:
        st.subheader(f"📋 Estudiantes del Curso {curso_dirige}")
        
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso_dirige}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code == 200:
            estudiantes = response_est.json()
            if estudiantes:
                df = pd.DataFrame(estudiantes)
                st.dataframe(df[['nombre_estudiante', 'documento_estudiante']], use_container_width=True)
                st.caption(f"Total: {len(estudiantes)} estudiantes")
            else:
                st.info("No hay estudiantes")
    
    with tab2:
        mostrar_notas_curso(data)
    
    with tab3:
        mostrar_asistencia_director(data)
    
    with tab4:
        st.info("🚧 Módulo en desarrollo")

def mostrar_asistencia_docente_para_director(data, curso_fijo):
    """Versión para director - solo marca asistencia en su curso"""
    st.subheader(f"📋 Marcar Asistencia - Curso {curso_fijo}")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    fecha = st.date_input("Fecha", datetime.now())
    
    # Obtener estudiantes del curso específico
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso_fijo}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudiantes:
        st.warning(f"No hay estudiantes en el curso {curso_fijo}")
        return
    
    # Obtener asistencias existentes
    asistencias_existentes = {}
    url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso_fijo}&fecha=eq.{fecha}"
    response_asist = requests.get(url_asist, headers=headers)
    
    if response_asist.status_code == 200:
        for a in response_asist.json():
            asistencias_existentes[a.get('documento_estudiante')] = a
    
    st.markdown(f"**{curso_fijo} - {fecha.strftime('%d/%m/%Y')}**")
    st.markdown("---")
    
    # Formulario
    with st.form(key=f"form_asistencia_director_{curso_fijo}_{fecha}"):
        # Cabecera
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 2])
        with col1:
            st.markdown("**Estudiante**")
        with col2:
            st.markdown("**Estado**")
        with col3:
            st.markdown("**Retardo**")
        with col4:
            st.markdown("**Uniforme**")
        with col5:
            st.markdown("**Justif.**")
        with col6:
            st.markdown("**Observación**")
        st.markdown("---")
        
        datos_asistencia = []
        
        for idx, estudiante in enumerate(estudiantes):
            doc = estudiante.get('documento_estudiante')
            nombre = estudiante.get('nombre_estudiante')[:25]
            existente = asistencias_existentes.get(doc, {})
            
            estado_actual = existente.get('estado', "Presente")
            retardo_actual = existente.get('retardo', False)
            uniforme_actual = existente.get('uniforme_malo', False)
            justificado_actual = existente.get('justificado', False)
            observaciones_actual = existente.get('observaciones', "")
            
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 2])
            
            with col1:
                st.write(f"**{nombre}**")
            with col2:
                estado = st.selectbox(
                    "",
                    ["Presente", "Ausente"],
                    index=["Presente", "Ausente"].index(estado_actual),
                    key=f"estado_dir_{idx}_{doc}",
                    label_visibility="collapsed"
                )
            with col3:
                if estado == "Presente":
                    retardo = st.checkbox("", value=retardo_actual, key=f"retardo_dir_{idx}_{doc}")
                else:
                    retardo = False
                    st.write("—")
            with col4:
                uniforme = st.checkbox("", value=uniforme_actual, key=f"uniforme_dir_{idx}_{doc}")
            with col5:
                if estado == "Ausente" or retardo:
                    justificado = st.checkbox("", value=justificado_actual, key=f"justificado_dir_{idx}_{doc}")
                else:
                    justificado = False
                    st.write("—")
            with col6:
                observaciones = st.text_input("", value=observaciones_actual, key=f"obs_dir_{idx}_{doc}",
                                             label_visibility="collapsed", placeholder="Observación...")
            
            datos_asistencia.append({
                "documento_estudiante": doc,
                "curso": curso_fijo,
                "fecha": str(fecha),
                "estado": estado,
                "retardo": retardo if estado == "Presente" else False,
                "uniforme_malo": uniforme,
                "justificado": justificado if (estado == "Ausente" or retardo) else False,
                "observaciones": observaciones,
                "documento_docente": documento_docente
            })
            
            st.markdown("---")
        
        submitted = st.form_submit_button("💾 Guardar Asistencia", type="primary", use_container_width=True)
        
        if submitted:
            guardados = 0
            for registro in datos_asistencia:
                check_url = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{registro['documento_estudiante']}&fecha=eq.{registro['fecha']}"
                check = requests.get(check_url, headers=headers)
                
                if check.status_code == 200 and check.json():
                    id_asist = check.json()[0].get('id')
                    requests.patch(f"{SUPABASE_URL}/rest/v1/asistencia?id=eq.{id_asist}", 
                                  headers=headers, json={
                                      "estado": registro['estado'],
                                      "retardo": registro['retardo'],
                                      "uniforme_malo": registro['uniforme_malo'],
                                      "justificado": registro['justificado'],
                                      "observaciones": registro['observaciones']
                                  })
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/asistencia", headers=headers, json=registro)
                guardados += 1
            
            st.success(f"✅ Asistencia guardada para {guardados} estudiantes")
            st.balloons()
    
    # Botón para volver
    if st.button("🔙 Volver al Reporte", use_container_width=True):
        st.rerun()
