# ============================================
# modulos/paneles/admin.py - VERSIÓN COMPLETA Y CORREGIDA
# ============================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from utils import SUPABASE_URL, get_headers

# ============================================
# CONSTANTES
# ============================================
CURSOS = ["901", "902", "903", "1001", "1002", "1003", "1101"]
DIAS_SEMANA = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
PARENTESCOS = ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"]
SEXOS = ["", "Masculino", "Femenino"]
TIPOS_CONTRATO = ["", "Planta", "Contrato", "Cátedra", "Ocasional"]

# ============================================
# FUNCIÓN PRINCIPAL mostrar()
# ============================================
def mostrar(data):
    """Panel de administrador - El menú se maneja desde app.py"""
    st.title("🛡️ Panel de Administrador")
    st.write(f"Bienvenido, {data.get('username', 'Admin')}")
    
    # Mostrar contenido principal
    st.subheader("📊 Panel de control")
    st.info("🔐 Selecciona una opción del menú lateral para comenzar.")
    
    # Métricas rápidas
    headers = get_headers()
    
    try:
        response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
        total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    except:
        total_estudiantes = 0
    
    try:
        response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
        if response_doc.status_code == 200:
            datos = response_doc.json()
            docentes_unicos = set([d.get('documento_docente') for d in datos if d.get('documento_docente')])
            total_docentes = len(docentes_unicos)
        else:
            total_docentes = 0
    except:
        total_docentes = 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👨‍🎓 Estudiantes", total_estudiantes)
    col2.metric("👨‍🏫 Docentes", total_docentes)
    col3.metric("📚 Cursos", "7")
    col4.metric("📅 Año Lectivo", datetime.now().year)
    
    st.divider()
    st.caption("📌 Panel de control del Administrador")

# ============================================
# GESTIÓN DE ESTUDIANTES
# ============================================
def gestion_estudiantes():
    """Gestión de estudiantes"""
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Nuevo", "✏️ Editar"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
            if response.status_code == 200:
                estudiantes = response.json()
                if estudiantes:
                    df = pd.DataFrame(estudiantes)
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total: {len(estudiantes)} estudiantes")
                else:
                    st.info("No hay estudiantes registrados")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        st.write("**Registrar nuevo estudiante**")
        with st.form("nuevo_estudiante", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                curso = st.selectbox("Curso *", CURSOS)
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            with col2:
                st.markdown("**Datos del acudiente**")
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", PARENTESCOS)
                telefono_acudiente = st.text_input("Teléfono del acudiente")
                email_acudiente = st.text_input("Email del acudiente")
            
            if st.form_submit_button("💾 Registrar", type="primary"):
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
                            st.info(f"🔑 Estudiante: {documento} | demo2026")
                            st.info(f"🔑 Acudiente: {documento_acudiente} | demo2026")
                            st.balloons()
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        st.write("**Editar estudiante**")
        documento_buscar = st.text_input("Documento del estudiante", key="buscar_est_edit")
        
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
                                           index=CURSOS.index(estudiante.get('curso', '901')))
                    with col2:
                        telefono = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
                        email = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
                    
                    if st.form_submit_button("💾 Guardar cambios", type="primary"):
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
                            st.success("✅ Estudiante actualizado")
                            st.rerun()
                        else:
                            st.error(f"Error: {response_update.status_code}")
            else:
                st.warning("No se encontró el estudiante")

# ============================================
# GESTIÓN DE DOCENTES
# ============================================
def gestion_docentes():
    """Gestión de docentes"""
    st.subheader("👨‍🏫 Gestión de Docentes")
    headers = get_headers()
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Nuevo", "✏️ Editar"])
    
    with tab1:
        try:
            response = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
            if response.status_code == 200:
                docentes = response.json()
                if docentes:
                    df = pd.DataFrame(docentes)
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total: {len(docentes)} docentes")
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
                titulo = st.text_input("Título")
                tipo_contrato = st.selectbox("Tipo de contrato", TIPOS_CONTRATO)
                fecha_ingreso = st.date_input("Fecha de ingreso", value=None)
            
            if st.form_submit_button("💾 Registrar", type="primary"):
                if not all([nombre, apellidos, documento]):
                    st.error("❌ Completa los campos obligatorios")
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
                            st.info(f"🔑 Usuario: {username} | demo2026")
                            st.balloons()
                        else:
                            st.error(f"Error: {response.status_code}")
    
    with tab3:
        st.write("**Editar docente**")
        documento_buscar = st.text_input("Documento del docente", key="buscar_doc_edit")
        
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
                    
                    if st.form_submit_button("💾 Guardar cambios", type="primary"):
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
# CONFIGURAR NIVELES
# ============================================
def configurar_niveles():
    """Configurar niveles educativos"""
    st.subheader("📚 Niveles Educativos")
    headers = get_headers()
    
    response = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response.status_code == 200:
        niveles = response.json()
        if niveles:
            st.write("**Niveles existentes:**")
            for n in niveles:
                st.write(f"- {n['nombre']}")
    
    with st.expander("➕ Agregar nivel"):
        nuevo_nivel = st.text_input("Nombre del nivel", key="nuevo_nivel_input")
        if st.button("Agregar nivel", key="agregar_nivel_btn"):
            if nuevo_nivel:
                data = {"nombre": nuevo_nivel, "orden": len(niveles) + 1 if niveles else 1}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/niveles", headers=headers, json=data)
                if r.status_code == 201:
                    st.success(f"✅ Nivel '{nuevo_nivel}' agregado")
                    st.rerun()

