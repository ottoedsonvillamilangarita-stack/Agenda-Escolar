# ==============================================================================
# modulos/paneles/admin.py - PANEL ADMINISTRADOR CON DOBLE SINCRONIZACIÓN
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers
import modulos.features.horarios as horarios_feature

CURSOS_FALLBACK = ["901", "902", "903", "1001", "1002", "1003", "1101"]

def obtener_grados_info(headers):
    """Obtiene los grados mapeando curso con id_grado y nivel_id"""
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
        if r.status_code == 200 and r.json():
            return r.json()
    except Exception:
        pass
    return [{"curso": c, "id_grado": i+1, "nivel_id": 1} for i, c in enumerate(CURSOS_FALLBACK)]

def obtener_docentes_dict(headers):
    """Obtiene la lista completa de docentes con formato legible"""
    try:
        r = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?order=apellidos_docente.asc", headers=headers)
        if r.status_code == 200 and r.json():
            docs = {}
            for d in r.json():
                doc_id = str(d.get('documento_docente', '')).strip()
                if doc_id:
                    apellidos = str(d.get('apellidos_docente') or '').strip()
                    nombre = str(d.get('nombre_docente') or '').strip()
                    nom_completo = f"{apellidos} {nombre}".strip()
                    docs[doc_id] = nom_completo if nom_completo else f"Docente ({doc_id})"
            return docs
    except Exception:
        pass
    return {}

def mostrar(data):
    headers = get_headers()
    grados_info = obtener_grados_info(headers)
    cursos = [str(g['curso']).strip() for g in grados_info if g.get('curso')]
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

# ==============================================================================
# GESTIÓN ACADÉMICA: DIRECTORES DE GRUPO (DOBLE TABLA)
# ==============================================================================
def gestion_directores_grupo():
    st.subheader("👨‍🏫 Asignación de Directores de Grupo")
    headers = get_headers()
    grados_info = obtener_grados_info(headers)
    cursos = [str(g['curso']).strip() for g in grados_info if g.get('curso')]
    map_curso_idgrado = {str(g['curso']).strip(): g.get('id_grado') for g in grados_info}
    map_idgrado_curso = {g.get('id_grado'): str(g['curso']).strip() for g in grados_info}
    docentes = obtener_docentes_dict(headers)

    # 1. Consultar directores_grupo (tabla nativa)
    r_dg = requests.get(f"{SUPABASE_URL}/rest/v1/directores_grupo", headers=headers)
    dg_rows = r_dg.json() if r_dg.status_code == 200 else []
    map_dir = {map_idgrado_curso.get(r.get('id_grado')): str(r.get('docente_documento','')).strip() for r in dg_rows if r.get('id_grado')}

    # 2. Consultar asignacion_academica como respaldo
    r_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?asignatura=ilike.%direccion%", headers=headers)
    for a in (r_asig.json() if r_asig.status_code == 200 else []):
        c = str(a.get('curso', '')).strip()
        if c and not map_dir.get(c):
            map_dir[c] = str(a.get('documento_docente', '')).strip()

    c_tabla, c_form = st.columns([1.3, 1], gap="medium")

    with c_tabla:
        st.markdown("**📋 Panorama de Directores Asignados**")
        data_resumen = []
        for c in cursos:
            doc_id = map_dir.get(c, "")
            doc_nom = docentes.get(doc_id, f"Docente ({doc_id})" if doc_id else "⚠️ Sin asignar")
            data_resumen.append({"Curso": c, "Director de Grupo": doc_nom})
        st.dataframe(pd.DataFrame(data_resumen), use_container_width=True, height=280)

    with c_form:
        st.markdown("**✏️ Asignar o Cambiar Director**")
        curso_sel = st.selectbox("Seleccionar Curso:", cursos, key="dir_sel_curso_input")
        id_grado_sel = map_curso_idgrado.get(curso_sel)
        
        doc_actual_id = map_dir.get(curso_sel, "")
        doc_actual_nom = docentes.get(doc_actual_id, "Ninguno") if doc_actual_id else "Ninguno"
        st.caption(f"Director actual de **{curso_sel}**: `{doc_actual_nom}`")

        opciones_docs = [""] + list(docentes.keys())
        idx_act = opciones_docs.index(doc_actual_id) if doc_actual_id in opciones_docs else 0
        
        with st.form(f"form_asignar_director_{curso_sel}", clear_on_submit=False):
            doc_nuevo = st.selectbox(
                "Nuevo Director Docente:",
                opciones_docs,
                index=idx_act,
                format_func=lambda x: f"{docentes.get(x)} ({x})" if x else "Vacante (Sin asignar)",
                key=f"sb_doc_director_{curso_sel}"
            )

            if st.form_submit_button("💾 Guardar Director", type="primary", use_container_width=True):
                # Limpiar en directores_grupo
                if id_grado_sel:
                    requests.delete(f"{SUPABASE_URL}/rest/v1/directores_grupo?id_grado=eq.{id_grado_sel}", headers=headers)
                # Limpiar en asignacion_academica
                requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=ilike.%direccion%", headers=headers)

                if doc_nuevo:
                    # Guardar en directores_grupo
                    if id_grado_sel:
                        requests.post(f"{SUPABASE_URL}/rest/v1/directores_grupo", headers=headers, json={"id_grado": id_grado_sel, "docente_documento": doc_nuevo})
                    # Guardar en asignacion_academica
                    requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json={"curso": curso_sel, "asignatura": "DIRECCION DE GRUPO", "documento_docente": doc_nuevo, "anio": datetime.now().year})
                    
                    st.success(f"✅ {docentes.get(doc_nuevo, doc_nuevo)} asignado a {curso_sel}")
                else:
                    st.info(f"Dirección de {curso_sel} liberada.")
                st.rerun()

# ==============================================================================
# GESTIÓN ACADÉMICA: CARGA ACADÉMICA (DOCENTE POR ASIGNATURA)
# ==============================================================================
def asignar_docentes_curso():
    st.subheader("📚 Carga Académica (Docente por Asignatura)")
    headers = get_headers()
    grados_info = obtener_grados_info(headers)
    cursos = [str(g['curso']).strip() for g in grados_info if g.get('curso')]
    map_curso_nivel = {str(g['curso']).strip(): g.get('nivel_id') for g in grados_info}
    docentes = obtener_docentes_dict(headers)

    c_top, _ = st.columns([1.5, 2.5])
    with c_top:
        curso_sel = st.selectbox("Seleccionar Curso a Gestionar:", cursos, key="carga_curso_sel_act")

    nid_curso = map_curso_nivel.get(curso_sel)

    # Filtrar asignaturas por nivel educativo
    materias_filtradas = []
    if nid_curso:
        r_rel = requests.get(f"{SUPABASE_URL}/rest/v1/materias_niveles?nivel_id=eq.{nid_curso}", headers=headers)
        if r_rel.status_code == 200 and r_rel.json():
            ids_m = [r['materia_id'] for r in r_rel.json()]
            r_mat_filt = requests.get(f"{SUPABASE_URL}/rest/v1/materias", headers=headers)
            if r_mat_filt.status_code == 200:
                materias_filtradas = [m['nombre'].strip().upper() for m in r_mat_filt.json() if m['id'] in ids_m and m.get('nombre')]

    if not materias_filtradas:
        r_all_m = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
        materias_filtradas = [m['nombre'].strip().upper() for m in r_all_m.json() if m.get('nombre')] if r_all_m.status_code == 200 and r_all_m.json() else ["MATEMATICAS", "ESPAÑOL", "INGLES"]

    # Traer asignaciones existentes excluyendo direcciones de curso
    r_actuales = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}", headers=headers)
    actuales_raw = r_actuales.json() if r_actuales.status_code == 200 else []
    actuales = [a for a in actuales_raw if "DIRECCION" not in str(a.get('asignatura', '')).upper()]

    col_t, col_f = st.columns([1.3, 1], gap="medium")

    with col_t:
        st.markdown(f"**Materias asignadas a {curso_sel}:**")
        if actuales:
            tabla = []
            for a in actuales:
                d_id = str(a.get('documento_docente', '')).strip()
                tabla.append({
                    "Asignatura": a.get('asignatura'),
                    "Docente": docentes.get(d_id, f"Docente ({d_id})")
                })
            st.dataframe(pd.DataFrame(tabla), use_container_width=True, height=270)
            
            c_d1, c_d2 = st.columns([2, 1])
            with c_d1:
                asig_del = st.selectbox("Materia a retirar:", [a.get('asignatura') for a in actuales], label_visibility="collapsed", key=f"sel_ret_materia_{curso_sel}")
            with c_d2:
                if st.button("🗑️ Quitar", key=f"btn_del_mat_{curso_sel}", use_container_width=True):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=eq.{asig_del}", headers=headers)
                    st.success(f"{asig_del} retirada")
                    st.rerun()
        else:
            st.info(f"El grado {curso_sel} no tiene materias vinculadas.")

    with col_f:
        st.markdown("**➕ Asignar Asignatura a Docente:**")
        with st.form(f"form_asignar_doc_materia_{curso_sel}", clear_on_submit=True):
            materia_nom = st.selectbox("Asignatura:", materias_filtradas, key=f"asig_sel_{curso_sel}")
            
            lista_doc_ids = list(docentes.keys())
            doc_id = st.selectbox(
                "Docente Responsable:",
                lista_doc_ids,
                format_func=lambda x: f"{docentes.get(x)} ({x})",
                key=f"doc_sel_{curso_sel}"
            )
            
            if st.form_submit_button("💾 Guardar Carga Académica", type="primary", use_container_width=True):
                requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=eq.{materia_nom}", headers=headers)
                data_ins = {
                    "curso": curso_sel,
                    "asignatura": materia_nom,
                    "documento_docente": doc_id,
                    "anio": datetime.now().year
                }
                r_post = requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data_ins)
                if r_post.status_code == 201:
                    st.success(f"✅ {materia_nom} asignada a {docentes.get(doc_id, doc_id)}")
                    st.rerun()
                else:
                    st.error(f"Error al guardar: {r_post.text}")

