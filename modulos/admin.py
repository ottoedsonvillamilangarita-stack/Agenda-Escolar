# ... (código anterior hasta las funciones específicas)

# ============================================
# SECCIÓN 2: GESTIÓN DE ALUMNOS (SIMPLIFICADA)
# ============================================
def mostrar_gestion_alumnos():
    st.subheader("👨‍🎓 Gestión de Alumnos")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista", "➕ Nuevo Alumno", "✏️ Editar", "📥 Carga Masiva"])
    
    with tab2:
        st.write("**Registrar nuevo alumno**")
        st.info("📌 Los campos marcados con * son obligatorios")
        
        with st.form("nuevo_alumno"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
            with col2:
                nombre_acudiente = st.text_input("Nombre del acudiente *")
                documento_acudiente = st.text_input("Documento del acudiente *")
                parentesco = st.selectbox("Parentesco", ["", "Padre", "Madre", "Tío", "Abuelo", "Otro"])
                telefono = st.text_input("Teléfono del acudiente (opcional)")
            
            if st.form_submit_button("💾 Guardar Alumno", type="primary"):
                if not all([nombre, apellidos, documento, curso, nombre_acudiente, documento_acudiente]):
                    st.error("❌ Por favor completa todos los campos obligatorios")
                else:
                    # Guardar alumno
                    headers = get_headers()
                    data_alumno = {
                        "nombre_estudiante": nombre,
                        "apellidos_estudiante": apellidos,
                        "documento_estudiante": documento,
                        "curso": curso,
                        "nombre_acudiente": nombre_acudiente,
                        "documento_acudiente": documento_acudiente,
                        "parentesco": parentesco,
                        "telefono_acudiente": telefono
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/estudiantes", headers=headers, json=data_alumno)
                    
                    if response.status_code == 201:
                        # Crear usuario para el alumno
                        user_alumno = {
                            "username": documento,
                            "password_hash": "demo2026",
                            "rol": "estudiante",
                            "documento": documento
                        }
                        requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_alumno)
                        
                        # Crear/actualizar usuario para el acudiente
                        user_acudiente = {
                            "username": nombre_acudiente.replace(" ", "_"),
                            "password_hash": "demo2026",
                            "rol": "acudiente",
                            "documento": documento_acudiente
                        }
                        requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_acudiente)
                        
                        st.success(f"✅ Alumno {nombre} registrado exitosamente")
                        st.info(f"🔑 Usuario alumno: {documento} | Contraseña: demo2026")
                        st.info(f"🔑 Usuario acudiente: {nombre_acudiente.replace(' ', '_')} | Contraseña: demo2026")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")

