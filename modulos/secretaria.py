import streamlit as st
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.horarios import mostrar_horario_tabla
from modulos.features.asistencia import mostrar_reporte_asistencia_general

def mostrar(data):
    st.title("📋 Panel de Secretaria")
    st.write(f"Bienvenida, {data.get('username', 'Secretaria')}")
    
    headers = get_headers()
    
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    opcion = st.selectbox(
        "Seleccionar función",
        [
            "📊 Dashboard",
            "👨‍🎓 Gestión de Estudiantes",
            "👨‍🏫 Gestión de Docentes",
            "📚 Gestión de Cursos",
            "📅 Consultar Horarios",
            "📄 Certificados",
            "📊 Reportes"
        ]
    )
    
    st.divider()
    
    if opcion == "📊 Dashboard":
        mostrar_dashboard()
    elif opcion == "👨‍🎓 Gestión de Estudiantes":
        gestion_estudiantes()
    elif opcion == "👨‍🏫 Gestión de Docentes":
        gestion_docentes()
    elif opcion == "📚 Gestión de Cursos":
        gestion_cursos()
    elif opcion == "📅 Consultar Horarios":
        consultar_horarios()
    elif opcion == "📄 Certificados":
        st.info("🚧 Módulo en desarrollo")
    elif opcion == "📊 Reportes":
        st.info("🚧 Módulo en desarrollo")


def mostrar_dashboard():
    st.subheader("📊 Dashboard Secretaria")
    
    headers = get_headers()
    
    response_est = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
    total_estudiantes = len(response_est.json()) if response_est.status_code == 200 else 0
    
    response_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    total_docentes = len(response_doc.json()) if response_doc.status_code == 200 else 0
    
    estudiantes = response_est.json() if response_est.status_code == 200 else []
    activos = len([e for e in estudiantes if e.get('activo', True) != False])
    inactivos = total_estudiantes - activos
    
    # Estadísticas por curso
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    estudiantes_por_curso = {}
    for curso in cursos:
        estudiantes_por_curso[curso] = len([e for e in estudiantes if e.get('curso') == curso])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("👨‍🎓 Total Estudiantes", total_estudiantes)
    col2.metric("✅ Activos", activos)
    col3.metric("❌ Inactivos", inactivos)
    col4.metric("👨‍🏫 Total Docentes", total_docentes)
    col5.metric("✅ Docentes Activos", total_docentes)
    
    with st.expander("📊 Distribución por Curso"):
        for curso, cantidad in estudiantes_por_curso.items():
            st.write(f"**Curso {curso}:** {cantidad} estudiantes")
    
    st.info("📌 Panel de gestión administrativa")