# ============================================
# GESTIONAR ASIGNATURAS
# ============================================
def gestionar_asignaturas():
    """Gestionar asignaturas"""
    st.subheader("📚 Gestionar Asignaturas")
    headers = get_headers()
    
    # Obtener niveles
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    nivel_nombres = [n['nombre'] for n in niveles]
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    
    # Obtener materias
    response_materias = requests.get(f"{SUPABASE_URL}/rest/v1/materias?order=nombre.asc", headers=headers)
    if response_materias.status_code != 200:
        st.error("Error al cargar materias")
        return
    
    materias = response_materias.json()
    
    # Obtener relaciones
    response_relaciones = requests.get(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers)
    relaciones = response_relaciones.json() if response_relaciones.status_code == 200 else []
    
    # Crear diccionario de niveles por materia
    niveles_por_materia = {}
    for r in relaciones:
        materia_id = r['materia_id']
        nivel_id = r['nivel_id']
        if materia_id not in niveles_por_materia:
            niveles_por_materia[materia_id] = []
        niveles_por_materia[materia_id].append(nivel_id)
    
    # Mostrar tabla
    st.write("### Asignaturas y niveles")
    
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
            
            st.write("**Niveles:**")
            cols = st.columns(len(nivel_nombres))
            for idx, nivel in enumerate(nivel_nombres):
                with cols[idx]:
                    nivel_id = niveles_dict.get(nivel)
                    checked = nivel_id in niveles_ids if nivel_id else False
                    if st.checkbox(nivel, value=checked, key=f"m_{m['id']}_{nivel}"):
                        if not checked and nivel_id:
                            rel_data = {"materia_id": m['id'], "nivel_id": nivel_id}
                            requests.post(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers, json=rel_data)
                    else:
                        if checked and nivel_id:
                            requests.delete(f"{SUPABASE_URL}/rest/v1/materias_niveles?materia_id=eq.{m['id']}&nivel_id=eq.{nivel_id}", headers=headers)
    
    # Agregar nueva materia
    st.divider()
    st.write("### ➕ Agregar nueva asignatura")
    with st.form("nueva_materia"):
        nombre = st.text_input("Nombre de la asignatura *")
        codigo = st.text_input("Código (opcional)")
        
        st.write("**Niveles:**")
        niveles_nueva = []
        cols = st.columns(len(nivel_nombres))
        for idx, nivel in enumerate(nivel_nombres):
            with cols[idx]:
                if st.checkbox(nivel, key=f"nueva_{nivel}"):
                    niveles_nueva.append(nivel)
        
        if st.form_submit_button("💾 Crear asignatura", type="primary"):
            if not nombre:
                st.error("❌ El nombre es obligatorio")
            elif not niveles_nueva:
                st.error("❌ Selecciona al menos un nivel")
            else:
                data = {"nombre": nombre.upper().strip(), "codigo": codigo.upper().strip() if codigo else None}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/materias", headers=headers, json=data)
                if r.status_code == 201:
                    materia_id = r.json()[0]['id']
                    for nivel_nombre in niveles_nueva:
                        nivel_id = niveles_dict.get(nivel_nombre)
                        if nivel_id:
                            rel_data = {"materia_id": materia_id, "nivel_id": nivel_id}
                            requests.post(f"{SUPABASE_URL}/rest/v1/materias_niveles", headers=headers, json=rel_data)
                    st.success(f"✅ Asignatura '{nombre}' creada")
                    st.rerun()

# ============================================
# ASIGNAR PÉNSUM POR NIVEL
# ============================================
def asignar_pensum_nivel():
    """Asignar pénsum por nivel"""
    st.subheader("📚 Asignar Pénsum por Nivel")
    st.info("Funcionalidad en desarrollo")

