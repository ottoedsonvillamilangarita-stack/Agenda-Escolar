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
    
    # Obtener cursos del docente (incluye dirección de curso)
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
    
    # Cabecera
    st.markdown(f"**{curso} - {fecha.strftime('%d/%m/%Y')}**")
    st.markdown("---")
    
    # Columnas
    col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 3])
    with col1:
        st.markdown("**Estudiante**")
    with col2:
        st.markdown("**Estado**")
    with col3:
        st.markdown("**Retardo**")
    with col4:
        st.markdown("**Uniforme**")
    with col5:
        st.markdown("**Observación**")
    st.markdown("---")
    
    # Filas por estudiante
    datos_asistencia = []
    
    for estudiante in estudiantes:
        doc = estudiante.get('documento_estudiante')
        nombre = estudiante.get('nombre_estudiante')[:25]
        existente = asistencias_existentes.get(doc, {})
        
        estado_actual = existente.get('estado', "Presente")
        retardo_actual = existente.get('retardo', False)
        uniforme_actual = existente.get('uniforme_malo', False)
        observaciones_actual = existente.get('observaciones', "")
        
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 3])
        
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
            retardo = st.checkbox("", value=retardo_actual, key=f"retardo_{doc}_{fecha}")
        
        with col4:
            uniforme = st.checkbox("", value=uniforme_actual, key=f"uniforme_{doc}_{fecha}")
        
        with col5:
            observaciones = st.text_input("", value=observaciones_actual, key=f"obs_{doc}_{fecha}",
                                         label_visibility="collapsed", placeholder="Observación...")
        
        datos_asistencia.append({
            "documento_estudiante": doc,
            "curso": curso,
            "fecha": str(fecha),
            "estado": estado,
            "retardo": retardo,
            "uniforme_malo": uniforme,
            "observaciones": observaciones,
            "documento_docente": documento_docente
        })
        
        st.markdown("---")
    
    # Guardar
    if st.button("💾 Guardar Asistencia", type="primary", use_container_width=True):
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
                    "observaciones": registro['observaciones']
                }
                response = requests.patch(f"{SUPABASE_URL}/rest/v1/asistencia?id=eq.{id_asist}", 
                                          headers=headers, json=update_data)
            else:
                response = requests.post(f"{SUPABASE_URL}/rest/v1/asistencia", headers=headers, json=registro)
            
            if response.status_code in [200, 201, 204]:
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
    
    # Estadísticas
    total = len(df)
    presentes = len(df[df['estado'] == 'Presente'])
    ausentes = len(df[df['estado'] == 'Ausente'])
    retardos = len(df[df['retardo'] == True])
    uniforme_malo = len(df[df['uniforme_malo'] == True])
    porcentaje = (presentes / total * 100) if total > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📊 Total días", total)
    col2.metric("✅ Presentes", presentes)
    col3.metric("❌ Ausentes", ausentes)
    col4.metric("⏰ Retardos", retardos)
    col5.metric("🎽 Uniforme mal", uniforme_malo)
    
    st.progress(porcentaje / 100)
    st.caption(f"📈 Porcentaje de asistencia: {porcentaje:.1f}%")
    
    st.divider()
    
    # Tabla detallada
    st.write("**Detalle de asistencia:**")
    df_mostrar = df[['fecha', 'estado', 'retardo', 'uniforme_malo', 'observaciones']].sort_values('fecha', ascending=False)
    df_mostrar['fecha'] = df_mostrar['fecha'].dt.strftime('%d/%m/%Y')
    df_mostrar = df_mostrar.rename(columns={
        'fecha': 'Fecha',
        'estado': 'Estado',
        'retardo': 'Retardo',
        'uniforme_malo': 'Uniforme mal',
        'observaciones': 'Observaciones'
    })
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
                    
                    total = len(df)
                    presentes = len(df[df['estado'] == 'Presente'])
                    ausentes = len(df[df['estado'] == 'Ausente'])
                    retardos = len(df[df['retardo'] == True])
                    uniforme_malo = len(df[df['uniforme_malo'] == True])
                    porcentaje = (presentes / total * 100) if total > 0 else 0
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("✅ Presentes", presentes)
                    col2.metric("📊 %", f"{porcentaje:.0f}%")
                    col3.metric("⏰ Retardos", retardos)
                    col4.metric("🎽 Uniforme mal", uniforme_malo)
                    
                    st.progress(porcentaje / 100)
                    
                    st.write("**Detalle:**")
                    df_mostrar = df[['fecha', 'estado', 'retardo', 'uniforme_malo', 'observaciones']].sort_values('fecha', ascending=False)
                    df_mostrar['fecha'] = pd.to_datetime(df_mostrar['fecha']).dt.strftime('%d/%m')
                    df_mostrar = df_mostrar.rename(columns={
                        'fecha': 'Fecha',
                        'estado': 'Estado',
                        'retardo': 'Retardo',
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
    st.success(f"📌 Curso: {curso}")
    
    # Opción: Marcar asistencia o ver reporte
    modo = st.radio("Seleccionar acción:", ["📋 Marcar Asistencia", "📊 Ver Reporte"], horizontal=True)
    
    if modo == "📋 Marcar Asistencia":
        # Llamar a la función de asistencia del docente
        mostrar_asistencia_docente(data)
    else:
        # Mostrar reporte
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
                    ausentes = len([a for a in asistencias if a['estado'] == 'Ausente'])
                    retardos = len([a for a in asistencias if a.get('retardo') == True])
                    uniforme_malo = len([a for a in asistencias if a.get('uniforme_malo') == True])
                    porcentaje = (presentes / total * 100) if total > 0 else 0
                    
                    reporte.append({
                        "Estudiante": nombre,
                        "Presentes": presentes,
                        "Ausentes": ausentes,
                        "Retardos": retardos,
                        "Uniforme mal": uniforme_malo,
                        "% Asist.": f"{porcentaje:.0f}"
                    })
            
            if reporte:
                df = pd.DataFrame(reporte)
                st.dataframe(df, use_container_width=True)
                
                # Resaltar estudiantes con problemas
                df_alerta = df[(df['Ausentes'] > 3) | (df['Retardos'] > 5) | (df['Uniforme mal'] > 3)]
                if not df_alerta.empty:
                    st.error("🚨 ESTUDIANTES CON ALERTAS:")
                    st.dataframe(df_alerta[['Estudiante', 'Ausentes', 'Retardos', 'Uniforme mal']], use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar reporte", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")
            else:
                st.info("No hay datos en el período seleccionado")

# ============================================
# REPORTE PARA SECRETARIA/COORDINADOR
# ============================================

def mostrar_reporte_asistencia_general(data):
    st.subheader("📊 Reporte General de Asistencia")
    
    headers = get_headers()
    
    # Seleccionar curso
    cursos = ["Todos", "901", "902", "903", "1001", "1002", "1003", "1101"]
    curso = st.selectbox("Curso", cursos)
    
    # Seleccionar período
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha inicio")
    with col2:
        fecha_fin = st.date_input("Fecha fin")
    
    if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
        # Obtener estudiantes
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
                ausentes = len([a for a in asistencias if a['estado'] == 'Ausente'])
                retardos = len([a for a in asistencias if a.get('retardo') == True])
                uniforme_malo = len([a for a in asistencias if a.get('uniforme_malo') == True])
                porcentaje = (presentes / total * 100) if total > 0 else 0
                
                reporte.append({
                    "Curso": curso_est,
                    "Estudiante": nombre,
                    "Presentes": presentes,
                    "Ausentes": ausentes,
                    "Retardos": retardos,
                    "Uniforme mal": uniforme_malo,
                    "% Asist.": f"{porcentaje:.0f}"
                })
        
        if reporte:
            df = pd.DataFrame(reporte)
            st.dataframe(df, use_container_width=True)
            
            # Resumen por curso
            st.subheader("📊 Resumen por Curso")
            resumen_curso = df.groupby('Curso').agg({
                'Presentes': 'sum',
                'Ausentes': 'sum',
                'Retardos': 'sum',
                'Uniforme mal': 'sum'
            }).reset_index()
            st.dataframe(resumen_curso, use_container_width=True)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar reporte", data=csv, file_name="reporte_asistencia_general.csv", mime="text/csv")
        else:
            st.info("No hay datos en el período seleccionado")
