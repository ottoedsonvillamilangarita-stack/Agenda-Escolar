import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers

# =============================================
# IMPORTAR MÓDULOS - IMPORTS DIRECTOS (SIN __init__)
# =============================================
import modulos.paneles.admin as admin
import modulos.paneles.docente as docente
import modulos.paneles.estudiante as estudiante
import modulos.paneles.acudiente as acudiente
import modulos.paneles.director as director
import modulos.paneles.coordinador as coordinador
import modulos.paneles.secretaria as secretaria
import modulos.paneles.supervisor as supervisor

from modulos.shared import auth as login
from modulos.shared.mobile_utils import es_movil, aplicar_css_movil

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
    
    # =============================================
    # DEFINIR rol_actual ANTES DE USARLO
    # =============================================
    rol_actual = st.session_state.get('rol_actual', st.session_state.user_data.get('rol'))
    
    # =============================================
    # MENÚ PARA ADMINISTRADOR
    # =============================================
    if rol_actual == 'admin':
        st.sidebar.title("📚 Plataforma Escolar")
        st.sidebar.write(f"👤 {st.session_state.usuario}")
        st.sidebar.write(f"📌 Rol: ADMIN")
        st.sidebar.markdown("---")
        
        st.sidebar.subheader("📊 General")
        if st.sidebar.button("Dashboard", use_container_width=True):
            st.session_state.admin_seccion = "dashboard"
            st.rerun()
        
        st.sidebar.subheader("👥 Recursos Humanos")
        if st.sidebar.button("Docentes", use_container_width=True):
            st.session_state.admin_seccion = "docentes"
            st.rerun()
        if st.sidebar.button("Estudiantes", use_container_width=True):
            st.session_state.admin_seccion = "estudiantes"
            st.rerun()
        
        st.sidebar.subheader("📚 Académico")
        if st.sidebar.button("Niveles", use_container_width=True):
            st.session_state.admin_seccion = "niveles"
            st.rerun()
        if st.sidebar.button("Asignaturas", use_container_width=True):
            st.session_state.admin_seccion = "asignaturas"
            st.rerun()
        if st.sidebar.button("Asignar Pénsum", use_container_width=True):
            st.session_state.admin_seccion = "pensum"
            st.rerun()
        if st.sidebar.button("Asignar Docentes", use_container_width=True):
            st.session_state.admin_seccion = "asignar_docentes"
            st.rerun()
        if st.sidebar.button("Cursos", use_container_width=True):
            st.session_state.admin_seccion = "cursos"
            st.rerun()
        if st.sidebar.button("Directores de Grupo", use_container_width=True):
            st.session_state.admin_seccion = "directores"
            st.rerun()
        
        st.sidebar.subheader("⏰ Horarios")
        if st.sidebar.button("Horas por Nivel", use_container_width=True):
            st.session_state.admin_seccion = "horas_nivel"
            st.rerun()
        if st.sidebar.button("Días Laborales", use_container_width=True):
            st.session_state.admin_seccion = "dias_laborales"
            st.rerun()
        if st.sidebar.button("Asignar Horarios", use_container_width=True):
            st.session_state.admin_seccion = "horarios"
            st.rerun()
        
        st.sidebar.subheader("⚙️ Configuración")
        if st.sidebar.button("Datos del Colegio", use_container_width=True):
            st.session_state.admin_seccion = "sistema"
            st.rerun()
        if st.sidebar.button("Festivos", use_container_width=True):
            st.session_state.admin_seccion = "festivos"
            st.rerun()
        
        st.sidebar.subheader("📊 Reportes")
        if st.sidebar.button("Reportes Académicos", use_container_width=True):
            st.session_state.admin_seccion = "reportes"
            st.rerun()
        
        st.sidebar.markdown("---")
        if st.sidebar.button("Cerrar sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
        # =============================================
        # MOSTRAR EL CONTENIDO SEGÚN LA SECCIÓN
        # =============================================
        seccion = st.session_state.get("admin_seccion", "dashboard")
        
        if seccion == "dashboard":
            admin.mostrar(st.session_state.user_data)
        elif seccion == "estudiantes":
            admin.gestion_estudiantes()
        elif seccion == "docentes":
            admin.gestion_docentes()
        elif seccion == "niveles":
            admin.configurar_niveles()
        elif seccion == "asignaturas":
            admin.gestionar_asignaturas()
        elif seccion == "pensum":
            admin.asignar_pensum_nivel()
        elif seccion == "asignar_docentes":
            admin.asignar_docentes_curso()
        elif seccion == "cursos":
            admin.gestionar_grados()
        elif seccion == "directores":
            admin.gestion_directores_grupo()
        elif seccion == "horas_nivel":
            admin.configurar_horas_nivel()
        elif seccion == "dias_laborales":
            admin.configurar_jornada_nivel()
        elif seccion == "horarios":
            admin.configurar_horario_curso()
        elif seccion == "sistema":
            admin.mostrar_sistema()
        elif seccion == "festivos":
            admin.gestion_festivos()
        elif seccion == "reportes":
            admin.reportes_academicos()
        else:
            admin.mostrar(st.session_state.user_data)
    
    # =============================================
    # MENÚ PARA OTROS ROLES
    # =============================================
    else:
        st.sidebar.title("📚 Plataforma Escolar")
        st.sidebar.write(f"👤 {st.session_state.usuario}")
        
        user_roles = st.session_state.user_data.get('roles', [])
        user_roles = [r for r in user_roles if r]
        
        if len(user_roles) > 1:
            st.sidebar.write("---")
            st.sidebar.write("🔄 **Cambiar perfil:**")
            for rol in user_roles:
                nombre_mostrar = rol.replace('_grupo', '')
                if st.sidebar.button(f"🔁 {nombre_mostrar.upper()}", key=f"cambiar_{rol}", 
                                     disabled=(rol == rol_actual),
                                     use_container_width=True):
                    st.session_state.rol_actual = rol
                    st.rerun()
            st.sidebar.write("---")
            st.sidebar.write(f"**Perfil actual:** {rol_actual.replace('_grupo', '').upper()}")
        else:
            st.sidebar.write(f"📌 Rol: {rol_actual.replace('_grupo', '').upper()}")
        
        st.sidebar.write("---")
        if st.sidebar.button("Cerrar sesión", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
        # =============================================
        # REDIRECCIÓN POR ROL (PARA NO ADMINISTRADORES)
        # =============================================
        ROLES_VALIDOS = ['estudiante', 'docente', 'acudiente', 'director', 'coordinador', 'secretaria', 'supervisor']
        
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
        else:
            st.error(f"⚠️ Rol no reconocido: {rol_actual}")
            st.info("📌 Roles disponibles: " + ", ".join(ROLES_VALIDOS))
            if st.button("Volver a login"):
                st.session_state.logged_in = False
                st.rerun()
