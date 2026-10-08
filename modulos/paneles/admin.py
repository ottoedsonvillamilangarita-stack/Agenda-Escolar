# ==============================================================================
# modulos/paneles/admin.py - PANEL ADMINISTRADOR
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils import SUPABASE_URL, get_headers

import modulos.features.horarios as horarios_feature

# ============================================
# CONSTANTES
# ============================================
CURSOS = ["901", "902", "903", "1001", "1002", "1003", "1101"]
DIAS_SEMANA = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
PARENTESCOS = ["Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Tutor Legal", "Otro"]
SEXOS = ["", "Masculino", "Femenino"]
TIPOS_CONTRATO = ["", "Planta", "Contrato", "Cátedra", "Ocasional"]

# ============================================
# VISTA PRINCIPAL: DASHBOARD ADMIN
# ============================================
def mostrar(data):
    headers = get_headers()
    
    st.markdown("""
    <div style="background: white; padding: 18px 22px; border-radius: 12px; border: 1px solid #E2E8F0; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="width: 50px; height: 50px; background: linear-gradient(135deg, #1E3A8A, #3B82F6); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: white;">
                🏫
            </div>
            <div>
                <h2 style="margin: 0; font-size: 19px; font-weight: 700; color: #0F172A;">COLEGIO DE PRUEBA</h2>
                <p style="margin: 2px 0 0 0; font-size: 12.5px; color: #64748B; font-style: italic;">"Preparando gente para el futuro"</p>
            </div>
        </div>
        <div style="text-align: right;">
            <span style="background: #DCFCE7; color: #166534; font-size: 11.5px; font-weight: 600; padding: 4px 9px; border-radius: 16px;">🟢 Sistema Activo</span>
            <span style="background: #EEF2F6; color: #334155; font-size: 11.5px; font-weight: 600; padding: 4px 9px; border-radius: 16px; margin-left: 6px;">📅 Año 2026</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        r_cur = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=id_grado", headers=headers)
        total_cursos = len(r_cur.json()) if r_cur.status_code == 200 and r_cur.json() else len(CURSOS)
    except Exception:
        total_cursos = len(CURSOS)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style="background: white; padding: 16px; border-radius: 10px; border: 1px solid #E2E8F0;">
            <div style="font-size: 10.5px; text-transform: uppercase; color: #64748B; font-weight: 700;">👨‍🎓 Estudiantes</div>
            <div style="font-size: 26px; font-weight: 700; color: #0F172A; margin: 3px 0;">{total_estudiantes}</div>
            <div style="font-size: 11px; color: #16A34A; font-weight: 600;">Matriculados activos</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: white; padding: 16px; border-radius: 10px; border: 1px solid #E2E8F0;">
            <div style="font-size: 10.5px; text-transform: uppercase; color: #64748B; font-weight: 700;">👨‍🏫 Docentes</div>
            <div style="font-size: 26px; font-weight: 700; color: #0F172A; margin: 3px 0;">{total_docentes}</div>
            <div style="font-size: 11px; color: #2563EB; font-weight: 600;">Planta vinculada</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 10px; border: 1px solid #E2E8F0;">
            <div style="font-size: 10.5px; text-transform: uppercase; color: #64748B; font-weight: 700;">📚 Cursos / Grados</div>
            <div style="font-size: 26px; font-weight: 700; color: #0F172A; margin: 3px 0;">{total_cursos}</div>
            <div style="font-size: 11px; color: #8B5CF6; font-weight: 600;">Registrados en sede</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: white; padding: 16px; border-radius: 10px; border: 1px solid #E2E8F0;">
            <div style="font-size: 10.5px; text-transform: uppercase; color: #64748B; font-weight: 700;">👨‍👩‍👧 Familias</div>
            <div style="font-size: 26px; font-weight: 700; color: #0F172A; margin: 3px 0;">189+</div>
            <div style="font-size: 11px; color: #EA580C; font-weight: 600;">Acudientes activos</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    col_izq, col_der = st.columns([2, 1])
    with col_izq:
        st.subheader("📢 Agenda & Novedades Institucionales")
        st.info("ℹ️ **Cierre de Período Académico:** Verifique que los docentes completen la consolidación de notas y porcentajes.")
        st.warning("⚠️ **Excusas Pendientes:** Los acudientes han radicado justificaciones médicas que requieren visto bueno.")

    with col_der:
        st.subheader("⚡ Acceso Rápido")
        st.write("• **👥 Comunidad Escolar:** Registro y consulta de estudiantes y docentes.")
        st.write("• **📚 Gestión Académica:** Pénsum, asignaturas y dirección de grupo.")
        st.write("• **⏰ Horarios:** Franjas horarias y cronogramas semanales.")


# ============================================
# GESTIÓN DE ESTUDIANTES & NÚCLEO FAMILIAR
# ============================================
def gestion_estudiantes():
    st.subheader("👨‍🎓 Gestión de Estudiantes y Familias")
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Directorio de Alumnos", "➕ Matricular Estudiante", "✏️ Ficha del Estudiante & Familia"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
            if response.status_code == 200:
                estudiantes = response.json()
                if estudiantes:
                    df = pd.DataFrame(estudiantes)
                    if 'estado' not in df.columns:
                        df['estado'] = 'Activo'
                    else:
                        df['estado'] = df['estado'].fillna('Activo').replace('', 'Activo')

                    cursos_reales = sorted([str(c) for c in df['curso'].dropna().unique()]) if 'curso' in df.columns else CURSOS

                    c_f1, c_f2, c_f3 = st.columns([1.5, 1.5, 2])
                    with c_f1:
                        filtro_estado = st.selectbox("Estado:", ["Todos", "Activo", "Retirado", "Graduado"], index=0)
                    with c_f2:
                        filtro_curso = st.selectbox("Curso:", ["Todos"] + cursos_reales, index=0)
                    with c_f3:
                        busq_nombre = st.text_input("Buscar alumno:", placeholder="Nombre o documento...")

                    df_filtrado = df.copy()
                    if filtro_estado != "Todos":
                        df_filtrado = df_filtrado[df_filtrado['estado'].astype(str).str.lower() == filtro_estado.lower()]
                    if filtro_curso != "Todos":
                        df_filtrado = df_filtrado[df_filtrado['curso'].astype(str) == str(filtro_curso)]
                    if busq_nombre:
                        b = busq_nombre.lower()
                        mascara = (
                            df_filtrado['nombre_estudiante'].astype(str).str.lower().str.contains(b, na=False) |
                            df_filtrado['apellidos_estudiante'].astype(str).str.lower().str.contains(b, na=False) |
                            df_filtrado['documento_estudiante'].astype(str).str.contains(b, na=False)
                        )
                        df_filtrado = df_filtrado[mascara]

                    if 'curso' in df_filtrado.columns and 'apellidos_estudiante' in df_filtrado.columns:
                        df_filtrado = df_filtrado.sort_values(by=['curso', 'apellidos_estudiante'])

                    cols_preferidas = ['documento_estudiante', 'nombre_estudiante', 'apellidos_estudiante', 'curso', 'estado', 'telefono_acudiente', 'email_acudiente']
                    cols_finales = [c for c in cols_preferidas if c in df_filtrado.columns]
                    
                    df_mostrar = df_filtrado[cols_finales].copy()
                    df_mostrar.columns = [c.replace('_estudiante', '').capitalize() for c in df_mostrar.columns]

                    st.dataframe(df_mostrar, use_container_width=True, height=360)
                    st.caption(f"Mostrando **{len(df_mostrar)}** de **{len(df)}** alumnos registrados")
                else:
                    st.info("No hay estudiantes registrados.")
            else:
                st.error(f"Error ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"Error al cargar estudiantes: {str(e)}")
    
    with tab2:
        st.write("**Formulario de Matrícula y Acudiente Inicial**")
        with st.form("nuevo_estudiante", clear_on_submit=True):
            c_est, c_acu = st.columns(2)
            with c_est:
                st.markdown("##### 👤 Datos del Alumno")
                nombre = st.text_input("Nombre(s) *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de Identidad *")
                curso = st.selectbox("Curso a matricular *", CURSOS)
            with c_acu:
                st.markdown("##### 👨‍👩‍👧 Acudiente Principal")
                nombre_acudiente = st.text_input("Nombre completo acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco *", PARENTESCOS)
                telefono_acudiente = st.text_input("Teléfono acudiente")
                email_acudiente = st.text_input("Correo acudiente (notificaciones)")
            
            if st.form_submit_button("💾 Completar Matrícula", type="primary", use_container_width=True):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                    st.error("❌ Completa los campos obligatorios (*)")
                else:
                    check_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
                    check_res = requests.get(check_url, headers=headers)
                    if check_res.status_code == 200 and check_res.json():
                        st.error(f"❌ Ya existe un alumno registrado con el documento {documento}")
                    else:
                        data_est = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "documento_estudiante": documento,
                            "curso": curso,
                            "estado": "Activo",
                            "nombre_acudiente": nombre_acudiente,
                            "documento_acudiente": documento_acudiente,
                            "parentesco": parentesco,
                            "telefono_acudiente": telefono_acudiente,
                            "email_acudiente": email_acudiente
                        }
                        res_est = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data_est)
                        if res_est.status_code == 201:
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json={
                                "username": documento, "password_hash": "demo2026", "rol": "estudiante", "documento": documento, "roles": ["estudiante"]
                            })
                            requests.post(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers, json={
                                "documento_estudiante": documento, "documento_acudiente": documento_acudiente,
                                "nombre_acudiente": nombre_acudiente, "parentesco": parentesco,
                                "telefono_acudiente": telefono_acudiente, "email_acudiente": email_acudiente, "es_principal": True
                            })
                            requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json={
                                "username": documento_acudiente, "password_hash": "demo2026", "rol": "acudiente", "documento": documento_acudiente, "roles": ["acudiente"]
                            })
                            st.success(f"✅ Alumno {nombre} {apellidos} matriculado exitosamente")
                            st.rerun()
                        else:
                            st.error(f"Error al matricular: {res_est.status_code}")

    with tab3:
        col_b1, _ = st.columns([3, 1])
        with col_b1:
            documento_buscar = st.text_input("🔍 Buscar expediente por documento:", placeholder="Ingresa documento y presiona Enter", key="buscar_est_integral")
        
        if documento_buscar:
            url_est = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
            res_est = requests.get(url_est, headers=headers)
            
            if res_est.status_code == 200 and res_est.json():
                estudiante = res_est.json()[0]
                estado_actual = estudiante.get('estado', 'Activo')
                
                col_izq, col_der = st.columns([1, 1], gap="medium")
                
                with col_izq:
                    color_estado = "#16A34A" if estado_actual == "Activo" else "#DC2626"
                    bg_estado = "#DCFCE7" if estado_actual == "Activo" else "#FEE2E2"
                    
                    st.markdown(f"""
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <b style="color: #0F172A; font-size: 13.5px;">👤 Datos del Alumno</b>
                        <span style="font-size: 11px; font-weight: 700; color: {color_estado}; background: {bg_estado}; padding: 2px 7px; border-radius: 6px;">
                            {estado_actual.upper()}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form("form_editar_alumno"):
                        c1, c2 = st.columns(2)
                        with c1:
                            nombre_upd = st.text_input("Nombre(s)", value=estudiante.get('nombre_estudiante', ''))
                        with c2:
                            apellidos_upd = st.text_input("Apellidos", value=estudiante.get('apellidos_estudiante', ''))
                            
                        c3, c4 = st.columns(2)
                        with c3:
                            curso_actual = estudiante.get('curso', '901')
                            curso_idx = CURSOS.index(curso_actual) if curso_actual in CURSOS else 0
                            curso_upd = st.selectbox("Curso", CURSOS, index=curso_idx)
                        with c4:
                            estados_disp = ["Activo", "Retirado", "Graduado"]
                            est_idx = estados_disp.index(estado_actual) if estado_actual in estados_disp else 0
                            estado_upd = st.selectbox("Estado", estados_disp, index=est_idx)
                            
                        if st.form_submit_button("💾 Guardar Cambios Alumno", type="primary", use_container_width=True):
                            payload = {
                                "nombre_estudiante": nombre_upd,
                                "apellidos_estudiante": apellidos_upd,
                                "curso": curso_upd,
                                "estado": estado_upd
                            }
                            r_upd_est = requests.patch(f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}", headers=headers, json=payload)
                            if r_upd_est.status_code in [200, 204]:
                                st.success("✅ Alumno actualizado")
                                st.rerun()
                            else:
                                st.error(f"Error: {r_upd_est.text}")

                with col_der:
                    st.markdown("""
                    <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
                        <b style="color: #0F172A; font-size: 13.5px;">👨‍👩‍👧 Acudientes Vinculados</b>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    url_acuds = f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_estudiante=eq.{documento_buscar}"
                    res_acuds = requests.get(url_acuds, headers=headers)
                    acudientes = res_acuds.json() if res_acuds.status_code == 200 else []

                    if acudientes:
                        for idx, acud in enumerate(acudientes):
                            es_princ = acud.get('es_principal', False)
                            doc_acud = acud.get('documento_acudiente')
                            borde = "#2563EB" if es_princ else "#CBD5E1"
                            fondo_badge = "#DBEAFE" if es_princ else "#F1F5F9"
                            texto_badge = "#1D4ED8" if es_princ else "#64748B"
                            
                            st.markdown(f"""
                            <div style="background: white; border: 1.5px solid {borde}; border-radius: 8px; padding: 9px 12px; margin-bottom: 6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 13px; font-weight: 700; color: #0F172A;">{acud.get('nombre_acudiente')} ({acud.get('parentesco', 'Tutor')})</span>
                                    <span style="font-size: 9.5px; font-weight: 700; color: {texto_badge}; background: {fondo_badge}; padding: 2px 6px; border-radius: 4px;">
                                        {'⭐ PRINCIPAL' if es_princ else 'Secundario'}
                                    </span>
                                </div>
                                <div style="font-size: 11px; color: #475569; margin-top: 3px;">
                                    📄 Doc: <b>{doc_acud}</b> | 📞 {acud.get('telefono_acudiente') or 'Sin tel'} | ✉️ {acud.get('email_acudiente') or 'Sin correo'}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("Sin acudientes vinculados.")
            else:
                st.warning("🔍 No se encontró ningún estudiante con ese documento.")


# ============================================
# GESTIÓN DE DOCENTES
# ============================================
def gestion_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Planta Docente", "➕ Registrar Docente", "✏️ Editar Docente"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?order=apellidos_docente.asc", headers=headers)
            if response.status_code == 200:
                docentes = response.json()
                if docentes:
                    df = pd.DataFrame(docentes)
                    cols = ['documento_docente', 'nombre_docente', 'apellidos_docente', 'titulo', 'tipo_contrato', 'telefono_docente', 'email_docente']
                    df_final = df[[c for c in cols if c in df.columns]]
                    df_final.columns = [c.replace('_docente', '').capitalize() for c in df_final.columns]
                    st.dataframe(df_final, use_container_width=True, height=360)
                    st.caption(f"Total docentes: {len(docentes)}")
                else:
                    st.info("No hay docentes registrados.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.write("**Registrar nuevo docente**")
        with st.form("nuevo_docente", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre(s) *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de identidad *")
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                sexo = st.selectbox("Sexo", SEXOS)
            with col2:
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
                titulo = st.text_input("Título profesional")
                tipo_contrato = st.selectbox("Tipo de contrato", TIPOS_CONTRATO)
                fecha_ingreso = st.date_input("Fecha de ingreso", value=None)
            
            if st.form_submit_button("💾 Guardar Docente", type="primary", use_container_width=True):
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
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers
