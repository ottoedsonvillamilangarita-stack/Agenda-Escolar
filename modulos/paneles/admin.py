# ============================================
# modulos/paneles/admin.py - VERSIÓN COMPACTA & ZERO-SCROLL
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
        r_cur = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=id", headers=headers)
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
        <div style="background: white; padding: 16px; border-radius: 10px; border: 1px solid #E2E8F0;">
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

                    cols_preferidas = ['documento_estudiante', 'nombre_estudiante', 'apellidos_estudiante', 'curso', 'estado', 'telefono_estudiante', 'email_estudiante', 'direccion_estudiante']
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
                telefono = st.text_input("Teléfono del estudiante")
                email = st.text_input("Correo electrónico estudiante")
                direccion = st.text_input("Dirección de residencia")
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
                            "telefono_estudiante": telefono,
                            "email_estudiante": email,
                            "direccion_estudiante": direccion
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
                            
                        c5, c6 = st.columns(2)
                        with c5:
                            telefono_upd = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
                        with c6:
                            email_upd = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
                            
                        direccion_upd = st.text_input("Dirección", value=estudiante.get('direccion_estudiante', ''))
                        
                        if st.form_submit_button("💾 Guardar Cambios Alumno", type="primary", use_container_width=True):
                            payload = {
                                "nombre_estudiante": nombre_upd,
                                "apellidos_estudiante": apellidos_upd,
                                "curso": curso_upd,
                                "estado": estado_upd,
                                "telefono_estudiante": telefono_upd,
                                "email_estudiante": email_upd,
                                "direccion_estudiante": direccion_upd
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
                            
                            c_btn1, c_btn2, c_btn3 = st.columns([1, 1, 1])
                            with c_btn1:
                                with st.popover("✏️ Editar", use_container_width=True):
                                    st.markdown(f"**Modificar:** {acud.get('nombre_acudiente')}")
                                    with st.form(f"form_pop_acud_{doc_acud}_{idx}"):
                                        ed_nombre = st.text_input("Nombre completo", value=acud.get('nombre_acudiente', ''))
                                        par_actual = acud.get('parentesco', 'Padre')
                                        idx_p = PARENTESCOS.index(par_actual) if par_actual in PARENTESCOS else 0
                                        ed_par = st.selectbox("Parentesco", PARENTESCOS, index=idx_p)
                                        ed_tel = st.text_input("Teléfono", value=acud.get('telefono_acudiente', ''))
                                        ed_email = st.text_input("Correo", value=acud.get('email_acudiente', ''))
                                        
                                        if st.form_submit_button("💾 Guardar", type="primary", use_container_width=True):
                                            payload_acud = {
                                                "nombre_acudiente": ed_nombre,
                                                "parentesco": ed_par,
                                                "telefono_acudiente": ed_tel,
                                                "email_acudiente": ed_email
                                            }
                                            url_upd = f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_estudiante=eq.{documento_buscar}&documento_acudiente=eq.{doc_acud}"
                                            r_upd = requests.patch(url_upd, headers=headers, json=payload_acud)
                                            if r_upd.status_code in [200, 204]:
                                                st.success("✅ Acudiente actualizado")
                                                st.rerun()
                                            else:
                                                st.error(f"Error ({r_upd.status_code}): {r_upd.text}")
                            
                            with c_btn2:
                                if not es_princ:
                                    if st.button("⭐ Principal", key=f"btn_p_{doc_acud}_{idx}", use_container_width=True):
                                        requests.patch(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_estudiante=eq.{documento_buscar}", headers=headers, json={"es_principal": False})
                                        requests.patch(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_estudiante=eq.{documento_buscar}&documento_acudiente=eq.{doc_acud}", headers=headers, json={"es_principal": True})
                                        st.rerun()
                                else:
                                    st.button("⭐ Principal", disabled=True, use_container_width=True, key=f"btn_dis_{doc_acud}_{idx}")
                            
                            with c_btn3:
                                if st.button("🗑️ Quitar", key=f"btn_del_{doc_acud}_{idx}", use_container_width=True):
                                    requests.delete(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_estudiante=eq.{documento_buscar}&documento_acudiente=eq.{doc_acud}", headers=headers)
                                    st.rerun()
                            
                            st.write("")
                    else:
                        st.warning("Sin acudientes vinculados.")

                    with st.expander("➕ Vincular otro acudiente", expanded=False):
                        with st.form("form_add_acudiente_extra", clear_on_submit=True):
                            n_nom = st.text_input("Nombre completo *")
                            ca1, ca2 = st.columns(2)
                            with ca1:
                                n_doc = st.text_input("Documento *")
                            with ca2:
                                n_par = st.selectbox("Parentesco *", PARENTESCOS)
                            ca3, ca4 = st.columns(2)
                            with ca3:
                                n_tel = st.text_input("Teléfono")
                            with ca4:
                                n_em = st.text_input("Email")
                            n_pr = st.checkbox("Marcar como acudiente principal", value=False)
                            
                            if st.form_submit_button("🔗 Vincular al Alumno", type="primary", use_container_width=True):
                                if not n_nom or not n_doc:
                                    st.error("Nombre y documento obligatorios")
                                else:
                                    if n_pr:
                                        requests.patch(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente?documento_estudiante=eq.{documento_buscar}", headers=headers, json={"es_principal": False})
                                    requests.post(f"{SUPABASE_URL}/rest/v1/estudiante_acudiente", headers=headers, json={
                                        "documento_estudiante": documento_buscar, "documento_acudiente": n_doc,
                                        "nombre_acudiente": n_nom, "parentesco": n_par,
                                        "telefono_acudiente": n_tel, "email_acudiente": n_em, "es_principal": n_pr
                                    })
                                    requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json={
                                        "username": n_doc, "password_hash": "demo2026", "rol": "acudiente", "documento": n_doc, "roles": ["acudiente"]
                                    })
                                    st.success(f"✅ {n_nom} vinculado exitosamente")
                                    st.rerun()
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
                            st.rerun()
                        else:
                            st.error(f"Error: {response.status_code}")
    
    with tab3:
        documento_buscar = st.text_input("Buscar docente por documento:", placeholder="Ej: 79123456", key="buscar_doc_edit")
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
                    
                    if st.form_submit_button("💾 Guardar Cambios Docente", type="primary", use_container_width=True):
                        data_update = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo
                        }
                        requests.patch(f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}", headers=headers, json=data_update)
                        st.success("✅ Ficha docente actualizada")
                        st.rerun()
            else:
                st.warning("No se encontró ningún docente con ese documento")


# ============================================
# GESTIÓN ACADÉMICA 1: NIVELES EDUCATIVOS (COMPACTO)
# ============================================
def configurar_niveles():
    st.subheader("📚 Niveles Educativos")
    headers = get_headers()
    
    col_tabla, col_form = st.columns([1.3, 1], gap="medium")
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []

    with col_tabla:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Niveles Activos en la Institución</b>
        </div>
        """, unsafe_allow_html=True)
        
        if niveles:
            df_niv = pd.DataFrame(niveles)[['orden', 'nombre']].rename(columns={'orden': 'Orden', 'nombre': 'Nivel Educativo'})
            st.dataframe(df_niv, use_container_width=True, height=260)
            
            # Selector compacto para eliminar
            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                niv_del = st.selectbox("Seleccionar para eliminar:", [n['nombre'] for n in niveles], label_visibility="collapsed")
            with c_del2:
                if st.button("🗑️ Eliminar", use_container_width=True):
                    id_borrar = next(n['id'] for n in niveles if n['nombre'] == niv_del)
                    requests.delete(f"{SUPABASE_URL}/rest/v1/niveles?id=eq.{id_borrar}", headers=headers)
                    st.success(f"Nivel '{niv_del}' eliminado")
                    st.rerun()
        else:
            st.info("No hay niveles registrados.")

    with col_form:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Registrar Nuevo Nivel</b>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("form_nuevo_nivel", clear_on_submit=True):
            nuevo_nivel = st.text_input("Nombre del Nivel (Ej: Bachillerato, Primaria) *")
            orden_nivel = st.number_input("Orden de visualización", min_value=1, value=len(niveles) + 1 if niveles else 1)
            
            if st.form_submit_button("💾 Guardar Nivel", type="primary", use_container_width=True):
                if nuevo_nivel:
                    data = {"nombre": nuevo_nivel.strip(), "orden": int(orden_nivel)}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/niveles", headers=headers, json=data)
                    if r.status_code == 201:
                        st.success(f"✅ Nivel '{nuevo_nivel}' creado")
                        st.rerun()
                    else:
                        st.error(f"Error: {r.text}")


# ============================================
# GESTIÓN ACADÉMICA 2: ASIGNATURAS Y PÉNSUM (COMPACTO)
# ============================================
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

    col_tabla, col_form = st.columns([1.3, 1], gap="medium")

    with col_tabla:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📘 Catálogo de Asignaturas y Grados que la Cursan</b>
        </div>
        """, unsafe_allow_html=True)

        if materias:
            datos_mat = []
            for m in materias:
                nivs = ", ".join(niveles_por_materia.get(m['id'], [])) or "Sin asignar"
                datos_mat.append({
                    "ID": m['id'],
                    "Asignatura": m.get('nombre'),
                    "Código": m.get('codigo') or "-",
                    "Niveles Educativos": nivs
                })
            df_mat = pd.DataFrame(datos_mat)
            st.dataframe(df_mat[['Asignatura', 'Código', 'Niveles Educativos']], use_container_width=True, height=280)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                mat_del_nom = st.selectbox("Eliminar asignatura:", [m['nombre'] for m in materias], label_visibility="collapsed")
            with c_del2:
                if st.button("🗑️ Eliminar", use_container_width=True, key="btn_del_mat"):
                    id_mat_del = next(m['id'] for m in materias if m['nombre'] == mat_del_nom)
                    requests.delete(f"{SUPABASE_URL}/rest/v1/materias_niveles?materia_id=eq.{id_mat_del}", headers=headers)
                    requests.delete(f"{SUPABASE_URL}/rest/v1/materias?id=eq.{id_mat_del}", headers=headers)
                    st.success(f"Asignatura eliminada")
                    st.rerun()
        else:
            st.info("No hay asignaturas registradas.")

    with col_form:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Nueva Asignatura / Pénsum</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_nueva_materia", clear_on_submit=True):
            nombre_mat = st.text_input("Nombre de la asignatura *")
            codigo_mat = st.text_input("Código o abreviatura (Ej: MAT-01)")
            niveles_sel = st.multiselect("Niveles donde se imparte *", nivel_nombres)

            if st.form_submit_button("💾 Guardar Asignatura", type="primary", use_container_width=True):
                if not nombre_mat or not niveles_sel:
                    st.error("❌ Nombre y niveles son obligatorios")
                else:
                    data = {"nombre": nombre_mat.upper().strip(), "codigo": codigo_mat.upper().strip() if codigo_mat else None}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/materias", headers=headers, json=data)
                    if r.status_code == 201:
                        m_id = r.json()[0]['id']
                        for n_nom in niveles_sel:
                            requests.post(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers, json={"materia_id": m_id, "nivel_id": niveles_dict.get(n_nom)})
                        st.success("✅ Asignatura creada")
                        st.rerun()
                    else:
                        st.error(f"Error: {r.text}")


# ============================================
# GESTIÓN ACADÉMICA 3: CURSOS Y GRADOS (COMPACTO)
# ============================================
def gestionar_grados():
    st.subheader("📚 Gestión de Grados y Cursos")
    headers = get_headers()
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    
    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    grados = r_grados.json() if r_grados.status_code == 200 else []

    col_tabla, col_form = st.columns([1.3, 1], gap="medium")

    with col_tabla:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Cursos y Grados Matriculados</b>
        </div>
        """, unsafe_allow_html=True)

        if grados:
            data = []
            for g in grados:
                n_nombre = next((n['nombre'] for n in niveles if n['id'] == g.get('nivel_id')), "Sin nivel")
                data.append({"Curso / Salón": g.get('curso'), "Nivel Educativo": n_nombre})
            st.dataframe(pd.DataFrame(data), use_container_width=True, height=280)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                cur_del = st.selectbox("Eliminar curso:", [g['curso'] for g in grados if g.get('curso')], label_visibility="collapsed")
            with c_del2:
                if st.button("🗑️ Eliminar", use_container_width=True, key="btn_del_curso"):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/grados?curso=eq.{cur_del}", headers=headers)
                    st.success(f"Curso {cur_del} eliminado")
                    st.rerun()
        else:
            st.info("No hay cursos creados.")

    with col_form:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Crear Nuevo Curso</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("nuevo_grado", clear_on_submit=True):
            nombre_cur = st.text_input("Nombre del Curso (Ej: 601, 702, Jardín A) *")
            nivel_cur = st.selectbox("Nivel Educativo al que pertenece *", [n['nombre'] for n in niveles])

            if st.form_submit_button("💾 Guardar Curso", type="primary", use_container_width=True):
                if nombre_cur:
                    data = {"curso": nombre_cur.upper().strip(), "nivel_id": niveles_dict.get(nivel_cur)}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/grados", headers=headers, json=data)
                    if r.status_code == 201:
                        st.success(f"✅ Curso {nombre_cur} creado")
                        st.rerun()
                    else:
                        st.error(f"Error: {r.text}")


# ============================================
# GESTIÓN ACADÉMICA 4: DIRECTORES DE GRUPO (PANORAMA GENERAL)
# ============================================
def gestion_directores_grupo():
    st.subheader("👨‍🏫 Asignación de Directores de Grupo")
    headers = get_headers()
    
    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=curso&order=curso.asc", headers=headers)
    cursos = [g['curso'] for g in r_grados.json() if g.get('curso')] if r_grados.status_code == 200 and r_grados.json() else CURSOS
    cursos = sorted(list(set(cursos)))

    r_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?order=apellidos_docente.asc", headers=headers)
    docentes = r_docentes.json() if r_docentes.status_code == 200 else []
    doc_dict = {d['documento_docente']: f"{d['apellidos_docente']} {d['nombre_docente']}" for d in docentes}

    r_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?asignatura=ilike.%direccion%", headers=headers)
    directores_actuales = r_asig.json() if r_asig.status_code == 200 else []
    dir_por_curso = {a['curso']: a['documento_docente'] for a in directores_actuales if a.get('curso')}

    col_tabla, col_form = st.columns([1.3, 1], gap="medium")

    with col_tabla:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Panorama Institucional de Direcciones de Grupo</b>
        </div>
        """, unsafe_allow_html=True)

        resumen = []
        for c in cursos:
            doc_id = dir_por_curso.get(c)
            nombre_doc = doc_dict.get(doc_id, "⚠️ Sin asignar") if doc_id else "⚠️ Sin asignar"
            resumen.append({"Curso": c, "Director de Grupo": nombre_doc})
        
        st.dataframe(pd.DataFrame(resumen), use_container_width=True, height=310)

    with col_form:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">✏️ Asignar o Cambiar Director</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_asignar_director"):
            curso_sel = st.selectbox("Seleccionar Curso:", cursos)
            doc_actual_id = dir_por_curso.get(curso_sel)
            doc_actual_nom = doc_dict.get(doc_actual_id, "Ninguno") if doc_actual_id else "Ninguno"
            st.caption(f"Director actual de **{curso_sel}**: `{doc_actual_nom}`")

            nuevo_doc_id = st.selectbox("Nuevo Director Docente:", [""] + list(doc_dict.keys()), format_func=lambda x: doc_dict.get(x, "Ninguno (Dejar Vacante)") if x else "Ninguno (Dejar Vacante)")

            if st.form_submit_button("💾 Guardar Director", type="primary", use_container_width=True):
                requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=ilike.%direccion%", headers=headers)
                if nuevo_doc_id:
                    data = {"curso": curso_sel, "asignatura": "DIRECCION DE CURSO", "documento_docente": nuevo_doc_id, "anio": datetime.now().year}
                    requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data)
                    st.success(f"✅ Director asignado para {curso_sel}")
                else:
                    st.info(f"Dirección de {curso_sel} liberada.")
                st.rerun()