# ==============================================================================
# GESTIÓN ACADÉMICA: ASIGNATURAS & CURSOS
# ==============================================================================
def gestionar_asignaturas():
    st.subheader("📚 Gestión de Asignaturas y Pénsum")
    headers = get_headers()
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    nivel_nombres = [n['nombre'] for n in niveles]
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    id_a_nivel = {n['id']: n['nombre'] for n in niveles}

    r_materias = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
    materias = r_materias.json() if r_materias.status_code == 200 else []

    r_rel = requests.get(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers)
    relaciones = r_rel.json() if r_rel.status_code == 200 else []

    niveles_por_materia = {}
    for r in relaciones:
        m_id = r.get('materia_id')
        n_id = r.get('nivel_id')
        if m_id and n_id in id_a_nivel:
            niveles_por_materia.setdefault(m_id, []).append(id_a_nivel[n_id])

    col_tabla, col_form = st.columns([1.2, 1.1], gap="medium")

    with col_tabla:
        st.markdown("**📋 Pénsum Institucional (Materias y Niveles Asignados)**")
        if materias:
            datos_mat = []
            for m in materias:
                nivs = ", ".join(niveles_por_materia.get(m['id'], [])) or "⚠️ Sin nivel"
                datos_mat.append({
                    "Asignatura": m.get('nombre'),
                    "Código": m.get('codigo') or "-",
                    "Niveles": nivs
                })
            df_mat = pd.DataFrame(datos_mat)
            st.dataframe(df_mat[['Asignatura', 'Código', 'Niveles']], use_container_width=True, height=330)
            st.caption(f"Total: {len(materias)} asignaturas registradas")
        else:
            st.info("No hay asignaturas registradas.")

    with col_form:
        subtab_edit, subtab_new = st.tabs(["✏️ Modificar / Eliminar", "➕ Nueva Asignatura"])

        with subtab_edit:
            if materias:
                mat_opciones = {m['id']: f"{m['nombre']} ({m.get('codigo') or 'Sin código'})" for m in materias}
                materia_sel_id = st.selectbox(
                    "Selecciona la asignatura a editar:",
                    options=list(mat_opciones.keys()),
                    format_func=lambda x: mat_opciones[x],
                    key="asig_edit_sel"
                )

                materia_actual = next((m for m in materias if m['id'] == materia_sel_id), None)
                niveles_actuales = [n for n in niveles_por_materia.get(materia_sel_id, []) if n in nivel_nombres]

                if materia_actual:
                    with st.form(f"form_edit_materia_{materia_sel_id}"):
                        nuevo_nom_mat = st.text_input("Nombre de la asignatura *", value=materia_actual.get('nombre', ''))
                        nuevo_cod_mat = st.text_input("Código / Abreviatura", value=materia_actual.get('codigo') or '')
                        nuevos_niveles_sel = st.multiselect(
                            "Niveles donde aplica esta asignatura *",
                            options=nivel_nombres,
                            default=niveles_actuales
                        )

                        if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                            if not nuevo_nom_mat:
                                st.error("❌ El nombre es obligatorio")
                            else:
                                payload_mat = {
                                    "nombre": nuevo_nom_mat.upper().strip(),
                                    "codigo": nuevo_cod_mat.upper().strip() if nuevo_cod_mat else None
                                }
                                requests.patch(f"{SUPABASE_URL}/rest/v1/materias?id=eq.{materia_sel_id}", headers=headers, json=payload_mat)

                                requests.delete(f"{SUPABASE_URL}/rest/v1/materias_niveles?materia_id=eq.{materia_sel_id}", headers=headers)
                                for n_nom in nuevos_niveles_sel:
                                    n_id = niveles_dict.get(n_nom)
                                    if n_id:
                                        requests.post(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers, json={"materia_id": materia_sel_id, "nivel_id": n_id})

                                st.success("✅ Asignatura actualizada")
                                st.rerun()

                    if st.button("🗑️ Eliminar esta asignatura", key=f"del_mat_btn_{materia_sel_id}", use_container_width=True):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/materias_niveles?materia_id=eq.{materia_sel_id}", headers=headers)
                        requests.delete(f"{SUPABASE_URL}/rest/v1/materias?id=eq.{materia_sel_id}", headers=headers)
                        st.warning("Asignatura eliminada")
                        st.rerun()
            else:
                st.info("Crea una asignatura primero.")

        with subtab_new:
            with st.form("form_nueva_materia", clear_on_submit=True):
                nombre_mat = st.text_input("Nombre de la asignatura (Ej: ALGEBRA) *")
                codigo_mat = st.text_input("Código (Ej: ALG-08)")
                niveles_sel = st.multiselect("Niveles donde se dicta *", nivel_nombres)

                if st.form_submit_button("💾 Crear Asignatura", type="primary", use_container_width=True):
                    if not nombre_mat:
                        st.error("❌ El nombre es obligatorio")
                    else:
                        data = {"nombre": nombre_mat.upper().strip(), "codigo": codigo_mat.upper().strip() if codigo_mat else None}
                        r = requests.post(f"{SUPABASE_URL}/rest/v1/materias", headers=headers, json=data)
                        if r.status_code == 201:
                            m_id = r.json()[0]['id']
                            for n_nom in niveles_sel:
                                requests.post(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers, json={"materia_id": m_id, "nivel_id": niveles_dict.get(n_nom)})
                            st.success(f"✅ Asignatura {nombre_mat} creada")
                            st.rerun()
                        else:
                            st.error(f"Error: {r.text}")

def gestionar_grados():
    st.subheader("🏫 Gestión de Cursos y Salones")
    headers = get_headers()
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    nivel_nombres = [n['nombre'] for n in niveles]
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    id_a_nivel = {n['id']: n['nombre'] for n in niveles}

    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    grados = r_grados.json() if r_grados.status_code == 200 else []

    col_tabla, col_form = st.columns([1.2, 1.1], gap="medium")

    with col_tabla:
        st.markdown("**📋 Salones y Cursos Activos**")
        if grados:
            data = []
            for g in grados:
                n_nombre = id_a_nivel.get(g.get('nivel_id'), "Sin nivel")
                data.append({"Curso / Salón": g.get('curso'), "Nivel Educativo": n_nombre})
            st.dataframe(pd.DataFrame(data), use_container_width=True, height=310)
        else:
            st.info("No hay cursos registrados.")

    with col_form:
        subtab_edit_c, subtab_new_c = st.tabs(["✏️ Modificar / Eliminar", "➕ Nuevo Curso"])

        with subtab_edit_c:
            if grados:
                cursos_nombres = [g['curso'] for g in grados if g.get('curso')]
                cur_sel = st.selectbox("Seleccionar curso a editar:", cursos_nombres, key="cur_sel_edit")
                grado_actual = next((g for g in grados if g.get('curso') == cur_sel), None)

                if grado_actual:
                    nivel_actual_id = grado_actual.get('nivel_id')
                    nivel_actual_nom = id_a_nivel.get(nivel_actual_id, nivel_nombres[0] if nivel_nombres else "")
                    idx_nivel = nivel_nombres.index(nivel_actual_nom) if nivel_actual_nom in nivel_nombres else 0

                    with st.form(f"form_edit_curso_{cur_sel}"):
                        nuevo_nom_cur = st.text_input("Nombre del Curso *", value=grado_actual.get('curso', ''))
                        nuevo_nivel_cur = st.selectbox("Nivel Educativo *", options=nivel_nombres, index=idx_nivel)

                        if st.form_submit_button("💾 Actualizar Curso", type="primary", use_container_width=True):
                            if not nuevo_nom_cur:
                                st.error("❌ El nombre es obligatorio")
                            else:
                                payload = {
                                    "curso": nuevo_nom_cur.upper().strip(),
                                    "nivel_id": niveles_dict.get(nuevo_nivel_cur)
                                }
                                if grado_actual.get('id_grado'):
                                    url_p = f"{SUPABASE_URL}/rest/v1/grados?id_grado=eq.{grado_actual.get('id_grado')}"
                                else:
                                    url_p = f"{SUPABASE_URL}/rest/v1/grados?curso=eq.{cur_sel}"
                                requests.patch(url_p, headers=headers, json=payload)
                                st.success("✅ Curso actualizado")
                                st.rerun()

                    if st.button("🗑️ Eliminar este curso", key=f"btn_del_cur_{cur_sel}", use_container_width=True):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/grados?curso=eq.{cur_sel}", headers=headers)
                        st.warning(f"Curso {cur_sel} eliminado")
                        st.rerun()
            else:
                st.info("Crea un curso primero.")

        with subtab_new_c:
            with st.form("form_nuevo_grado", clear_on_submit=True):
                nombre_cur = st.text_input("Nombre del Salón (Ej: 801, 1002) *")
                nivel_cur = st.selectbox("Nivel Educativo *", nivel_nombres if nivel_nombres else ["General"])

                if st.form_submit_button("💾 Guardar Curso", type="primary", use_container_width=True):
                    if nombre_cur:
                        data = {"curso": nombre_cur.upper().strip(), "nivel_id": niveles_dict.get(nivel_cur)}
                        requests.post(f"{SUPABASE_URL}/rest/v1/grados", headers=headers, json=data)
                        st.success(f"✅ Curso {nombre_cur} creado")
                        st.rerun()

# ==============================================================================
# ENLACES CON MÓDULOS DE HORARIOS Y COMUNIDAD
# ==============================================================================
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
    st.info("Colegio de Prueba - Plataforma Escolar 2026")

def reportes_academicos():
    st.subheader("📊 Reportes Académicos")
    st.info("Módulo de consolidación y reportes.")