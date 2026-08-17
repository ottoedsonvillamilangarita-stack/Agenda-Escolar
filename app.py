import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers
from modulos.paneles import admin, docente, estudiante, acudiente, director, coordinador, secretaria, supervisor
from modulos.shared import auth as login
from modulos.shared.mobile_utils import es_movil, aplicar_css_movil 
# app.py
# app.py
import modulos.paneles.admin as admin
import modulos.paneles.docente as docente
import modulos.paneles.estudiante as estudiante
import modulos.paneles.acudiente as acudiente
import modulos.paneles.director as director
import modulos.paneles.coordinador as coordinador
import modulos.paneles.secretaria as secretaria
import modulos.paneles.supervisor as supervisor
from modulos.shared import auth as login

# Configuración según dispositivo
ES_MOVIL = es_movil()

if ES_MOVIL:
    st.set_page_config(page_title="Plataforma Escolar", layout="centered", initial_sidebar_state="collapsed")
    aplicar_css_movil()
else:
    st.set_page_config(page_title="Plataforma Escolar", layout="wide")

# Inicializar session_state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login.mostrar_login()
else:
    # =============================================
    # ACTUALIZAR ROLES DESDE LA BASE DE DATOS
    # =============================================
    username = st.session_state.usuario
    headers = get_headers()
    
    url = f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{username}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200 and response.json():
        user_data = response.json()[0]
        st.session_state.user_data['roles'] = user_data.get('roles', [])
        st.session_state.user_data['rol'] = user_data.get('rol', '')
        
        if st.session_state.get('rol_actual') not in st.session_state.user_data['roles']:
            st.session_state.rol_actual = st.session_state.user_data['roles'][0] if st.session_state.user_data['roles'] else ''
    
    # Barra lateral
    st.sidebar.title("📚 Plataforma Escolar")
    st.sidebar.write(f"👤 {st.session_state.usuario}")
    
    user_roles = st.session_state.user_data.get('roles', [])
    user_roles = [r for r in user_roles if r]
    
    rol_actual = st.session_state.get('rol_actual', st.session_state.user_data.get('rol'))
    
    if len(user_roles) > 1:
        st.sidebar.write("---")
        st.sidebar.write("🔄 **Cambiar perfil:**")
        for rol in user_roles:
            # Mostrar el rol con un nombre más amigable
            nombre_mostrar = rol.replace('_grupo', '')
            if st.sidebar.button(f"🔁 {nombre_mostrar.upper()}", key=f"cambiar_{rol}", 
                                 disabled=(rol == rol_actual),
                                 use_container_width=True):
                st.session_state.rol_actual = rol
                st.rerun()
           st.sidebar.write("---")
    if st.sidebar.button("Cerrar sesión", use_container_width=True):
           if st.sidebar.button("Cerrar sesión", use_container_width=True):
           # =============================================
    # MENÚ ESPECÍFICO PARA ADMINISTRADOR
    # =============================================
    if rol_actual == 'admin':
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
    
    # Redirección por rol (CONVERSIÓN DE NOMBRES)
    ROLES_VALIDOS = ['estudiante', 'docente', 'acudiente', 'director', 'coordinador', 'secretaria', 'supervisor', 'admin']
    # Redirección por rol (CONVERSIÓN DE NOMBRES)
    ROLES_VALIDOS = ['estudiante', 'docente', 'acudiente', 'director', 'coordinador', 'secretaria', 'supervisor', 'admin']
    
    # Convertir director_grupo a director para el módulo
    if rol_actual == 'director_grupo':
        rol_actual = 'director'
        st.session_state.rol_actual = 'director'
    
    if rol_actual in ROLES_VALIDOS:
        if rol_actual == 'estudiante':
            estudiante.mostrar(st.session_state.user_data)
        elif rol_actual == 'docente':
            docente.mostrar(st.session_state.user_data)
        elif rol_actual == 'acudiente':
            acudiente.mostrar(st.session_state.user_data)
        elif rol_actual == 'director':
            director.mostrar(st.session_state.user_data)
        elif rol_actual == 'coordinador':
            coordinador.mostrar(st.session_state.user_data)
        elif rol_actual == 'secretaria':
            secretaria.mostrar(st.session_state.user_data)
        elif rol_actual == 'supervisor':
            supervisor.mostrar(st.session_state.user_data)
        elif rol_actual == 'admin':
            admin.mostrar(st.session_state.user_data)
    else:
        st.error(f"⚠️ Rol no reconocido: {rol_actual}")
        st.info("📌 Roles disponibles: " + ", ".join(ROLES_VALIDOS))
        if st.button("Volver a login"):
            st.session_state.logged_in = False
            st.rerun()
        st.session_state.logged_in = False
        st.rerun()
    
    # Redirección por rol (CONVERSIÓN DE NOMBRES)
    ROLES_VALIDOS = ['estudiante', 'docente', 'acudiente', 'director', 'coordinador', 'secretaria', 'supervisor', 'admin']
    
    # Convertir director_grupo a director para el módulo
    if rol_actual == 'director_grupo':
        rol_actual = 'director'
        st.session_state.rol_actual = 'director'
    
    if rol_actual in ROLES_VALIDOS:
        if rol_actual == 'estudiante':
            estudiante.mostrar(st.session_state.user_data)
        elif rol_actual == 'docente':
            docente.mostrar(st.session_state.user_data)
        elif rol_actual == 'acudiente':
            acudiente.mostrar(st.session_state.user_data)
        elif rol_actual == 'director':
            director.mostrar(st.session_state.user_data)
        elif rol_actual == 'coordinador':
            coordinador.mostrar(st.session_state.user_data)
        elif rol_actual == 'secretaria':
            secretaria.mostrar(st.session_state.user_data)
        elif rol_actual == 'supervisor':
            supervisor.mostrar(st.session_state.user_data)
        elif rol_actual == 'admin':
            admin.mostrar(st.session_state.user_data)
    else:
        st.error(f"⚠️ Rol no reconocido: {rol_actual}")
        st.info("📌 Roles disponibles: " + ", ".join(ROLES_VALIDOS))
        if st.button("Volver a login"):
            st.session_state.logged_in = False
            st.rerun()


