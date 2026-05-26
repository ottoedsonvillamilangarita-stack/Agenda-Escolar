import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

# ============================================
# FUNCIÓN UNIFICADA DE REPORTE
# ============================================

def mostrar_reporte_asistencia(curso, fecha_inicio, fecha_fin, headers, titulo="Reporte de Asistencia"):
    """Función ÚNICA para generar reportes de asistencia"""
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return None
    
    estudiantes = response_est.json()
    
    if not estudiantes:
        st.info("No hay estudiantes en este curso")
        return None
    
    st.markdown(f"**{titulo}**")
    st.markdown("---")
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 2])
    with col1:
        st.markdown("**Estudiante**")
    with col2:
        st.markdown("**Presentes**")
    with col3:
        st.markdown("**Ausentes**")
    with col4:
        st.markdown("**Aus. Justif.**")
    with col5:
        st.markdown("**Retardos**")
    with col6:
        st.markdown("**Uniforme**")
    with col7:
        st.markdown("**Observaciones**")
    st.markdown("---")
    
    reporte = []
    for estudiante in estudiantes:
        doc = estudiante.get('documento_estudiante')
        nombre = estudiante.get('nombre_estudiante')
        
        url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{doc}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
        response_asist = requests.get(url_asist, headers=headers)
        
        presentes = 0
        ausentes_total = 0
        ausentes_justificados = 0
        retardos_total = 0
        uniforme_malo = 0
        observaciones_lista = []
        
        if response_asist.status_code == 200:
            asistencias = response_asist.json()
            for a in asistencias:
                estado = a.get('estado', '')
                if estado == 'Presente':
                    presentes += 1
                elif estado == 'Ausente':
                    ausentes_total += 1
                    if a.get('justificado') == True:
                        ausentes_justificados += 1
                
                if a.get('retardo') == True:
                    retardos_total += 1
                if a.get('uniforme_malo') == True:
                    uniforme_malo += 1
                
                obs = a.get('observaciones', '')
                if obs and obs.strip():
                    observaciones_lista.append(obs)
        
        ausentes_no_justificados = ausentes_total - ausentes_justificados
        total_dias = presentes + ausentes_total
        porcentaje = (presentes / total_dias * 100) if total_dias > 0 else 0
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1, 1, 1, 1, 1, 2])
        with col1:
            st.write(f"**{nombre[:25]}**")
        with col2:
            st.write(f"{presentes}")
        with col3:
            st.write(f"{ausentes_total}")
        with col4:
            st.write(f"{ausentes_justificados}")
        with col5:
            st.write(f"{retardos_total}")
        with col6:
            st.write(f"{uniforme_malo}")
        with col7:
            if observaciones_lista:
                st.write(f"📝 {len(observaciones_lista)} obs")
            else:
                st.write("—")
        
        reporte.append({
            "Estudiante": nombre,
            "Presentes": presentes,
            "Ausentes": ausentes_total,
            "Aus. Justif.": ausentes_justificados,
            "Aus. No Justif.": ausentes_no_justificados,
            "Retardos": retardos_total,
            "Uniforme mal": uniforme_malo,
            "% Asist.": f"{porcentaje:.0f}%"
        })
    
    st.markdown("---")
    
    df = pd.DataFrame(reporte)
    
    st.subheader("🚨 Alertas")
    df_ausencias = df[df['Aus. No Justif.'] > 3]
    if not df_ausencias.empty:
        st.error("📌 ESTUDIANTES CON MÁS DE 3 AUSENCIAS SIN JUSTIFICAR:")
        for _, row in df_ausencias.iterrows():
            st.write(f"• {row['Estudiante']}: {row['Aus. No Justif.']}")
    
    df_retardos = df[df['Retardos'] > 5]
    if not df_retardos.empty:
        st.warning("⏰ ESTUDIANTES CON MÁS DE 5 RETARDOS:")
        for _, row in df_retardos.iterrows():
            st.write(f"• {row['Estudiante']}: {row['Retardos']}")
    
    df_uniforme = df[df['Uniforme mal'] > 3]
    if not df_uniforme.empty:
        st.info("🎽 ESTUDIANTES CON PROBLEMAS DE UNIFORME:")
        for _, row in df_uniforme.iterrows():
            st.write(f"• {row['Estudiante']}: {row['Uniforme mal']}")
    
    if df_ausencias.empty and df_retardos.empty and df_uniforme.empty:
        st.success("✅ No hay estudiantes con alertas")
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar reporte", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")
    
    return df


# ============================================
# DOCENTE - MARCAR ASISTENCIA
# ============================================

def mostrar_asistencia_docente(data):
    st.subheader("📋 Marcar Asistencia")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar cursos")
        return
    
    asignaciones = response.json()
    cursos_unicos = list(set([a.get('curso') for a in asignaciones if a.get('curso')]))
    
    if not cursos_unicos:
        st.warning("No tienes cursos asignados")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        curso = st.selectbox("Curso", cursos_unicos)
    with col2:
        fecha = st.date_input("Fecha", datetime.now())
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudantes:
        st.warning(f"No hay estudiantes en el curso {curso}")
        return
    
    asistencias_existentes = {}
    url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=eq.{fecha}"
    response_asist = requests.get(url_asist, headers=headers)
    
    if response_asist.status_code == 200:
        for a in response_asist.json():
            asistencias_existentes[a.get('documento_estudiante')] = a
    
    st.markdown(f"**{curso} - {fecha.strftime('%d/%m/%Y')}**")
    st.markdown("---")
    
    with st.form(key=f"form_asistencia_{curso}_{fecha}"):
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
                    key=f"estado_{idx}_{doc}",
                    label_visibility="collapsed"
                )
            with col3:
                if estado == "Presente":
                    retardo = st.checkbox("", value=retardo_actual, key=f"retardo_{idx}_{doc}")
                else:
                    retardo = False
                    st.write("—")
            with col4:
                uniforme = st.checkbox("", value=uniforme_actual, key=f"uniforme_{idx}_{doc}")
            with col5:
                if estado == "Ausente" or retardo:
                    justificado = st.checkbox("", value=justificado_actual, key=f"justificado_{idx}_{doc}")
                else:
                    justificado = False
                    st.write("—")
            with col6:
                observaciones = st.text_input("", value=observaciones_actual, key=f"obs_{idx}_{doc}",
                                             label_visibility="collapsed", placeholder="Observación...")
            
            datos_asistencia.append({
                "documento_estudiante": doc,
                "curso": curso,
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


# ============================================
# DIRECTOR - MARCAR ASISTENCIA (solo su curso)
# ============================================

def mostrar_asistencia_docente_para_director(data, curso_fijo):
    """Versión para director - solo marca asistencia en su curso"""
    st.subheader(f"📋 Marcar Asistencia - Curso {curso_fijo}")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    fecha = st.date_input("Fecha", datetime.now())
    
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso_fijo}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudiantes:
        st.warning(f"No hay estudiantes en el curso {curso_fijo}")
        return
    
    asistencias_existentes = {}
    url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso_fijo}&fecha=eq.{fecha}"
    response_asist = requests.get(url_asist, headers=headers)
    
    if response_asist.status_code == 200:
        for a in response_asist.json():
            asistencias_existentes[a.get('documento_estudiante')] = a
    
    st.markdown(f"**{curso_fijo} - {fecha.strftime('%d/%m/%Y')}**")
    st.markdown("---")
    
    with st.form(key=f"form_asistencia_director_{curso_fijo}_{fecha}"):
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
    
    if st.button("🔙 Volver al Reporte", use_container_width=True):
        st.rerun()


# ============================================
# DIRECTOR - REPORTE DE ASISTENCIA
# ============================================

