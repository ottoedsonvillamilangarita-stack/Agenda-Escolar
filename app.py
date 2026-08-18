# app.py (sección del menú para admin)
if rol_actual == 'admin':
    st.sidebar.title("📚 Plataforma Escolar")
    st.sidebar.write(f"👤 {st.session_state.usuario}")
    st.sidebar.write(f"📌 Rol: ADMIN")
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("📊 General")
    if st.sidebar.button("Dashboard", use_container_width=True):
        admin.mostrar_dashboard()
    
    st.sidebar.subheader("👥 Recursos Humanos")
    if st.sidebar.button("Docentes", use_container_width=True):
        admin.gestion_docentes()
    if st.sidebar.button("Estudiantes", use_container_width=True):
        admin.gestion_estudiantes()
    
    st.sidebar.subheader("📚 Académico")
    if st.sidebar.button("Niveles", use_container_width=True):
        admin.configurar_niveles()
    if st.sidebar.button("Asignaturas", use_container_width=True):
        admin.gestionar_asignaturas()
    if st.sidebar.button("Asignar Pénsum", use_container_width=True):
        admin.asignar_pensum_nivel()
    if st.sidebar.button("Asignar Docentes", use_container_width=True):
        admin.asignar_docentes_curso()
    if st.sidebar.button("Cursos", use_container_width=True):
        admin.gestionar_grados()
    if st.sidebar.button("Directores de Grupo", use_container_width=True):
        admin.gestion_directores_grupo()
    
    st.sidebar.subheader("⏰ Horarios")
    if st.sidebar.button("Horas por Nivel", use_container_width=True):
        admin.configurar_horas_nivel()
    if st.sidebar.button("Días Laborales", use_container_width=True):
        admin.configurar_jornada_nivel()
    if st.sidebar.button("Asignar Horarios", use_container_width=True):
        admin.configurar_horario_curso()
    
    st.sidebar.subheader("⚙️ Configuración")
    if st.sidebar.button("Datos del Colegio", use_container_width=True):
        admin.mostrar_sistema()
    if st.sidebar.button("Festivos", use_container_width=True):
        admin.gestion_festivos()
    
    st.sidebar.subheader("📊 Reportes")
    if st.sidebar.button("Reportes Académicos", use_container_width=True):
        admin.reportes_academicos()
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    
    # Mostrar el panel del administrador
    admin.mostrar(st.session_state.user_data)