# ============================================
# GESTIÓN ACADÉMICA 5: ASIGNACIÓN DOCENTE POR MATERIA (COMPACTO)
# ============================================
def asignar_docentes_curso():
    st.subheader("👨‍🏫 Carga Académica Docente por Curso")
    headers = get_headers()
    
    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=curso&order=curso.asc", headers=headers)
    cursos = [g['curso'] for g in r_grados.json() if g.get('curso')] if r_grados.status_code == 200 and r_grados.json() else CURSOS
    cursos = sorted(list(set(cursos)))

    r_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes?order=apellidos_docente.asc", headers=headers)
    docentes = r_doc.json() if r_doc.status_code == 200 else []
    doc_dict = {d['documento_docente']: f"{d['apellidos_docente']} {d['nombre_docente']}" for d in docentes}

    r_mat = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
    materias = r_mat.json() if r_mat.status_code == 200 else []

    # Barra superior ultra compacta
    col_c1, _ = st.columns([1.5, 2.5])
    with col_c1:
        curso_sel = st.selectbox("Selecciona el curso a consultar/gestionar:", cursos, key="asig_curso_sel")

    r_actuales = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}", headers=headers)
    actuales = [a for a in r_actuales.json() if "DIRECCION" not in str(a.get('asignatura', '')).upper()] if r_actuales.status_code == 200 else []

    col_tabla, col_form = st.columns([1.3, 1], gap="medium")

    with col_tabla:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Asignaturas y Docentes del Grado {curso_sel}</b>
        </div>
        """, unsafe_allow_html=True)

        if actuales:
            tabla = [{"Asignatura": a.get('asignatura'), "Docente Encargado": doc_dict.get(a.get('documento_docente'), a.get('documento_docente'))} for a in actuales]
            st.dataframe(pd.DataFrame(tabla), use_container_width=True, height=270)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                asig_del = st.selectbox("Desvincular materia:", [a.get('asignatura') for a in actuales], label_visibility="collapsed")
            with c_del2:
                if st.button("🗑️ Quitar", use_container_width=True):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=eq.{asig_del}", headers=headers)
                    st.success(f"{asig_del} removida de {curso_sel}")
                    st.rerun()
        else:
            st.info(f"El grado {curso_sel} no tiene asignaturas ni docentes vinculados.")

    with col_form:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Asignar Asignatura a Docente</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_asignar_doc", clear_on_submit=True):
            materia_nom = st.selectbox("Asignatura:", [m['nombre'] for m in materias])
            docente_id = st.selectbox("Docente Asignado:", list(doc_dict.keys()), format_func=lambda x: doc_dict.get(x))

            if st.form_submit_button("💾 Guardar Carga Académica", type="primary", use_container_width=True):
                requests.delete(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}&asignatura=eq.{materia_nom}", headers=headers)
                data = {"curso": curso_sel, "asignatura": materia_nom, "documento_docente": docente_id, "anio": datetime.now().year}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data)
                if r.status_code == 201:
                    st.success(f"✅ {materia_nom} asignada con éxito")
                    st.rerun()
                else:
                    st.error(f"Error: {r.text}")


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