def mostrar_asistencia_director(data):
    st.subheader("📋 Asistencia del Curso")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # Obtener curso que dirige
    url_dir = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=eq.Dirección de Curso"
    response_dir = requests.get(url_dir, headers=headers)
    
    if response_dir.status_code != 200 or not response_dir.json():
        st.warning("No eres director de ningún curso")
        return
    
    curso = response_dir.json()[0].get('curso')
    st.success(f"📌 Director del curso: **{curso}**")
    
    # ============================================
    # MARCAR ASISTENCIA (dentro de la misma función)
    # ============================================
    with st.expander("📋 Marcar Asistencia", expanded=False):
        fecha = st.date_input("Fecha", datetime.now())
        
        # Obtener estudiantes del curso
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code == 200:
            estudiantes = response_est.json()
            
            if estudiantes:
                # Obtener asistencias existentes
                asistencias_existentes = {}
                url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=eq.{fecha}"
                response_asist = requests.get(url_asist, headers=headers)
                
                if response_asist.status_code == 200:
                    for a in response_asist.json():
                        asistencias_existentes[a.get('documento_estudiante')] = a
                
                with st.form(key=f"form_asistencia_{curso}_{fecha}"):
                    st.markdown(f"**Curso {curso} - {fecha.strftime('%d/%m/%Y')}**")
                    st.markdown("---")
                    
                    # Cabecera simplificada
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
                    with col1:
                        st.markdown("**Estudiante**")
                    with col2:
                        st.markdown("**Estado**")
                    with col3:
                        st.markdown("**Novedad**")
                    with col4:
                        st.markdown("**Observación**")
                    st.markdown("---")
                    
                    datos_asistencia = []
                    
                    for estudiante in estudiantes:
                        doc = estudiante.get('documento_estudiante')
                        nombre = estudiante.get('nombre_estudiante')[:25]
                        existente = asistencias_existentes.get(doc, {})
                        
                        estado_actual = existente.get('estado', "Presente")
                        novedad_actual = "Retardo" if existente.get('retardo') else ("Uniforme" if existente.get('uniforme_malo') else "Ninguna")
                        observaciones_actual = existente.get('observaciones', "")
                        
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 3])
                        
                        with col1:
                            st.write(f"**{nombre}**")
                        with col2:
                            estado = st.selectbox(
                                "",
                                ["Presente", "Ausente"],
                                index=["Presente", "Ausente"].index(estado_actual),
                                key=f"estado_{doc}_{fecha}",
                                label_visibility="collapsed"
                            )
                        with col3:
                            if estado == "Presente":
                                novedad = st.selectbox(
                                    "",
                                    ["Ninguna", "Retardo", "Uniforme"],
                                    index=["Ninguna", "Retardo", "Uniforme"].index(novedad_actual),
                                    key=f"novedad_{doc}_{fecha}",
                                    label_visibility="collapsed"
                                )
                            else:
                                novedad = "Ninguna"
                                st.write("—")
                        with col4:
                            observaciones = st.text_input("", value=observaciones_actual, key=f"obs_{doc}_{fecha}",
                                                         label_visibility="collapsed", placeholder="Observación...")
                        
                        datos_asistencia.append({
                            "documento_estudiante": doc,
                            "curso": curso,
                            "fecha": str(fecha),
                            "estado": estado,
                            "retardo": novedad == "Retardo",
                            "uniforme_malo": novedad == "Uniforme",
                            "justificado": False,
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
                                                  "observaciones": registro['observaciones']
                                              })
                            else:
                                requests.post(f"{SUPABASE_URL}/rest/v1/asistencia", headers=headers, json=registro)
                            guardados += 1
                        
                        st.success(f"✅ Asistencia guardada para {guardados} estudiantes")
                        st.balloons()
            else:
                st.info("No hay estudiantes en este curso")
    
    # ============================================
    # REPORTE DE ASISTENCIA
    # ============================================
    st.divider()
    st.subheader("📊 Reporte de Asistencia")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", key="reporte_desde")
    with col2:
        fecha_fin = st.date_input("Hasta", key="reporte_hasta")
    
    if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
        url_datos = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
        response_datos = requests.get(url_datos, headers=headers)
        
        if response_datos.status_code == 200:
            datos = response_datos.json()
            if datos:
                df = pd.DataFrame(datos)
                
                # Mostrar resumen por estudiante
                st.markdown("---")
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
                with col1:
                    st.markdown("**Estudiante**")
                with col2:
                    st.markdown("**Presentes**")
                with col3:
                    st.markdown("**Ausentes**")
                with col4:
                    st.markdown("**Retardos**")
                with col5:
                    st.markdown("**Uniforme**")
                st.markdown("---")
                
                estudiantes_unicos = set([d.get('documento_estudiante') for d in datos])
                
                for doc_est in estudiantes_unicos:
                    # Obtener nombre del estudiante
                    url_nombre = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{doc_est}"
                    resp_nombre = requests.get(url_nombre, headers=headers)
                    nombre = resp_nombre.json()[0].get('nombre_estudiante') if resp_nombre.status_code == 200 and resp_nombre.json() else doc_est
                    
                    registros_est = [d for d in datos if d.get('documento_estudiante') == doc_est]
                    presentes = len([r for r in registros_est if r.get('estado') == 'Presente' and not r.get('retardo')])
                    ausentes = len([r for r in registros_est if r.get('estado') == 'Ausente'])
                    retardos = len([r for r in registros_est if r.get('retardo') == True])
                    uniformes = len([r for r in registros_est if r.get('uniforme_malo') == True])
                    
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
                    with col1:
                        st.write(f"**{nombre[:25]}**")
                    with col2:
                        st.write(f"{presentes}")
                    with col3:
                        st.write(f"{ausentes}")
                    with col4:
                        st.write(f"{retardos}")
                    with col5:
                        st.write(f"{uniformes}")
                
                st.markdown("---")
                st.success(f"Total registros: {len(datos)}")
                
                # Descargar
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar reporte", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")
            else:
                st.info("No hay registros en el período seleccionado")

