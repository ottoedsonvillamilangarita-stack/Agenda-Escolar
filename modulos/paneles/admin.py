# ==============================================================================
# modulos/paneles/admin.py - PANEL ADMINISTRADOR INTEGRAL
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers
import modulos.features.horarios as horarios_feature

CURSOS_FALLBACK = ["901", "902", "903", "1001", "1002", "1003", "1101"]

def obtener_cursos_activos(headers):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=curso&order=curso.asc", headers=headers)
        if r.status_code == 200 and r.json():
            return [g['curso'] for g in r.json() if g.get('curso')]
    except Exception:
        pass
    return CURSOS_FALLBACK

def obtener_docentes_dict(headers):
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?order=apellidos_docente.asc", headers=headers)
        if r.status_code == 200 and r.json():
            return {str(d['documento_docente']): f"{d.get('apellidos_docente','')} {d.get('nombre_docente','')}".strip() for d in r.json()}
    except Exception:
        pass
    return {}

# ============================================
# VISTA PRINCIPAL
# ============================================
def mostrar(data):
    headers = get_headers()
    cursos = obtener_cursos_activos(headers)
    docentes = obtener_docentes_dict(headers)
    
    st.markdown("""
    <div style="background: white; padding: 16px 20px; border-radius: 10px; border: 1px solid #E2E8F0; display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
        <div>
            <h3 style="margin: 0; color: #0F172A; font-weight: 700;">PANEL DE CONTROL ADMINISTRATIVO</h3>
            <p style="margin: 2px 0 0 0; font-size: 12px; color: #64748B;">Gestión Escolar Integral</p>
        </div>
        <div>
            <span style="background: #DCFCE7; color: #166534; font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 12px;">Activo 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Cursos Registrados", len(cursos))
    col2.metric("Docentes en Planta", len(docentes))
    col3.metric("Estado Plataforma", "En Línea")

# ============================================
# GESTIÓN ACADÉMICA: ASIGNACIÓN DOCENTE Y DIRECTORES
# ============================================
def gestion_directores_grupo():
    st.subheader("👨‍🏫 Asignación de Directores de Grupo")
    headers = get_headers()
    cursos = obtener_cursos_activos(headers)
    docentes = obtener_docentes_dict(headers)

    r_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?asignatura=eq.DIRECCION%20DE%20GRUPO", headers=headers)
    dirs_actuales = r_asig.json() if r_asig.status_code == 200 else []
    map_dir = {d['curso']: str(d.get('documento_docente','')) for d in dirs_actuales if d.get('curso')}

    c_tabla, c_form = st.columns([1.3, 1], gap="medium")

    with c_tabla:
        st.markdown("**📋 Directores Asignados Actualmente**")
        data_resumen = []
        for c in cursos:
            doc_doc = map_dir.get(c)
            doc_nom = docentes.get(doc_doc, "⚠️ Sin asignar") if doc_doc else "⚠️ Sin asignar"
            data_resumen.append({"Curso": c, "Director de Grupo": doc_nom})
        st.dataframe(pd.DataFrame(data_resumen), use_container_width=True, height=280)

    with c_form:
        st.markdown("**✏️ Asignar / Actualizar Director**")
        with st.form("form_asignar_director", clear_on_submit=False):
            curso_sel = st.selectbox("Seleccionar Curso:", cursos)
            doc_actual_id = map_dir.get(curso_sel, "")
            st.caption(f"Actual: **{docentes.get(doc_actual_id, 'Ninguno')}**")

            opciones_docs = [""] + list(docentes.keys())
            idx_act = opciones_docs.index(doc_actual_id) if doc_actual_id in opciones_docs else 0
            doc_nuevo = st.selectbox("Nuevo Director:", opciones_docs, index=idx_act, format_func=lambda x: docentes.get(x, "Vacante (Sin asignar)") if x else "Vacante (Sin asignar)")

            if st.form_submit_button("💾 Guardar Director", type="primary", use_container_width=True):
                requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=eq.DIRECCION%20DE%20GRUPO", headers=headers)
                if doc_nuevo:
                    payload = {"curso": curso_sel, "asignatura": "DIRECCION DE GRUPO", "documento_docente": doc_nuevo, "anio": datetime.now().year}
                    requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=payload)
                    st.success(f"Director guardado para {curso_sel}")
                else:
                    st.info(f"Dirección de {curso_sel} liberada")
                st.rerun()

def asignar_docentes_curso():
    st.subheader("📚 Carga Académica (Docente por Asignatura)")
    headers = get_headers()
    cursos = obtener_cursos_activos(headers)
    docentes = obtener_docentes_dict(headers)

    r_mat = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
    materias_db = [m['nombre'].strip().upper() for m in r_mat.json() if m.get('nombre')] if r_mat.status_code == 200 else []
    if not materias_db:
        materias_db = ["MATEMATICAS", "ESPAÑOL", "INGLES", "CIENCIAS NATURALES", "CIENCIAS SOCIALES", "EDUCACION FISICA", "ARTISTICA", "TECNOLOGIA", "ETICA", "RELIGION", "FILOSOFIA", "FISICA", "QUIMICA"]

    c_top, _ = st.columns([1.5, 2.5])
    with c_top:
        curso_sel = st.selectbox("Seleccionar Curso a Gestionar:", cursos, key="carga_curso_sel")

    r_actuales = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}", headers=headers)
    actuales = [a for a in r_actuales.json() if "DIRECCION" not in str(a.get('asignatura', '')).upper()] if r_actuales.status_code == 200 else []

    col_t, col_f = st.columns([1.3, 1], gap="medium")

    with col_t:
        st.markdown(f"**Materias asignadas en {curso_sel}:**")
        if actuales:
            tabla = [{"Asignatura": a.get('asignatura'), "Docente": docentes.get(str(a.get('documento_docente')), a.get('documento_docente'))} for a in actuales]
            st.dataframe(pd.DataFrame(tabla), use_container_width=True, height=270)
            
            c_d1, c_d2 = st.columns([2, 1])
            with c_d1:
                asig_del = st.selectbox("Materia a retirar:", [a.get('asignatura') for a in actuales], label_visibility="collapsed")
            with c_d2:
                if st.button("🗑️ Quitar", use_container_width=True):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=eq.{asig_del}", headers=headers)
                    st.success("Removida")
                    st.rerun()
        else:
            st.info(f"El grado {curso_sel} no tiene materias asignadas aún.")

    with col_f:
        st.markdown("**➕ Asignar Materia a Docente:**")
        with st.form("form_asignar_doc_materia", clear_on_submit=True):
            materia_nom = st.selectbox("Asignatura:", materias_db)
            doc_id = st.selectbox("Docente Responsable:", list(docentes.keys()), format_func=lambda x: docentes.get(x, "Sin nombre"))
            
            if st.form_submit_button("💾 Guardar Carga Académica", type="primary", use_container_width=True):
                requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=eq.{materia_nom}", headers=headers)
                data_ins = {"curso": curso_sel, "asignatura": materia_nom, "documento_docente": doc_id, "anio": datetime.now().year}
                r_post = requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data_ins)
                if r_post.status_code == 201:
                    st.success(f"{materia_nom} asignada con éxito")
                    st.rerun()
                else:
                    st.error(f"Error: {r_post.text}")

# ============================================
# LLAMADAS AL MÓDULO DE HORARIOS
# ============================================
def configurar_niveles():
    horarios_feature.configurar_niveles(get_headers())

def configurar_horas_nivel():
    horarios_feature.configurar_horas_nivel(get_headers())

def configurar_jornada_nivel():
    horarios_feature.configurar_jornada_nivel(get_headers())

def configurar_horario_curso():
    horarios_feature.configurar_horario_curso(get_headers())

def gestion_festivos():
    horarios_feature.gestion_festivos(get_headers())

def gestionar_asignaturas():
    st.subheader("📚 Pénsum y Asignaturas")
    headers = get_headers()
    r = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
    if r.status_code == 200 and r.json():
        st.dataframe(pd.DataFrame(r.json())[['id', 'nombre', 'codigo']], use_container_width=True)
    with st.form("form_nueva_mat_admin", clear_on_submit=True):
        nom_m = st.text_input("Nombre Asignatura:")
        cod_m = st.text_input("Código (opcional):")
        if st.form_submit_button("Guardar Asignatura", type="primary"):
            if nom_m:
                requests.post(f"{SUPABASE_URL}/rest/v1/materias", headers=headers, json={"nombre": nom_m.strip().upper(), "codigo": cod_m.strip().upper() if cod_m else None})
                st.success("Materia creada")
                st.rerun()

def gestionar_grados():
    st.subheader("🏫 Cursos y Salones")
    headers = get_headers()
    r = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    if r.status_code == 200 and r.json():
        st.dataframe(pd.DataFrame(r.json()), use_container_width=True)

def gestion_estudiantes():
    st.subheader("Directorio Estudiantil")
    headers = get_headers()
    r = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    if r.status_code == 200 and r.json():
        st.dataframe(pd.DataFrame(r.json())[['documento_estudiante', 'nombre_estudiante', 'apellidos_estudiante', 'curso', 'estado']], use_container_width=True)

def gestion_docentes():
    st.subheader("Planta Docente")
    headers = get_headers()
    r = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?order=apellidos_docente.asc", headers=headers)
    if r.status_code == 200 and r.json():
        st.dataframe(pd.DataFrame(r.json())[['documento_docente', 'nombre_docente', 'apellidos_docente', 'email_docente', 'telefono_docente']], use_container_width=True)

def mostrar_sistema():
    st.subheader("⚙️ Configuración Institucional")
    st.info("Colegio de Prueba - Sistema Escolar 2026")

def reportes_academicos():
    st.subheader("📊 Reportes Académicos")
    st.info("Módulo de consolidación y reportes.")