def gestion_estudiantes():
    st.subheader("👨‍🎓 Gestión de Estudiantes")
    
    headers = get_headers()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Estudiantes", "➕ Matricular", "✏️ Editar", "🚫 Dar de Baja"])
    
    with tab1:
        # Filtros
        st.write("**🔍 Filtros**")
        
        niveles = ["Todos", "Secundaria", "Media"]
        cursos_secundaria = ["901", "902", "903"]
        cursos_media = ["1001", "1002", "1003", "1101"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filtro_nivel = st.selectbox("Nivel", niveles, key="filtro_nivel_est")
            # Actualizar cursos según nivel seleccionado
            if filtro_nivel == "Secundaria":
                opciones_cursos = ["Todos"] + cursos_secundaria
            elif filtro_nivel == "Media":
                opciones_cursos = ["Todos"] + cursos_media
            else:
                opciones_cursos = ["Todos", "901", "902", "903", "1001", "1002", "1003", "1101"]
        with col2:
            filtro_curso = st.selectbox("Curso", opciones_cursos, key="filtro_curso_est")
        with col3:
            filtro_activo = st.selectbox("Estado", ["Todos", "Activos", "Inactivos"], key="filtro_activo_est")
        with col4:
            buscar_nombre = st.text_input("Buscar", placeholder="Nombre...", key="buscar_nombre_est")
        
        response = requests.get(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers)
        
        if response.status_code == 200:
            estudiantes = response.json()
            if estudiantes:
                df = pd.DataFrame(estudiantes)
                
                # Mapeo de curso a nivel
                nivel_por_curso = {
                    "901": "Secundaria", "902": "Secundaria", "903": "Secundaria",
                    "1001": "Media", "1002": "Media", "1003": "Media", "1101": "Media"
                }
                df['nivel'] = df['curso'].map(nivel_por_curso)
                
                # Aplicar filtros
                df_filtrada = df.copy()
                
                if filtro_nivel != "Todos":
                    df_filtrada = df_filtrada[df_filtrada['nivel'] == filtro_nivel]
                if filtro_curso != "Todos":
                    df_filtrada = df_filtrada[df_filtrada['curso'] == filtro_curso]
                if filtro_activo == "Activos":
                    df_filtrada = df_filtrada[df_filtrada['activo'] != False]
                elif filtro_activo == "Inactivos":
                    df_filtrada = df_filtrada[df_filtrada['activo'] == False]
                if buscar_nombre:
                    df_filtrada = df_filtrada[df_filtrada['nombre_estudiante'].str.contains(buscar_nombre, case=False, na=False)]
                
                columnas = ['nombre_estudiante', 'apellidos_estudiante', 'documento_estudiante', 'curso', 'nivel', 'nombre_acudiente']
                columnas_existentes = [col for col in columnas if col in df_filtrada.columns]
                st.dataframe(df_filtrada[columnas_existentes], use_container_width=True)
                st.caption(f"Mostrando {len(df_filtrada)} de {len(estudiantes)} estudiantes")
                
                # Botón para exportar
                if st.button("📥 Exportar a CSV", key="exportar_estudiantes"):
                    csv = df_filtrada[columnas_existentes].to_csv(index=False).encode('utf-8')
                    st.download_button("Descargar CSV", data=csv, file_name="estudiantes_filtrados.csv", mime="text/csv")
            else:
                st.info("No hay estudiantes registrados")
    
    with tab2:
        st.info("Completa todos los campos obligatorios (*)")
        
        with st.form("form_matricula", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de identidad *")
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
                direccion = st.text_input("Dirección")
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            with col2:
                st.markdown("**Datos del acudiente**")
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Hermano", "Hermana", "Otro"])
                telefono_acudiente = st.text_input("Teléfono del acudiente")
                email_acudiente = st.text_input("Email del acudiente")
                direccion_acudiente = st.text_input("Dirección del acudiente")
            
            st.markdown("**Datos de matrícula**")
            col3, col4 = st.columns(2)
            with col3:
                fecha_matricula = st.date_input("Fecha de matrícula")
            with col4:
                observaciones = st.text_area("Observaciones", height=68)
            
            submitted = st.form_submit_button("💾 Registrar Estudiante", type="primary")
            
            if submitted:
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
                            "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                            "curso": curso,
                            "direccion_estudiante": direccion,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email,
                            "nombre_acudiente": nombre_acudiente,
                            "documento_acudiente": documento_acudiente,
                            "parentesco": parentesco,
                            "telefono_acudiente": telefono_acudiente,
                            "email_acudiente": email_acudiente,
                            "direccion_acudiente": direccion_acudiente,
                            "fecha_matricula": str(fecha_matricula),
                            "observaciones": observaciones,
                            "activo": True
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
                            
                            st.success(f"✅ Estudiante {nombre} {apellidos} matriculado exitosamente")
                            st.info(f"🔑 Usuario: {documento} | Contraseña: demo2026")
                            st.balloons()
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        documento_buscar = st.text_input("Documento de identidad del estudiante", key="buscar_editar_est")
        
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                estudiante = response.json()[0]
                
                with st.form("form_editar_estudiante", clear_on_submit=False):
                    st.success(f"Editando: {estudiante.get('nombre_estudiante', '')} {estudiante.get('apellidos_estudiante', '')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Datos personales**")
                        nombre = st.text_input("Nombre", value=estudiante.get('nombre_estudiante', ''))
                        apellidos = st.text_input("Apellidos", value=estudiante.get('apellidos_estudiante', ''))
                        st.text_input("Documento", value=estudiante.get('documento_estudiante', ''), disabled=True)
                        
                        cursos_opciones = ["901", "902", "903", "1001", "1002", "1003", "1101"]
                        curso_actual = estudiante.get('curso', '901')
                        try:
                            idx_curso = cursos_opciones.index(curso_actual)
                        except ValueError:
                            idx_curso = 0
                        curso = st.selectbox("Curso", cursos_opciones, index=idx_curso)
                        
                        telefono = st.text_input("Teléfono", value=estudiante.get('telefono_estudiante', ''))
                        email = st.text_input("Email", value=estudiante.get('email_estudiante', ''))
                    
                    with col2:
                        st.markdown("**Datos del acudiente**")
                        nombre_acudiente = st.text_input("Nombre del acudiente", value=estudiante.get('nombre_acudiente', ''))
                        documento_acudiente = st.text_input("Documento del acudiente", value=estudiante.get('documento_acudiente', ''))
                        
                        parentesco_opciones = ["", "Padre", "Madre", "Tío", "Tía", "Abuelo", "Abuela", "Otro"]
                        parentesco_actual = estudiante.get('parentesco', '')
                        try:
                            idx_parentesco = parentesco_opciones.index(parentesco_actual)
                        except ValueError:
                            idx_parentesco = 0
                        parentesco = st.selectbox("Parentesco", parentesco_opciones, index=idx_parentesco)
                        
                        telefono_acudiente = st.text_input("Teléfono del acudiente", value=estudiante.get('telefono_acudiente', ''))
                        email_acudiente = st.text_input("Email del acudiente", value=estudiante.get('email_acudiente', ''))
                    
                    activo = st.checkbox("Activo", value=estudiante.get('activo', True))
                    
                    submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
                    
                    if submitted:
                        data_update = {
                            "nombre_estudiante": nombre,
                            "apellidos_estudiante": apellidos,
                            "curso": curso,
                            "telefono_estudiante": telefono,
                            "email_estudiante": email,
                            "nombre_acudiente": nombre_acudiente,
                            "documento_acudiente": documento_acudiente,
                            "parentesco": parentesco,
                            "telefono_acudiente": telefono_acudiente,
                            "email_acudiente": email_acudiente,
                            "activo": activo
                        }
                        
                        update_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento_buscar}"
                        response_update = requests.patch(update_url, headers=headers, json=data_update)
                        
                        if response_update.status_code == 200:
                            st.success("✅ Estudiante actualizado exitosamente")
                            st.rerun()
                        else:
                            st.error(f"Error al actualizar: {response_update.status_code}")
            elif response.status_code == 200:
                st.warning("No se encontró un estudiante con ese documento")
    
    with tab4:
        documento = st.text_input("Documento de identidad del estudiante", key="buscar_baja_est")
        
        if documento:
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                estudiante = response.json()[0]
                nombre = estudiante.get('nombre_estudiante', '')
                apellidos = estudiante.get('apellidos_estudiante', '')
                curso = estudiante.get('curso', '')
                
                st.warning(f"⚠️ Estás a punto de dar de baja a: **{nombre} {apellidos}** (Curso: {curso})")
                
                motivo = st.text_area("Motivo de la baja")
                fecha_baja = st.date_input("Fecha de baja")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar Baja", type="primary"):
                        data_update = {
                            "activo": False,
                            "fecha_baja": str(fecha_baja),
                            "motivo_baja": motivo
                        }
                        update_url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{documento}"
                        response_update = requests.patch(update_url, headers=headers, json=data_update)
                        
                        if response_update.status_code == 200:
                            st.success(f"✅ Estudiante {nombre} {apellidos} dado de baja")
                            st.rerun()
                        else:
                            st.error("Error al dar de baja")
                with col2:
                    if st.button("❌ Cancelar"):
                        st.rerun()
            elif response.status_code == 200:
                st.warning("No se encontró un estudiante con ese documento")


def gestion_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    headers = get_headers()
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista de Docentes", "➕ Contratar", "✏️ Editar", "🚫 Retirar"])
    
    with tab1:
        # Filtros
        st.write("**🔍 Filtros**")
        
        # Definir áreas
        areas = ["Todas", "Ciencias Básicas", "Humanidades", "Ciencias Sociales", "Idiomas", "Artes", "Educación Física", "Técnica"]
        
        # Niveles
        niveles = ["Todos", "Secundaria", "Media"]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            filtro_curso = st.selectbox("Curso", ["Todos", "901", "902", "903", "1001", "1002", "1003", "1101"], key="filtro_curso_doc")
        with col2:
            filtro_area = st.selectbox("Área", areas, key="filtro_area_doc")
        with col3:
            filtro_nivel = st.selectbox("Nivel", niveles, key="filtro_nivel_doc")
        with col4:
            filtro_activo = st.selectbox("Estado", ["Todos", "Activos", "Inactivos"], key="filtro_activo_doc")
        with col5:
            buscar_nombre = st.text_input("Buscar", placeholder="Nombre...", key="buscar_nombre_doc")
        
        # Obtener datos
        response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
        response_asignaciones = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica", headers=headers)
        
        if response_docentes.status_code == 200:
            docentes = response_docentes.json()
            asignaciones = response_asignaciones.json() if response_asignaciones.status_code == 200 else []
            
            if docentes:
                df = pd.DataFrame(docentes)
                
                # Mapeo de cursos a niveles
                nivel_por_curso = {
                    "901": "Secundaria", "902": "Secundaria", "903": "Secundaria",
                    "1001": "Media", "1002": "Media", "1003": "Media", "1101": "Media"
                }
                
                # Mapeo de asignaturas a áreas
                area_por_asignatura = {
                    "Matemáticas": "Ciencias Básicas",
                    "Trigonometría": "Ciencias Básicas",
                    "Cálculo": "Ciencias Básicas",
                    "Física": "Ciencias Básicas",
                    "Química": "Ciencias Básicas",
                    "Biología": "Ciencias Básicas",
                    "Español": "Humanidades",
                    "Literatura": "Humanidades",
                    "Inglés": "Idiomas",
                    "Francés": "Idiomas",
                    "Sociales": "Ciencias Sociales",
                    "Historia": "Ciencias Sociales",
                    "Geografía": "Ciencias Sociales",
                    "Filosofía": "Humanidades",
                    "Ética": "Humanidades",
                    "Artes": "Artes",
                    "Música": "Artes",
                    "Educación Física": "Educación Física",
                    "Deportes": "Educación Física",
                    "Tecnología": "Técnica",
                    "Informática": "Técnica",
                    "Administración": "Técnica",
                    "Proyecto": "Técnica"
                }
                
                # Procesar asignaciones
                docentes_cursos = {}
                docentes_asignaturas = {}
                docentes_niveles = {}
                docentes_areas = {}
                
                for a in asignaciones:
                    doc = a.get('documento_docente')
                    if doc:
                        if doc not in docentes_cursos:
                            docentes_cursos[doc] = set()
                            docentes_asignaturas[doc] = set()
                            docentes_niveles[doc] = set()
                            docentes_areas[doc] = set()
                        
                        curso = a.get('curso')
                        asignatura = a.get('asignatura')
                        
                        if curso:
                            docentes_cursos[doc].add(curso)
                            nivel = nivel_por_curso.get(curso, "Secundaria")
                            docentes_niveles[doc].add(nivel)
                        
                        if asignatura:
                            docentes_asignaturas[doc].add(asignatura)
                            area = area_por_asignatura.get(asignatura, "Otras")
                            docentes_areas[doc].add(area)
                
                df['cursos'] = df['documento_docente'].map(lambda x: ", ".join(sorted(docentes_cursos.get(x, set()))) if x in docentes_cursos else "")
                df['asignaturas'] = df['documento_docente'].map(lambda x: ", ".join(sorted(docentes_asignaturas.get(x, set()))) if x in docentes_asignaturas else "")
                df['niveles'] = df['documento_docente'].map(lambda x: ", ".join(sorted(docentes_niveles.get(x, set()))) if x in docentes_niveles else "")
                df['areas'] = df['documento_docente'].map(lambda x: ", ".join(sorted(docentes_areas.get(x, set()))) if x in docentes_areas else "")
                
                # Aplicar filtros
                df_filtrada = df.copy()
                
                if filtro_curso != "Todos":
                    df_filtrada = df_filtrada[df_filtrada['cursos'].str.contains(filtro_curso, na=False)]
                
                if filtro_area != "Todas":
                    df_filtrada = df_filtrada[df_filtrada['areas'].str.contains(filtro_area, na=False)]
                
                if filtro_nivel != "Todos":
                    df_filtrada = df_filtrada[df_filtrada['niveles'].str.contains(filtro_nivel, na=False)]
                
                if filtro_activo == "Activos":
                    df_filtrada = df_filtrada[df_filtrada['activo'] != False]
                elif filtro_activo == "Inactivos":
                    df_filtrada = df_filtrada[df_filtrada['activo'] == False]
                
                if buscar_nombre:
                    df_filtrada = df_filtrada[df_filtrada['nombre_docente'].str.contains(buscar_nombre, case=False, na=False)]
                
                # Mostrar resultados
                columnas = ['nombre_docente', 'apellidos_docente', 'documento_docente', 'cursos', 'asignaturas', 'niveles', 'areas']
                st.dataframe(df_filtrada[columnas], use_container_width=True)
                st.caption(f"Mostrando {len(df_filtrada)} de {len(docentes)} docentes")
                
                # Botón para exportar
                if st.button("📥 Exportar a CSV", key="exportar_docentes"):
                    csv = df_filtrada[columnas].to_csv(index=False).encode('utf-8')
                    st.download_button("Descargar CSV", data=csv, file_name="docentes_filtrados.csv", mime="text/csv")
            else:
                st.info("No hay docentes registrados")
    
    with tab2:
        st.info("Completa todos los campos obligatorios (*)")
        
        with st.form("form_contratar", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Datos personales**")
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento de identidad *")
                fecha_nacimiento = st.date_input("Fecha de nacimiento", value=None)
                sexo = st.selectbox("Sexo", ["", "Masculino", "Femenino"])
                direccion = st.text_input("Dirección")
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
            
            with col2:
                st.markdown("**Datos profesionales**")
                titulo = st.text_input("Título profesional")
                especializacion = st.text_input("Especialización")
                tipo_contrato = st.selectbox("Tipo de contrato", ["", "Planta", "Contrato", "Cátedra", "Ocasional"])
                fecha_ingreso = st.date_input("Fecha de ingreso")
                salario = st.number_input("Salario", min_value=0, step=100000)
                observaciones = st.text_area("Observaciones", height=68)
            
            submitted = st.form_submit_button("💾 Contratar Docente", type="primary")
            
            if submitted:
                if not all([nombre, apellidos, documento]):
                    st.error("❌ Completa todos los campos obligatorios (*)")
                else:
                    check_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento}"
                    check_response = requests.get(check_url, headers=headers)
                    
                    if check_response.status_code == 200 and check_response.json():
                        st.error(f"❌ Ya existe un docente con el documento {documento}")
                    else:
                        data_docente = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "documento_docente": documento,
                            "fecha_nacimiento": str(fecha_nacimiento) if fecha_nacimiento else None,
                            "sexo_docente": sexo,
                            "direccion_docente": direccion,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "titulo": titulo,
                            "especializacion": especializacion,
                            "tipo_contrato": tipo_contrato,
                            "fecha_ingreso": str(fecha_ingreso) if fecha_ingreso else None,
                            "salario": salario if salario > 0 else None,
                            "observaciones": observaciones,
                            "activo": True
                        }
                        
                        response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data_docente)
                        
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
                            
                            st.success(f"✅ Docente {nombre} {apellidos} contratado exitosamente")
                            st.info(f"🔑 Usuario: {username} | Contraseña: demo2026")
                            st.balloons()
                        else:
                            st.error(f"Error al registrar: {response.status_code}")
    
    with tab3:
        documento_buscar = st.text_input("Documento de identidad del docente", key="buscar_editar_doc")
        
        if documento_buscar:
            url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                docente = response.json()[0]
                
                with st.form("form_editar_docente", clear_on_submit=False):
                    st.success(f"Editando: {docente.get('nombre_docente', '')} {docente.get('apellidos_docente', '')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Datos personales**")
                        nombre = st.text_input("Nombre", value=docente.get('nombre_docente', ''))
                        apellidos = st.text_input("Apellidos", value=docente.get('apellidos_docente', ''))
                        st.text_input("Documento", value=docente.get('documento_docente', ''), disabled=True)
                        telefono = st.text_input("Teléfono", value=docente.get('telefono_docente', ''))
                        email = st.text_input("Email", value=docente.get('email_docente', ''))
                        direccion = st.text_input("Dirección", value=docente.get('direccion_docente', ''))
                    
                    with col2:
                        st.markdown("**Datos profesionales**")
                        titulo = st.text_input("Título", value=docente.get('titulo', ''))
                        especializacion = st.text_input("Especialización", value=docente.get('especializacion', ''))
                        
                        contrato_opciones = ["", "Planta", "Contrato", "Cátedra", "Ocasional"]
                        contrato_actual = docente.get('tipo_contrato', '')
                        try:
                            idx_contrato = contrato_opciones.index(contrato_actual)
                        except ValueError:
                            idx_contrato = 0
                        tipo_contrato = st.selectbox("Tipo de contrato", contrato_opciones, index=idx_contrato)
                    
                    activo = st.checkbox("Activo", value=docente.get('activo', True))
                    
                    submitted = st.form_submit_button("💾 Guardar Cambios", type="primary")
                    
                    if submitted:
                        data_update = {
                            "nombre_docente": nombre,
                            "apellidos_docente": apellidos,
                            "telefono_docente": telefono,
                            "email_docente": email,
                            "direccion_docente": direccion,
                            "titulo": titulo,
                            "especializacion": especializacion,
                            "tipo_contrato": tipo_contrato,
                            "activo": activo
                        }
                        
                        update_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento_buscar}"
                        response_update = requests.patch(update_url, headers=headers, json=data_update)
                        
                        if response_update.status_code == 200:
                            st.success("✅ Docente actualizado exitosamente")
                            st.rerun()
                        else:
                            st.error(f"Error al actualizar: {response_update.status_code}")
            elif response.status_code == 200:
                st.warning("No se encontró un docente con ese documento")
    
    with tab4:
        documento = st.text_input("Documento de identidad del docente", key="buscar_retiro_doc")
        
        if documento:
            url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                docente = response.json()[0]
                nombre = docente.get('nombre_docente', '')
                apellidos = docente.get('apellidos_docente', '')
                
                st.warning(f"⚠️ Estás a punto de retirar a: **{nombre} {apellidos}**")
                
                motivo = st.text_area("Motivo del retiro")
                fecha_retiro = st.date_input("Fecha de retiro")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar Retiro", type="primary"):
                        data_update = {
                            "activo": False,
                            "fecha_retiro": str(fecha_retiro),
                            "motivo_retiro": motivo
                        }
                        update_url = f"{SUPABASE_URL}/rest/v1/docentes?documento_docente=eq.{documento}"
                        response_update = requests.patch(update_url, headers=headers, json=data_update)
                        
                        if response_update.status_code == 200:
                            st.success(f"✅ Docente {nombre} {apellidos} retirado")
                            st.rerun()
                        else:
                            st.error("Error al retirar")
                with col2:
                    if st.button("❌ Cancelar"):
                        st.rerun()
            elif response.status_code == 200:
                st.warning("No se encontró un docente con ese documento")


def gestion_cursos():
    st.subheader("📚 Gestión de Cursos")
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    for curso in cursos:
        with st.expander(f"Curso {curso}"):
            st.write(f"**Asignaturas del curso {curso}:**")
            headers = get_headers()
            url = f"{SUPABASE_URL}/rest/v1/docentes?curso=eq.{curso}&select=asignatura,nombre_docente"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                materias = response.json()
                if materias:
                    for m in materias:
                        st.write(f"- {m.get('asignatura')}: {m.get('nombre_docente')}")
                else:
                    st.write("Sin asignaturas asignadas")


def consultar_horarios():
    st.subheader("📅 Consultar Horarios")
    
    headers = get_headers()
    
    tipo = st.radio("Ver horario de:", ["Curso", "Docente"], key="horario_tipo")
    
    if tipo == "Curso":
        cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