# ============================================
# ESTUDIANTE - VER ASISTENCIA
# ============================================

def mostrar_asistencia_estudiante(data):
    st.subheader("📋 Reporte de Asistencia")
    
    documento = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{documento}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar asistencia")
        return
    
    asistencias = response.json()
    
    if not asistencias:
        st.info("No hay registros de asistencia")
        return
    
    df = pd.DataFrame(asistencias)
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    total = len(df)
    presentes = len(df[df['estado'] == 'Presente'])
    ausentes_total = len(df[df['estado'] == 'Ausente'])
    ausentes_justificados = len(df[(df['estado'] == 'Ausente') & (df['justificado'] == True)])
    ausentes_no_justificados = ausentes_total - ausentes_justificados
    retardos_total = len(df[df['retardo'] == True])
    uniforme_malo = len(df[df['uniforme_malo'] == True])
    porcentaje = (presentes / total * 100) if total > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📊 Total días", total)
    col2.metric("✅ Presentes", presentes)
    col3.metric("📈 % Asistencia", f"{porcentaje:.0f}%")
    col4.metric("⏰ Retardos", retardos_total)
    col5.metric("🎽 Uniforme mal", uniforme_malo)
    
    st.divider()
    st.write("**Detalle de asistencia:**")
    df_mostrar = df[['fecha', 'estado', 'retardo', 'justificado', 'uniforme_malo', 'observaciones']].sort_values('fecha', ascending=False)
    df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_mostrar, use_container_width=True)


# ============================================
# ACUDIENTE - VER ASISTENCIA DE HIJOS
# ============================================

def mostrar_asistencia_acudiente(data):
    st.subheader("📋 Asistencia de mis hijos")
    
    documento_acudiente = data.get('documento')
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_acudiente=eq.{documento_acudiente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar datos")
        return
    
    hijos = response.json()
    if not hijos:
        st.info("No hay hijos asociados")
        return
    
    for hijo in hijos:
        doc_hijo = hijo.get('documento_estudiante')
        nombre_hijo = hijo.get('nombre_estudiante')
        
        with st.expander(f"📘 {nombre_hijo} - Curso {hijo.get('curso')}"):
            url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{doc_hijo}"
            response_asist = requests.get(url_asist, headers=headers)
            
            if response_asist.status_code == 200:
                asistencias = response_asist.json()
                if asistencias:
                    df = pd.DataFrame(asistencias)
                    df_mostrar = df[['fecha', 'estado', 'retardo', 'justificado', 'uniforme_malo', 'observaciones']].sort_values('fecha', ascending=False)
                    df_mostrar['fecha'] = pd.to_datetime(df_mostrar['fecha']).dt.strftime('%d/%m')
                    st.dataframe(df_mostrar, use_container_width=True)
                else:
                    st.info("Sin registros")


# ============================================
# SECRETARIA/COORDINADOR - REPORTE GENERAL
# ============================================

def mostrar_reporte_asistencia_general(data):
    st.subheader("📊 Reporte General de Asistencia")
    
    headers = get_headers()
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    curso = st.selectbox("Seleccionar curso", cursos)
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde")
    with col2:
        fecha_fin = st.date_input("Hasta")
    
    if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
        mostrar_reporte_asistencia(curso, fecha_inicio, fecha_fin, headers, f"Reporte de Asistencia - Curso {curso}")