# ============================================
# ASIGNAR DOCENTES A CURSO
# ============================================
def asignar_docentes_curso():
    """Asignar docentes a curso"""
    st.subheader("👨‍🏫 Asignar Docentes a Curso")
    headers = get_headers()
    
    # Obtener cursos
    response_cursos = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes?select=curso", headers=headers)
    if response_cursos.status_code == 200:
        cursos = list(set([e['curso'] for e in response_cursos.json() if e.get('curso')]))
        cursos.sort()
    
    if not cursos:
        st.warning("No hay cursos registrados")
        return
    
    curso_seleccionado = st.selectbox("Seleccionar curso", cursos)
    st.info(f"Funcionalidad en desarrollo para el curso {curso_seleccionado}")

# ============================================
# GESTIONAR GRADOS
# ============================================
def gestionar_grados():
    """Gestionar grados/cursos"""
    st.subheader("📚 Gestionar Cursos")
    headers = get_headers()
    
    # Obtener niveles
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    niveles_dict = {n['nombre']: n['id'] for n in niveles}
    nivel_nombres = [n['nombre'] for n in niveles]
    
    # Obtener grados
    response_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados", headers=headers)
    if response_grados.status_code != 200:
        st.error("Error al cargar grados")
        return
    
    grados = response_grados.json()
    
    # Mostrar tabla
    st.write("### Lista de cursos")
    if grados:
        data = []
        for g in grados:
            nivel_id = g.get('nivel_id')
            nivel_nombre = next((n['nombre'] for n in niveles if n['id'] == nivel_id), "Sin nivel")
            data.append({"Curso": g.get('curso'), "Nivel": nivel_nombre})
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    
    # Agregar nuevo curso
    st.divider()
    st.write("### ➕ Agregar nuevo curso")
    with st.form("nuevo_grado"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del curso *")
        with col2:
            nivel_seleccionado = st.selectbox("Nivel *", nivel_nombres)
        
        if st.form_submit_button("💾 Crear curso", type="primary"):
            if not nombre:
                st.error("❌ El nombre es obligatorio")
            else:
                nivel_id = niveles_dict.get(nivel_seleccionado)
                data = {"curso": nombre.upper().strip(), "nivel_id": nivel_id}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/grados", headers=headers, json=data)
                if r.status_code == 201:
                    st.success(f"✅ Curso '{nombre}' creado")
                    st.rerun()

# ============================================
# GESTIONAR DIRECTORES DE GRUPO
# ============================================
def gestion_directores_grupo():
    """Gestionar directores de grupo"""
    st.subheader("👨‍🏫 Directores de Grupo")
    headers = get_headers()
    
    # Obtener cursos
    response_cursos = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes?select=curso", headers=headers)
    if response_cursos.status_code == 200:
        cursos = list(set([e['curso'] for e in response_cursos.json() if e.get('curso')]))
        cursos.sort()
    
    if not cursos:
        st.warning("No hay cursos registrados")
        return
    
    curso_seleccionado = st.selectbox("Seleccionar curso", cursos)
    
    # Obtener docentes
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    if response_docentes.status_code != 200:
        st.error("Error al cargar docentes")
        return
    
    docentes = response_docentes.json()
    docentes_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}
    
    # Obtener director actual
    response_asignaciones = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_seleccionado}&asignatura=ilike.%direccion%", headers=headers)
    asignaciones = response_asignaciones.json() if response_asignaciones.status_code == 200 else []
    
    director_actual = asignaciones[0].get('documento_docente') if asignaciones else None
    nombre_actual = docentes_dict.get(director_actual, "Sin asignar") if director_actual else "Sin asignar"
    
    st.info(f"📌 Director actual: **{nombre_actual}**")
    
    docente_seleccionado = st.selectbox(
        "Seleccionar nuevo director",
        options=[""] + list(docentes_dict.keys()),
        format_func=lambda x: docentes_dict.get(x, "Ninguno") if x else "Ninguno"
    )
    
    if st.button("💾 Asignar director", type="primary"):
        if docente_seleccionado:
            # Eliminar director anterior
            if director_actual:
                delete_url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_seleccionado}&asignatura=ilike.%direccion%"
                requests.delete(delete_url, headers=headers)
            
            # Asignar nuevo director
            data = {
                "curso": curso_seleccionado,
                "asignatura": "DIRECCION DE CURSO",
                "documento_docente": docente_seleccionado,
                "anio": datetime.now().year
            }
            response = requests.post(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers, json=data)
            if response.status_code == 201:
                st.success(f"✅ Director asignado para {curso_seleccionado}")
                st.rerun()
            else:
                st.error(f"Error: {response.status_code}")
        else:
            st.warning("Selecciona un docente")

