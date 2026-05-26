import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

# ============================================
# DOCENTE Y DIRECTOR - MARCAR ASISTENCIA
# ============================================

def mostrar_asistencia_docente(data):
    st.subheader("📋 Marcar Asistencia")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    # Obtener cursos del docente
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
    
    # Seleccionar curso y fecha
    col1, col2 = st.columns(2)
    with col1:
        curso = st.selectbox("Curso", cursos_unicos)
    with col2:
        fecha = st.date_input("Fecha", datetime.now())
    
    # Obtener estudiantes
    url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
    response_est = requests.get(url_est, headers=headers)
    
    if response_est.status_code != 200:
        st.error("Error al cargar estudiantes")
        return
    
    estudiantes = response_est.json()
    if not estudiantes:
        st.warning(f"No hay estudiantes en el curso {curso}")
        return
    
    # Obtener asistencias existentes
    asistencias_existentes = {}
    url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=eq.{fecha}"
    response_asist = requests.get(url_asist, headers=headers)
    
    if response_asist.status_code == 200:
        for a in response_asist.json():
            asistencias_existentes[a.get('documento_estudiante')] = a
    
    st.markdown(f"**{curso} - {fecha.strftime('%d/%m/%Y')}**")
    st.markdown("---")
    
    # Formulario
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
            
            # Keys únicas usando idx
            estado_key = f"estado_{doc}_{idx}"
            retardo_key = f"retardo_{doc}_{idx}"
            uniforme_key = f"uniforme_{doc}_{idx}"
            justificado_key = f"justificado_{doc}_{idx}"
            obs_key = f"obs_{doc}_{idx}"
            
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 2])
            
            with col1:
                st.write(f"**{nombre}**")
            
            with col2:
                estado = st.selectbox(
                    "",
                    ["Presente", "Ausente"],
                    index=["Presente", "Ausente"].index(estado_actual),
                    key=estado_key,
                    label_visibility="collapsed"
                )
            
            with col3:
                if estado == "Presente":
                    retardo = st.checkbox("", value=retardo_actual, key=retardo_key)
                else:
                    retardo = False
                    st.write("—")
            
            with col4:
                uniforme = st.checkbox("", value=uniforme_actual, key=uniforme_key)
            
            with col5:
                # JUSTIFICADO: disponible para Ausente O Retardo
                if estado == "Ausente" or retardo:
                    justificado = st.checkbox("", value=justificado_actual, key=justificado_key)
                else:
                    justificado = False
                    st.write("—")
            
            with col6:
                observaciones = st.text_input("", value=observaciones_actual, key=obs_key,
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
                    update_data = {
                        "estado": registro['estado'],
                        "retardo": registro['retardo'],
                        "uniforme_malo": registro['uniforme_malo'],
                        "justificado": registro['justificado'],
                        "observaciones": registro['observaciones']
                    }
                    requests.patch(f"{SUPABASE_URL}/rest/v1/asistencia?id=eq.{id_asist}", 
                                  headers=headers, json=update_data)
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/asistencia", headers=headers, json=registro)
                guardados += 1
            
            st.success(f"✅ Asistencia guardada para {guardados} estudiantes")
            st.balloons()

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
    retardos_justificados = len(df[(df['retardo'] == True) & (df['justificado'] == True)])
    retardos_no_justificados = retardos_total - retardos_justificados
    uniforme_malo = len(df[df['uniforme_malo'] == True])
    porcentaje = (presentes / total * 100) if total > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 Total días", total)
    col2.metric("✅ Presentes", presentes)
    col3.metric("📈 % Asistencia", f"{porcentaje:.0f}%")
    col4.metric("🎽 Uniforme mal", uniforme_malo)
    
    st.divider()
    
    st.write("**📋 Detalle de ausencias:**")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"❌ Ausencias totales: {ausentes_total}")
        st.write(f"✅ Justificadas: {ausentes_justificados}")
    with col2:
        if ausentes_no_justificados > 0:
            st.warning(f"⚠️ No justificadas: {ausentes_no_justificados}")
        else:
            st.success(f"✅ No justificadas: {ausentes_no_justificados}")
    
    st.divider()
    
    st.write("**⏰ Detalle de retardos:**")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"⏰ Retardos totales: {retardos_total}")
        st.write(f"✅ Justificados: {retardos_justificados}")
    with col2:
        if retardos_no_justificados > 0:
            st.warning(f"⚠️ No justificados: {retardos_no_justificados}")
        else:
            st.success(f"✅ No justificados: {retardos_no_justificados}")
    
    st.divider()
    
    st.write("**Detalle de asistencia:**")
    df_mostrar = df[['fecha', 'estado', 'retardo', 'justificado', 'uniforme_malo', 'observaciones']].sort_values('fecha', ascending=False)
    df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%d/%m/%Y')
    df_mostrar = df_mostrar.rename(columns={
        'fecha': 'Fecha',
        'estado': 'Estado',
        'retardo': 'Retardo',
        'justificado': 'Justif.',
        'uniforme_malo': 'Uniforme mal',
        'observaciones': 'Observaciones'
    })
    st.dataframe(df_mostrar, use_container_width=True)
    
    if ausentes_no_justificados > 3:
        st.error(f"🚨 ALERTA: Tienes {ausentes_no_justificados} ausencias sin justificar")


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
                    
                    total = len(df)
                    presentes = len(df[df['estado'] == 'Presente'])
                    ausentes_total = len(df[df['estado'] == 'Ausente'])
                    ausentes_justificados = len(df[(df['estado'] == 'Ausente') & (df['justificado'] == True)])
                    ausentes_no_justificados = ausentes_total - ausentes_justificados
                    retardos_total = len(df[df['retardo'] == True])
                    uniforme_malo = len(df[df['uniforme_malo'] == True])
                    porcentaje = (presentes / total * 100) if total > 0 else 0
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("✅ Presentes", presentes)
                    col2.metric("📊 %", f"{porcentaje:.0f}%")
                    col3.metric("❌ Ausencias", ausentes_total)
                    col4.metric("🎽 Uniforme mal", uniforme_malo)
                    
                    st.progress(porcentaje / 100)
                    
                    if ausentes_no_justificados > 0:
                        st.warning(f"⚠️ Ausencias sin justificar: {ausentes_no_justificados}")
                    
                    df_mostrar = df[['fecha', 'estado', 'retardo', 'justificado', 'uniforme_malo', 'observaciones']].sort_values('fecha', ascending=False)
                    df_mostrar['fecha'] = pd.to_datetime(df_mostrar['fecha']).dt.strftime('%d/%m')
                    df_mostrar = df_mostrar.rename(columns={
                        'fecha': 'Fecha',
                        'estado': 'Estado',
                        'retardo': 'Retardo',
                        'justificado': 'Justif.',
                        'uniforme_malo': 'Uniforme',
                        'observaciones': 'Observaciones'
                    })
                    st.dataframe(df_mostrar, use_container_width=True)
                else:
                    st.info("Sin registros")


# ============================================
# DIRECTOR - REPORTE DE ASISTENCIA DEL CURSO
# ============================================

def mostrar_asistencia_director(data):
    st.subheader("📋 Reporte de Asistencia del Curso")
    
    documento_docente = data.get('documento')
    headers = get_headers()
    
    url_dir = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}&asignatura=eq.Dirección de Curso"
    response_dir = requests.get(url_dir, headers=headers)
    
    if response_dir.status_code != 200 or not response_dir.json():
        st.warning("No eres director de ningún curso")
        return
    
    curso = response_dir.json()[0].get('curso')
    st.success(f"📌 Curso: {curso}")
    
    # Botón para marcar asistencia
    if st.button("📋 Marcar Asistencia Hoy", use_container_width=True):
        mostrar_asistencia_docente(data)
        return
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde")
    with col2:
        fecha_fin = st.date_input("Hasta")
    
    if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code != 200:
            st.error("Error al cargar estudiantes")
            return
        
        estudiantes = response_est.json()
        
        # Cabecera del reporte
        st.markdown("---")
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
        with col1:
            st.markdown("**Estudiante**")
        with col2:
            st.markdown("**Presentes**")
        with col3:
            st.markdown("**Ausentes**")
        with col4:
            st.markdown("**Aus. Justif.**")
        with col5:
            st.markdown("**Aus. No Justif.**")
        with col6:
            st.markdown("**Retardos**")
        st.markdown("---")
        
        reporte = []
        for estudiante in estudiantes:
            doc = estudiante.get('documento_estudiante')
            nombre = estudiante.get('nombre_estudiante')
            
            url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{doc}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
            response_asist = requests.get(url_asist, headers=headers)
            
            if response_asist.status_code == 200:
                asistencias = response_asist.json()
                total = len(asistencias)
                presentes = len([a for a in asistencias if a['estado'] == 'Presente'])
                ausentes_total = len([a for a in asistencias if a['estado'] == 'Ausente'])
                ausentes_justificados = len([a for a in asistencias if a['estado'] == 'Ausente' and a.get('justificado') == True])
                ausentes_no_justificados = ausentes_total - ausentes_justificados
                retardos_total = len([a for a in asistencias if a.get('retardo') == True])
                
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
                with col1:
                    st.write(f"**{nombre}**")
                with col2:
                    st.write(f"{presentes}")
                with col3:
                    st.write(f"{ausentes_total}")
                with col4:
                    st.write(f"{ausentes_justificados}")
                with col5:
                    if ausentes_no_justificados > 0:
                        st.warning(f"{ausentes_no_justificados}")
                    else:
                        st.write("0")
                with col6:
                    st.write(f"{retardos_total}")
                
                reporte.append({
                    "Estudiante": nombre,
                    "Presentes": presentes,
                    "Ausentes": ausentes_total,
                    "Aus. Justif.": ausentes_justificados,
                    "Aus. No Justif.": ausentes_no_justificados,
                    "Retardos": retardos_total
                })
        
        if reporte:
            st.markdown("---")
            df = pd.DataFrame(reporte)
            
            # Alertas
            df_alerta = df[df['Aus. No Justif.'] > 3]
            if not df_alerta.empty:
                st.error("🚨 ESTUDIANTES CON MÁS DE 3 AUSENCIAS SIN JUSTIFICAR:")
                for _, row in df_alerta.iterrows():
                    st.write(f"• {row['Estudiante']}: {row['Aus. No Justif.']} ausencias sin justificar")
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar reporte", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")
        else:
            st.info("No hay datos en el período seleccionado")