# ============================================
# SECCIÓN 4: GESTIÓN DE DOCENTES (SIMPLIFICADA)
# ============================================
def mostrar_gestion_docentes():
    st.subheader("👨‍🏫 Gestión de Docentes")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista", "➕ Nuevo Docente", "✏️ Editar", "📥 Carga Masiva"])
    
    with tab2:
        st.write("**Registrar nuevo docente**")
        st.info("📌 Los campos marcados con * son obligatorios")
        
        with st.form("nuevo_docente"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *")
                apellidos = st.text_input("Apellidos *")
                documento = st.text_input("Documento *")
                curso = st.selectbox("Curso *", ["901", "902", "903", "1001", "1002", "1003", "1101"])
            with col2:
                asignatura = st.text_input("Asignatura *")
                intensidad = st.number_input("Intensidad (horas)", min_value=1, max_value=10, value=4)
                telefono = st.text_input("Teléfono (opcional)")
                email = st.text_input("Email (opcional)")
            
            if st.form_submit_button("💾 Guardar Docente", type="primary"):
                if not all([nombre, apellidos, documento, curso, asignatura]):
                    st.error("❌ Por favor completa todos los campos obligatorios")
                else:
                    headers = get_headers()
                    data = {
                        "nombre_docente": nombre,
                        "apellidos_docente": apellidos,
                        "documento_docente": documento,
                        "curso": curso,
                        "asignatura": asignatura,
                        "intensidad": str(intensidad),
                        "telefono_docente": telefono,
                        "email_docente": email
                    }
                    response = requests.post(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers, json=data)
                    
                    if response.status_code == 201:
                        # Crear usuario para el docente
                        user_docente = {
                            "username": nombre.replace(" ", "_"),
                            "password_hash": "demo2026",
                            "rol": "docente",
                            "documento": documento
                        }
                        requests.post(f"{SUPABASE_URL}/rest/v1/usuarios_login", headers=headers, json=user_docente)
                        
                        st.success(f"✅ Docente {nombre} registrado exitosamente")
                        st.info(f"🔑 Usuario: {nombre.replace(' ', '_')} | Contraseña: demo2026")
                    else:
                        st.error(f"Error: {response.status_code}")

# ============================================
# SECCIÓN 3: GESTIÓN DE ACUDIENTES (SOLO VISUALIZACIÓN)
# ============================================
def mostrar_gestion_acudientes():
    st.subheader("👨‍👩‍👧 Gestión de Acudientes")
    st.info("📌 Los acudientes se crean automáticamente al registrar alumnos")
    
    tab1, tab2 = st.tabs(["📋 Lista de Acudientes", "✏️ Editar Información"])
    
    with tab1:
        headers = get_headers()
        url = f"{SUPABASE_URL}/rest/v1/estudiantes"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            alumnos = response.json()
            acudientes_dict = {}
            for alumno in alumnos:
                doc_acud = alumno.get('documento_acudiente')
                if doc_acud and doc_acud not in acudientes_dict:
                    acudientes_dict[doc_acud] = {
                        "nombre": alumno.get('nombre_acudiente'),
                        "documento": doc_acud,
                        "telefono": alumno.get('telefono_acudiente'),
                        "parentesco": alumno.get('parentesco'),
                        "hijos": []
                    }
                if doc_acud:
                    acudientes_dict[doc_acud]["hijos"].append(alumno.get('nombre_estudiante'))
            
            if acudientes_dict:
                df = pd.DataFrame([{
                    "Nombre": v["nombre"],
                    "Documento": v["documento"],
                    "Teléfono": v["telefono"],
                    "Parentesco": v["parentesco"],
                    "Hijos": ", ".join(v["hijos"])
                } for v in acudientes_dict.values()])
                st.dataframe(df, use_container_width=True)
                st.caption(f"Total: {len(acudientes_dict)} acudientes")
            else:
                st.info("No hay acudientes registrados")
    
    with tab2:
        st.write("**Buscar acudiente por documento**")
        buscar = st.text_input("Documento del acudiente")
        
        if buscar:
            headers = get_headers()
            url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_acudiente=eq.{buscar}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200 and response.json():
                hijos = response.json()
                acudiente = hijos[0]
                
                with st.form("editar_acudiente"):
                    nombre = st.text_input("Nombre", acudiente.get('nombre_acudiente', ''))
                    telefono = st.text_input("Teléfono", acudiente.get('telefono_acudiente', ''))
                    
                    st.write("**Hijos asociados:**")
                    for hijo in hijos:
                        st.write(f"- {hijo.get('nombre_estudiante')} - {hijo.get('curso')}")
                    
                    if st.form_submit_button("💾 Actualizar Acudiente", type="primary"):
                        for hijo in hijos:
                            data = {
                                "nombre_acudiente": nombre,
                                "telefono_acudiente": telefono
                            }
                            url_update = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_estudiante=eq.{hijo.get('documento_estudiante')}"
                            requests.patch(url_update, headers=headers, json=data)
                        
                        st.success("✅ Acudiente actualizado exitosamente")
            else:
                st.warning("Acudiente no encontrado")