# ============================================
# CONFIGURAR HORAS POR NIVEL
# ============================================
def configurar_horas_nivel():
    """Configurar horas por nivel"""
    st.subheader("⏰ Configurar Horas por Nivel")
    headers = get_headers()
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    if response_niveles.status_code != 200:
        st.error("Error al cargar niveles")
        return
    
    niveles = response_niveles.json()
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    nivel_nombres = [n['nombre'] for n in niveles]
    nivel_seleccionado = st.selectbox("Seleccionar nivel", nivel_nombres)
    nivel_id = next(n['id'] for n in niveles if n['nombre'] == nivel_seleccionado)
    
    url_horas = f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=orden.asc"
    response_horas = requests.get(url_horas, headers=headers)
    horas = response_horas.json() if response_horas.status_code == 200 else []
    
    st.write(f"**Horas configuradas para {nivel_seleccionado}:**")
    if horas:
        for h in horas:
            st.write(f"- Hora {h['orden']}: {h['hora_inicio'][:5]} - {h['hora_fin'][:5]}")
    else:
        st.info("No hay horas configuradas para este nivel.")

# ============================================
# CONFIGURAR JORNADA POR NIVEL
# ============================================
def configurar_jornada_nivel():
    """Configurar jornada por nivel"""
    st.subheader("📅 Configurar Días Laborales por Nivel")
    st.info("Funcionalidad en desarrollo")

# ============================================
# CONFIGURAR HORARIO DE CURSO
# ============================================
def configurar_horario_curso():
    """Configurar horario de curso"""
    st.subheader("📖 Asignar Horarios por Curso")
    st.info("Funcionalidad en desarrollo")

# ============================================
# MOSTRAR SISTEMA
# ============================================
def mostrar_sistema():
    """Configuración del sistema"""
    st.subheader("⚙️ Configuración del Sistema")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre_colegio = st.text_input("Nombre del colegio", "Mi Colegio")
        año_lectivo = st.number_input("Año lectivo", min_value=2000, max_value=2100, value=datetime.now().year)
        if st.button("💾 Guardar Configuración", type="primary"):
            st.success("✅ Configuración guardada")
    
    with col2:
        st.write("**Información del sistema**")
        st.write(f"- Versión: 1.0.0")
        st.write(f"- Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        if st.button("📀 Crear Respaldo", type="primary"):
            st.success("✅ Respaldo creado")

# ============================================
# GESTIONAR FESTIVOS
# ============================================
def gestion_festivos():
    """Gestionar festivos"""
    st.subheader("📆 Festivos")
    headers = get_headers()
    
    year = st.selectbox("Año", [2024, 2025, 2026], key="festivos_year")
    
    url_festivos = f"{SUPABASE_URL}/rest/v1/festivos?year=eq.{year}&order=fecha.asc"
    response_festivos = requests.get(url_festivos, headers=headers)
    
    if response_festivos.status_code == 200:
        festivos = response_festivos.json()
        if festivos:
            st.write("**Festivos registrados:**")
            for f in festivos:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{f['fecha']} - {f.get('descripcion', 'Sin descripción')}")
                with col2:
                    if st.button("🗑️", key=f"del_festivo_{f['id']}"):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?id=eq.{f['id']}", headers=headers)
                        st.rerun()
        else:
            st.info("No hay festivos registrados")
    
    with st.expander("➕ Agregar festivo"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha", key="festivo_fecha")
        with col2:
            descripcion = st.text_input("Descripción", key="festivo_desc")
        
        if st.button("Agregar", key="agregar_festivo_btn"):
            data = {"fecha": str(fecha), "descripcion": descripcion, "year": fecha.year}
            requests.post(f"{SUPABASE_URL}/rest/v1/festivos", headers=headers, json=data)
            st.success("✅ Festivo agregado")
            st.rerun()

# ============================================
# REPORTES ACADÉMICOS
# ============================================
def reportes_academicos():
    """Reportes académicos"""
    st.subheader("📊 Reportes Académicos")
    
    st.info("📋 Funcionalidad en desarrollo")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Reportes disponibles:**")
        st.write("- 📊 Reporte de estudiantes por curso")
        st.write("- 📈 Reporte de notas")
        st.write("- 📋 Listado de docentes")
    with col2:
        st.write("**Próximamente:**")
        st.write("- 📊 Análisis de rendimiento")
        st.write("- 📈 Estadísticas por asignatura")