# ============================================
# SECRETARIA/COORDINADOR - REPORTE GENERAL
# ============================================

def mostrar_reporte_asistencia_general(data):
    st.subheader("📊 Reporte General de Asistencia")
    
    headers = get_headers()
    
    cursos = ["Todos", "901", "902", "903", "1001", "1002", "1003", "1101"]
    curso = st.selectbox("Curso", cursos)
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha inicio")
    with col2:
        fecha_fin = st.date_input("Fecha fin")
    
    if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
        if curso == "Todos":
            url_est = f"{SUPABASE_URL}/rest/v1/estudiantes"
        else:
            url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code != 200:
            st.error("Error al cargar estudiantes")
            return
        
        estudiantes = response_est.json()
        
        reporte = []
        for estudiante in estudiantes:
            doc = estudiante.get('documento_estudiante')
            nombre = estudiante.get('nombre_estudiante')
            curso_est = estudiante.get('curso')
            
            url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{doc}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
            response_asist = requests.get(url_asist, headers=headers)
            
            if response_asist.status_code == 200:
                asistencias = response_asist.json()
                total = len(asistencias)
                presentes = len([a for a in asistencias if a['estado'] == 'Presente'])
                ausentes_total = len([a for a in asistencias if a['estado'] == 'Ausente'])
                ausentes_justificados = len([a for a in asistencias if a['estado'] == 'Ausente' and a.get('justificado') == True])
                ausentes_no_justificados = ausentes_total - ausentes_justificados
                retardos_total = len([a for a in asistencias if a.get('retardo') == True])
                uniforme_malo = len([a for a in asistencias if a.get('uniforme_malo') == True])
                porcentaje = (presentes / total * 100) if total > 0 else 0
                
                reporte.append({
                    "Curso": curso_est,
                    "Estudiante": nombre,
                    "Presentes": presentes,
                    "Ausentes": ausentes_total,
                    "Aus. Justif.": ausentes_justificados,
                    "Aus. No Justif.": ausentes_no_justificados,
                    "Retardos": retardos_total,
                    "Uniforme mal": uniforme_malo,
                    "% Asist.": f"{porcentaje:.0f}"
                })
        
        if reporte:
            df = pd.DataFrame(reporte)
            st.dataframe(df, use_container_width=True)
            
            st.subheader("📊 Resumen por Curso")
            resumen_curso = df.groupby('Curso').agg({
                'Presentes': 'sum',
                'Ausentes': 'sum',
                'Aus. Justif.': 'sum',
                'Aus. No Justif.': 'sum',
                'Retardos': 'sum',
                'Uniforme mal': 'sum'
            }).reset_index()
            st.dataframe(resumen_curso, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar reporte", data=csv, file_name="reporte_asistencia_general.csv", mime="text/csv")
        else:
            st.info("No hay datos en el período seleccionado")
