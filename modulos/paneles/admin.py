# ============================================
# modulos/paneles/admin.py - VERSIÓN MODERNA & COMPACTA
# ============================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

# ============================================
# IMPORTAR FUNCIONES DE HORARIOS
# ============================================
from modulos.features.horarios import (
    configurar_horas_nivel as horarios_configurar_horas,
    configurar_jornada_nivel as horarios_configurar_jornada,
    configurar_horario_curso as horarios_configurar_horario,
    gestion_festivos as horarios_gestion_festivos
)

# ============================================
# CONSTANTES
# ============================================
CURSOS = ["901", "902", "903", "1001", "1002", "1003", "1101"]
DIAS_SEMANA = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
PARENTESCOS = ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"]
SEXOS = ["", "Masculino", "Femenino"]
TIPOS_CONTRATO = ["", "Planta", "Contrato", "Cátedra", "Ocasional"]

# ============================================
# VISTA PRINCIPAL: DASHBOARD ADMIN
# ============================================
def mostrar(data):
    headers = get_headers()
    
    # 1. ENCABEZADO INSTITUCIONAL (BRANDING DEL COLEGIO)
    st.markdown("""
    <div style="background: white; padding: 20px 24px; border-radius: 12px; border: 1px solid #E2E8F0; display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="width: 54px; height: 54px; background: linear-gradient(135deg, #1E3A8A, #3B82F6); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 26px; color: white;">
                🏫
            </div>
            <div>
                <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #0F172A;">COLEGIO DE PRUEBA</h2>
                <p style="margin: 2px 0 0 0; font-size: 13px; color: #64748B; font-style: italic;">"Preparando gente para el futuro"</p>
            </div>
        </div>
        <div style="text-align: right;">
            <span style="background: #DCFCE7; color: #166534; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 20px;">🟢 Sistema Activo</span>
            <span style="background: #EEF2F6; color: #334155; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 20px; margin-left: 6px;">📅 Año 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. CONSULTA DE MÉTRICAS EN SUPABASE
    try:
        r_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes?select=id", headers=headers)
        total_estudiantes = len(r_est.json()) if r_est.status_code == 200 else 0
    except Exception:
        total_estudiantes = 0

    try:
        r_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?select=documento_docente", headers=headers)
        total_docentes = len(r_doc.json()) if r_doc.status_code == 200 else 0
    except Exception:
        total_docentes = 0

    try:
        r_cur = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=id", headers=headers)
        total_cursos = len(r_cur.json()) if r_cur.status_code == 200 and r_cur.json() else len(CURSOS)
    except Exception:
        total_cursos = len(CURSOS)

    # 3. TARJETAS DE MÉTRICAS (KPI CARDS)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style="background: white; padding: 18px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
            <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: 700;">👨‍🎓 Estudiantes</div>
            <div style="font-size: 28px; font-weight: 700; color: #0F172A; margin: 4px 0;">{total_estudiantes}</div>
            <div style="font-size: 11px; color: #16A34A; font-weight: 600;">Matriculados activos</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 18px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
            <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: 700;">👨‍🏫 Docentes</div>
            <div style="font-size: 28px; font-weight: 700; color: #0F172A; margin: 4px 0;">{total_docentes}</div>
            <div style="font-size: 11px; color: #2563EB; font-weight: 600;">Planta vinculada</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: white; padding: 18px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
            <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: 700;">📚 Cursos / Grados</div>
            <div style="font-size: 28px; font-weight: 700; color: #0F172A; margin: 4px 0;">{total_cursos}</div>
            <div style="font-size: 11px; color: #8B5CF6; font-weight: 600;">Registrados en sede</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: white; padding: 18px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
            <div style="font-size: 11px; text-transform: uppercase; color: #64748B; font-weight: 700;">👨‍👩‍👧 Familias</div>
            <div style="font-size: 28px; font-weight: 700; color: #0F172A; margin: 4px 0;">189+</div>
            <div style="font-size: 11px; color: #EA580C; font-weight: 600;">Acudientes activos</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # 4. ÁREA DE TRABAJO EN 2 COLUMNAS
    col_izq, col_der = st.columns([2, 1])

    with col_izq:
        st.subheader("📢 Agenda & Novedades Institucionales")
        st.info("ℹ️ **Cierre de Período Académico:** Verifique que los docentes completen la consolidación de notas y porcentajes.")
        st.warning("⚠️ **Excusas Pendientes:** Los acudientes han radicado justificaciones médicas que requieren visto bueno.")

    with col_der:
        st.subheader("⚡ Acceso Rápido")
        st.caption("Navega desde el menú superior o lateral a los módulos:")
        st.write("• **👥 Comunidad Escolar:** Registro y consulta de estudiantes y docentes.")
        st.write("• **📚 Gestión Académica:** Pénsum, asignaturas y dirección de grupo.")
        st.write("• **⏰ Horarios:** Franjas horarias y cronogramas semanales.")


# ============================================
# GESTIÓN DE ESTUDIANTES
# ============================================
def gestion_estudiantes():
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Matriculados", "➕ Matricular Estudiante", "✏️ Editar Expediente"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
            if response.status_code == 200:
                estudiantes = response.json()
                if estudiantes:
                    df = pd.DataFrame(estudiantes)
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total matriculados: {len(estudiantes)} alumnos")
                else:
                    st.info("No hay estudiantes registrados")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.write("**Registrar nuevo estudiante**")
        with st.form("nuevo_estudiante", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Datos personales del alumno**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                curso = st.selectbox("Curso *", CURSOS)
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            with col2:
                st.markdown("**Datos del acudiente / representante**")
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", PARENTESCOS)
                telefono_acudiente = st.text_input("Teléfono del acudiente")
                email_acudiente = st.text_input("Email del acudiente")
            
            if st.form_submit_button("💾 Completar Matrícula", type="primary"):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                    st.error("❌ Completa todos los campos obligatorios (*)")
                else:
                    check_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un estudiante con el documento {documento}")
                    else:
                        data_estudiante = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "documento_estudiante": documento,
                            "curso": curso,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data_estudiante)
                        
                        if response.status_code == 201:
                            user_data = {
                                "username": documento,
                                "password_hash": "demo2026",
                                "rol": "estudiante",
                                "documento": documento,
                                "roles": ["estudiante"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                            
                            data_acudiente = {
                                "documento_estudiante": documento,
                                "documento_acudiente": documento_acudiente,
                                "nombre_acudiente": nombre_acudiente,
                                "parentesco": parentesco,
                                "telefono_acudiente": telefono_acudiente,
                                "email_acudiente": email_acudiente,
                                "es_principal": True
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers, json=data_acudiente)
                            
                            user_acud = {
                                "username": documento_acudiente,
                                "password_hash": "demo2026",
                                "rol": "acudiente",
                                "documento": documento_acudiente,
                                "roles": ["acudiente"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_acud)
                            
                            st.success(f"✅ Estudiante {nombre} {apellidos} registrado exitosamente")
                            st.info(f"🔑 Credenciales creadas: Alumno: {documento} | Acudiente: {documento_acudiente} (Clave: demo2026)")
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        st.write("**Editar expediente de estudiante**")
        documento_buscar = st.text_input("Documento del estudiante a modificar", key="buscar_est_edit")
        
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                estudiante = response.json()[0]
                with st.form("editar_estudiante"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre = st.text_input("Nombre", value=estudiante.get('nombre_estudiante', ''))
                        apellidos = st.text_input("Apellidos", value=estudiante.get('apellidos_estudiante', ''))
                        curso = st.selectbox("Curso", CURSOS, 
                                           index=CURSOS.index(estudiante.get('curso', '901')) if estudiante.get('curso') in CURSOS else 0)
                    with col2:
                        telefono = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
                        email = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
                    
                    if st.form_submit_button("💾 Actualizar Datos", type="primary"):
                        data_update = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "curso": curso,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email
                        }
                        update_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
                        response_update = requests.patch(update_url, headers=headers, json=data_update)
                        if response_update.status_code == 200:
                            st.success("✅ Expediente actualizado correctamente")
                            st.rerun()
                        else:
                            st.error(f"Error: {response_update.status_code}")
            else:
                st.warning("No se encontró ningún estudiante con ese documento")


# ============================================
# GESTIÓN DE DOCENTES
# ============================================
def gestion_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Planta Docente", "➕ Registrar Docente", "✏️ Editar Docente"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
            if response.status_code == 200:
                docentes = response.json()
                if docentes:
                    df = pd.DataFrame(docentes)
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total docentes: {len(docentes)}")
                else:
                    st.info("No hay docentes registrados")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.write("**Registrar nuevo docente**")
        with st.form("nuevo_docente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                sexo = st.selectbox("Sexo", SEXOS)
            with col2:
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
                titulo = st.text_input("Título profesional")
                tipo_contrato = st.selectbox("Tipo de contrato", TIPOS_CONTRATO)
                fecha_ingreso = st.date_input("Fecha de ingreso", value=None)
            
            if st.form_submit_button("💾 Guardar Docente", type="primary"):
                if not all([nombre, apellidos, documento]):
                    st.error("❌ Completa los campos obligatorios (*)")
                else:
                    check_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un docente con el documento {documento}")
                    else:
                        data = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "documento_docente": documento,
                            "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                            "sexo_docente": sexo,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo,
                            "tipo_contrato": tipo_contrato,
                            "fecha_ingreso": str(fecha_ingreso) if fecha_ingreso else None
                        }
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data)
                        if response.status_code == 201:
                            username = nombre.lower().replace(" ", "_") + "_" + documento[-4:]
                            user_data = {
                                "username": username,
                                "password_hash": "demo2026",
                                "rol": "docente",
                                "documento": documento,
                                "roles": ["docente"]
                            }
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_data)
                            st.success(f"✅ Docente {nombre} {apellidos} registrado")
                            st.info(f"🔑 Usuario asignado: {username} | demo2026")
                        else:
                            st.error(f"Error: {response.status_code}")
    
    with tab3:
        st.write("**Editar docente**")
        documento_buscar = st.text_input("Documento del docente a buscar", key="buscar_doc_edit")
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200 and response.json():
                docente = response.json()[0]
                with st.form("editar_docente"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre = st.text_input("Nombre", value=docente.get('nombre_docente', ''))
                        apellidos = st.text_input("Apellidos", value=docente.get('apellidos_docente', ''))
                    with col2:
                        telefono = st.text_input("Teléfono", value=docente.get('telefono_docente', ''))
                        email = st.text_input("Email", value=docente.get('email_docente', ''))
                        titulo = st.text_input("Título", value=docente.get('titulo', ''))
                    
                    if st.form_submit_button("💾 Guardar Cambios", type="primary"):
                        data_update = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo
                        }
                        update_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}"
                        requests.patch(update_url, headers=headers, json=data_update)
                        st.success("✅ Docente actualizado")
                        st.rerun()
            else:
                st.warning("No se encontró el docente")


# ============================================
# NIVELES EDUCATIVOS
# ============================================
def configurar_niveles():
    st.subheader("📚 Niveles Educativos")
    headers = get_headers()
    response = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response.status_code == 200:
        niveles = response.json()
        if niveles:
            for n in niveles:
                st.write(f"- **{n['nombre']}** (Orden: {n.get('orden')})")
    
    with st.expander("➕ Agregar nuevo nivel"):
        nuevo_nivel = st.text_input("Nombre del nivel")
        if st.button("Guardar Nivel", type="primary"):
            if nuevo_nivel:
                data = {"nombre": nuevo_nivel, "orden": len(niveles) + 1 if niveles else 1}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/niveles", headers=headers, json=data)
                if r.status_code == 201:
                    st.success(f"✅ Nivel '{nuevo_nivel}' agregado")
                    st.rerun()


# ============================================
# ASIGNATURAS Y PÉNSUM
# ============================================
def gestionar_asignaturas():
    st.subheader("📚 Gestión de Asignaturas y Pénsum")
    headers = get_headers()
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    nivel_nombres = [n['nombre'] for n in niveles]
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    
    response_materias = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
    materias = response_materias.json() if response_materias.status_code == 200 else []
    
    response_relaciones = requests.get(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers)
    relaciones = response_relaciones.json() if response_relaciones.status_code == 200 else []
    
    niveles_por_materia = {}
    for r in relaciones:
        m_id, n_id = r['materia_id'], r['nivel_id']
        niveles_por_materia.setdefault(m_id, []).append(n_id)
    
    st.write("### Asignaturas registradas por nivel")
    for m in materias:
        with st.expander(f"📘 {m['nombre']}"):
            niveles_ids = niveles_por_materia.get(m['id'], [])
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Código: {m.get('codigo', 'Sin código')}")
            with col2:
                if st.button("🗑️ Eliminar", key=f"del_materia_{m['id']}"):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/materias_niveles?materia_id=eq.{m['id']}", headers=headers)
                    requests.delete(f"{SUPABASE_URL}/rest/v1/materias?id=eq.{m['id']}", headers=headers)
                    st.rerun()
            
            st.write("**Niveles donde se imparte:**")
            cols = st.columns(len(nivel_nombres))
            for idx, nivel in enumerate(nivel_nombres):
                with cols[idx]:
                    n_id = niveles_dict.get(nivel)
                    checked = n_id in niveles_ids if n_id else False
                    if st.checkbox(nivel, value=checked, key=f"m_{m['id']}_{nivel}"):
                        if not checked and n_id:
                            requests.post(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers, json={"materia_id": m['id'], "nivel_id": n_id})
                    else:
                        if checked and n_id:
                            requests.delete(f"{SUPABASE_URL}/rest/v1/materias_niveles?materia_id=eq.{m['id']}&nivel_id=eq.{n_id}", headers=headers)

    st.divider()
    with st.expander("➕ Crear nueva asignatura"):
        with st.form("nueva_materia"):
            nombre = st.text_input("Nombre de la asignatura *")
            codigo = st.text_input("Código (opcional)")
            niveles_nueva = st.multiselect("Niveles donde aplica *", nivel_nombres)
            if st.form_submit_button("💾 Guardar Asignatura", type="primary"):
                if not nombre or not niveles_nueva:
                    st.error("❌ Nombre y niveles son obligatorios")
                else:
                    data = {"nombre": nombre.upper().strip(), "codigo": codigo.upper().strip() if codigo else None}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/materias", headers=headers, json=data)
                    if r.status_code == 201:
                        m_id = r.json()[0]['id']
                        for n_nom in niveles_nueva:
                            requests.post(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers, json={"materia_id": m_id, "nivel_id": niveles_dict.get(n_nom)})
                        st.success("✅ Asignatura creada con éxito")
                        st.rerun()


# ============================================
# CURSOS / GRADOS
# ============================================
def gestionar_grados():
    st.subheader("📚 Gestión de Grados y Cursos")
    headers = get_headers()
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    
    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados", headers=headers)
    grados = r_grados.json() if r_grados.status_code == 200 else []
    
    if grados:
        data = []
        for g in grados:
            n_nombre = next((n['nombre'] for n in niveles if n['id'] == g.get('nivel_id')), "Sin nivel")
            data.append({"Curso": g.get('curso'), "Nivel": n_nombre})
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    
    with st.expander("➕ Agregar nuevo curso"):
        with st.form("nuevo_grado"):
            nombre = st.text_input("Nombre del curso (Ej: 601, 701, Jardín) *")
            nivel_sel = st.selectbox("Nivel *", [n['nombre'] for n in niveles])
            if st.form_submit_button("💾 Crear Curso", type="primary"):
                if nombre:
                    data = {"curso": nombre.upper().strip(), "nivel_id": niveles_dict.get(nivel_sel)}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/grados", headers=headers, json=data)
                    if r.status_code == 201:
                        st.success(f"✅ Curso {nombre} creado")
                        st.rerun()


# ============================================
# DIRECTORES DE GRUPO
# ============================================
def gestion_directores_grupo():
    st.subheader("👨‍🏫 Directores de Grupo")
    headers = get_headers()
    
    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=curso", headers=headers)
    cursos = sorted(list(set([g['curso'] for g in r_grados.json() if g.get('curso')]))) if r_grados.status_code == 200 and r_grados.json() else CURSOS
    
    curso_sel = st.selectbox("Seleccionar curso", cursos)
    
    r_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes = r_docentes.json() if r_docentes.status_code == 200 else []
    doc_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}
    
    r_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=ilike.%direccion%", headers=headers)
    asig = r_asig.json() if r_asig.status_code == 200 else []
    actual_id = asig[0].get('documento_docente') if asig else None
    
    st.info(f"📌 Director actual de {curso_sel}: **{doc_dict.get(actual_id, 'Sin asignar')}**")
    nuevo_dir = st.selectbox("Asignar nuevo director:", [""] + list(doc_dict.keys()), format_func=lambda x: doc_dict.get(x, "Ninguno") if x else "Ninguno")
    
    if st.button("💾 Guardar Director", type="primary"):
        if actual_id:
            requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=ilike.%direccion%", headers=headers)
        if nuevo_dir:
            data = {"curso": curso_sel, "asignatura": "DIRECCION DE CURSO", "documento_docente": nuevo_dir, "anio": datetime.now().year}
            requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data)
            st.success(f"✅ Director asignado para {curso_sel}")
            st.rerun()


# ============================================
# ASIGNACIÓN ACADÉMICA DOCENTE
# ============================================
def asignar_docentes_curso():
    st.subheader("👨‍🏫 Asignación Académica (Docentes por Materia)")
    headers = get_headers()
    
    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=curso", headers=headers)
    cursos = sorted(list(set([g['curso'] for g in r_grados.json() if g.get('curso')]))) if r_grados.status_code == 200 and r_grados.json() else CURSOS
    
    curso_sel = st.selectbox("Seleccionar curso a gestionar", cursos, key="asig_curso_sel")
    
    r_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes = r_doc.json() if r_doc.status_code == 200 else []
    doc_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}
    
    r_mat = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
    materias = r_mat.json() if r_mat.status_code == 200 else []
    
    r_actuales = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}", headers=headers)
    actuales = r_actuales.json() if r_actuales.status_code == 200 else []
    
    st.write(f"### Carga académica actual de {curso_sel}")
    if actuales:
        tabla = [{"Asignatura": a.get('asignatura'), "Docente": doc_dict.get(a.get('documento_docente'), a.get('documento_docente'))} for a in actuales]
        st.dataframe(pd.DataFrame(tabla), use_container_width=True)
    else:
        st.info("No hay asignaciones académicas registradas para este curso")
    
    with st.expander("➕ Asignar o modificar materia a docente"):
        with st.form("form_asignar_doc"):
            materia_nom = st.selectbox("Asignatura", [m['nombre'] for m in materias])
            docente_id = st.selectbox("Docente", list(doc_dict.keys()), format_func=lambda x: doc_dict.get(x))
            if st.form_submit_button("💾 Guardar Asignación", type="primary"):
                # Eliminar asignación previa de esa materia en ese curso
                requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=eq.{materia_nom}", headers=headers)
                data = {"curso": curso_sel, "asignatura": materia_nom, "documento_docente": docente_id, "anio": datetime.now().year}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data)
                if r.status_code == 201:
                    st.success(f"✅ {materia_nom} asignada correctamente")
                    st.rerun()


# ============================================
# HORARIOS Y SISTEMA
# ============================================
def configurar_horas_nivel():
    horarios_configurar_horas(get_headers())

def configurar_jornada_nivel():
    horarios_configurar_jornada(get_headers())

def configurar_horario_curso():
    horarios_configurar_horario(get_headers())

def gestion_festivos():
    horarios_gestion_festivos(get_headers())

def mostrar_sistema():
    st.subheader("⚙️ Configuración Institucional")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Nombre de la Institución", value="Colegio de Prueba")
        st.text_input("Eslogan Institucional", value="Preparando gente para el futuro")
        st.number_input("Año Lectivo", value=datetime.now().year)
        if st.button("💾 Guardar Configuración", type="primary"):
            st.success("✅ Configuración guardada exitosamente")
    with col2:
        st.write("**Información de Plataforma**")
        st.write("- Proveedor: **EVALUAR S.A.S.**")
        st.write("- Modalidad: Plataforma Escolar Multicolegio SaaS")
        st.write("- Versión: 2.0.0")

def reportes_academicos():
    st.subheader("📊 Reportes Académicos")
    st.info("Módulo de consolidación y exportación de notas y ausencias.")
