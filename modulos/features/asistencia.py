import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

# ============================================
# DOCENTE - MARCAR ASISTENCIA
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
    
    with st.form(key=f"asis_docente_{curso}_{fecha}"):
        # Cabecera
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 2])
        with col1:
            st.markdown("**Estudiante**")
        with col2:
            st.markdown("**Estado**")
        with col3:
            st.markdown("**Retardo**")
        with col4:
            st.markdown("**Uniforme**")
        with col5:
            st.markdown("**Justificar**")
        st.markdown("---")
        
        datos = []
        
        for idx, est in enumerate(estudiantes):
            doc = est.get('documento_estudiante')
            nombre = est.get('nombre_estudiante')[:25]
            existente = asistencias_existentes.get(doc, {})
            
            estado_val = existente.get('estado', "Presente")
            retardo_val = existente.get('retardo', False)
            uniforme_val = existente.get('uniforme_malo', False)
            justificado_val = existente.get('justificado', False)
            
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 2])
            
            with col1:
                st.write(f"**{nombre}**")
            with col2:
                estado = st.selectbox(
                    "",
                    ["Presente", "Ausente"],
                    index=["Presente", "Ausente"].index(estado_val),
                    key=f"estado_doc_{idx}_{doc}",
                    label_visibility="collapsed"
                )
            with col3:
                if estado == "Presente":
                    retardo = st.checkbox("", value=retardo_val, key=f"retardo_doc_{idx}_{doc}")
                else:
                    retardo = False
                    st.write("—")
            with col4:
                uniforme = st.checkbox("", value=uniforme_val, key=f"uniforme_doc_{idx}_{doc}")
            with col5:
                # JUSTIFICADO: SIEMPRE visible
                justificado = st.checkbox("", value=justificado_val, key=f"justi_doc_{idx}_{doc}")
            
            datos.append({
                "doc": doc,
                "estado": estado,
                "retardo": retardo if estado == "Presente" else False,
                "uniforme": uniforme,
                "justificado": justificado
            })
        
        if st.form_submit_button("💾 Guardar", type="primary", use_container_width=True):
            guardados = 0
            for d in datos:
                check_url = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{d['doc']}&fecha=eq.{fecha}"
                check = requests.get(check_url, headers=headers)
                
                data_reg = {
                    "documento_estudiante": d['doc'],
                    "curso": curso,
                    "fecha": str(fecha),
                    "estado": d['estado'],
                    "retardo": d['retardo'],
                    "uniforme_malo": d['uniforme'],
                    "justificado": d['justificado'],
                    "observaciones": "",
                    "documento_docente": documento_docente
                }
                
                if check.status_code == 200 and check.json():
                    id_reg = check.json()[0].get('id')
                    requests.patch(f"{SUPABASE_URL}/rest/v1/asistencia?id=eq.{id_reg}", 
                                  headers=headers, json=data_reg)
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/asistencia", headers=headers, json=data_reg)
                guardados += 1
            
            st.success(f"✅ Guardados {guardados} registros")
            st.balloons()


# ============================================
# DIRECTOR - MARCAR ASISTENCIA
# ============================================

def mostrar_asistencia_director(data):
    st.subheader("📋 Marcar Asistencia")
    
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
    
    with st.form(key=f"asis_director_{curso}_{fecha}"):
        # Cabecera
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 2])
        with col1:
            st.markdown("**Estudiante**")
        with col2:
            st.markdown("**Estado**")
        with col3:
            st.markdown("**Retardo**")
        with col4:
            st.markdown("**Uniforme**")
        with col5:
            st.markdown("**Justificar**")
        st.markdown("---")
        
        datos = []
        
        for idx, est in enumerate(estudiantes):
            doc = est.get('documento_estudiante')
            nombre = est.get('nombre_estudiante')[:25]
            existente = asistencias_existentes.get(doc, {})
            
            estado_val = existente.get('estado', "Presente")
            retardo_val = existente.get('retardo', False)
            uniforme_val = existente.get('uniforme_malo', False)
            justificado_val = existente.get('justificado', False)
            
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 2])
            
            with col1:
                st.write(f"**{nombre}**")
            with col2:
                estado = st.selectbox(
                    "",
                    ["Presente", "Ausente"],
                    index=["Presente", "Ausente"].index(estado_val),
                    key=f"estado_dir_{idx}_{doc}",
                    label_visibility="collapsed"
                )
            with col3:
                if estado == "Presente":
                    retardo = st.checkbox("", value=retardo_val, key=f"retardo_dir_{idx}_{doc}")
                else:
                    retardo = False
                    st.write("—")
            with col4:
                uniforme = st.checkbox("", value=uniforme_val, key=f"uniforme_dir_{idx}_{doc}")
            with col5:
                # JUSTIFICADO: SIEMPRE visible
                justificado = st.checkbox("", value=justificado_val, key=f"justi_dir_{idx}_{doc}")
            
            datos.append({
                "doc": doc,
                "estado": estado,
                "retardo": retardo if estado == "Presente" else False,
                "uniforme": uniforme,
                "justificado": justificado
            })
        
        if st.form_submit_button("💾 Guardar Asistencia", type="primary", use_container_width=True):
            guardados = 0
            for d in datos:
                check_url = f"{SUPABASE_URL}/rest/v1/asistencia?documento_estudiante=eq.{d['doc']}&fecha=eq.{fecha}"
                check = requests.get(check_url, headers=headers)
                
                data_reg = {
                    "documento_estudiante": d['doc'],
                    "curso": curso,
                    "fecha": str(fecha),
                    "estado": d['estado'],
                    "retardo": d['retardo'],
                    "uniforme_malo": d['uniforme'],
                    "justificado": d['justificado'],
                    "observaciones": "",
                    "documento_docente": documento_docente
                }
                
                if check.status_code == 200 and check.json():
                    id_reg = check.json()[0].get('id')
                    requests.patch(f"{SUPABASE_URL}/rest/v1/asistencia?id=eq.{id_reg}", 
                                  headers=headers, json=data_reg)
                else:
                    requests.post(f"{SUPABASE_URL}/rest/v1/asistencia", headers=headers, json=data_reg)
                guardados += 1
            
            st.success(f"✅ Asistencia guardada para {guardados} estudiantes")
            st.balloons()


# ============================================
# DIRECTOR - REPORTE DE ASISTENCIA
# ============================================

def mostrar_reporte_asistencia_director(data):
    st.subheader("📊 Reporte de Asistencia")
    
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
    
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Desde", datetime.now().replace(day=1))
    with col2:
        fecha_fin = st.date_input("Hasta", datetime.now())
    
    if st.button("📊 Generar Reporte", type="primary", use_container_width=True):
        # Obtener estudiantes
        url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?curso=eq.{curso}"
        response_est = requests.get(url_est, headers=headers)
        
        if response_est.status_code == 200:
            estudiantes = {e['documento_estudiante']: e['nombre_estudiante'] for e in response_est.json()}
            
            # Obtener asistencias
            url_asist = f"{SUPABASE_URL}/rest/v1/asistencia?curso=eq.{curso}&fecha=gte.{fecha_inicio}&fecha=lte.{fecha_fin}"
            response_asist = requests.get(url_asist, headers=headers)
            
            if response_asist.status_code == 200:
                asistencias = response_asist.json()
                
                # Procesar por estudiante
                resumen = {}
                for doc, nombre in estudiantes.items():
                    resumen[doc] = {
                        "nombre": nombre,
                        "presentes": 0,
                        "ausentes": 0,
                        "justificados": 0,
                        "retardos": 0,
                        "uniformes": 0
                    }
                
                for a in asistencias:
                    doc = a.get('documento_estudiante')
                    if doc in resumen:
                        if a.get('estado') == 'Presente' and not a.get('retardo'):
                            resumen[doc]["presentes"] += 1
                        elif a.get('estado') == 'Ausente':
                            resumen[doc]["ausentes"] += 1
                            if a.get('justificado'):
                                resumen[doc]["justificados"] += 1
                        if a.get('retardo'):
                            resumen[doc]["retardos"] += 1
                        if a.get('uniforme_malo'):
                            resumen[doc]["uniformes"] += 1
                
                # Mostrar tabla
                st.markdown("---")
                col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
                with col1:
                    st.markdown("**Estudiante**")
                with col2:
                    st.markdown("**Presentes**")
                with col3:
                    st.markdown("**Ausentes**")
                with col4:
                    st.markdown("**Justif.**")
                with col5:
                    st.markdown("**Retardos**")
                with col6:
                    st.markdown("**Uniforme**")
                st.markdown("---")
                
                for doc, vals in resumen.items():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 1, 1])
                    with col1:
                        st.write(f"**{vals['nombre'][:25]}**")
                    with col2:
                        st.write(f"{vals['presentes']}")
                    with col3:
                        st.write(f"{vals['ausentes']}")
                    with col4:
                        st.write(f"{vals['justificados']}")
                    with col5:
                        st.write(f"{vals['retardos']}")
                    with col6:
                        st.write(f"{vals['uniformes']}")
                
                st.markdown("---")
                
                # Alertas
                st.subheader("🚨 Alertas")
                hay_alertas = False
                for doc, vals in resumen.items():
                    no_justif = vals["ausentes"] - vals["justificados"]
                    if no_justif > 3:
                        st.warning(f"• {vals['nombre']}: {no_justif} ausencias sin justificar")
                        hay_alertas = True
                    if vals['retardos'] > 5:
                        st.warning(f"• {vals['nombre']}: {vals['retardos']} retardos")
                        hay_alertas = True
                    if vals['uniformes'] > 3:
                        st.warning(f"• {vals['nombre']}: {vals['uniformes']} llamados por uniforme")
                        hay_alertas = True
                
                if not hay_alertas:
                    st.success("✅ No hay estudiantes con alertas")
                
                # Descargar
                df = pd.DataFrame([{
                    "Estudiante": vals['nombre'],
                    "Presentes": vals['presentes'],
                    "Ausentes": vals['ausentes'],
                    "Justificados": vals['justificados'],
                    "Retardos": vals['retardos'],
                    "Uniforme": vals['uniformes']
                } for doc, vals in resumen.items()])
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar CSV", data=csv, file_name=f"asistencia_{curso}.csv", mime="text/csv")


# ============================================
# ESTUDIANTE - VER ASISTENCIA
# ============================================

def mostrar_asistencia_estudiante(data):
    st.subheader("📋 Mi Asistencia")
    
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
    st.dataframe(df, use_container_width=True)


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
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("Sin registros")
