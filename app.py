# ============================================
# app.py - ORQUESTADOR PRINCIPAL & UI MODERNA
# ============================================

import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers

# =============================================
# IMPORTAR MÓDULOS
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

# =============================================
# CONFIGURACIÓN DE PÁGINA (PANTALLA COMPLETA)
# =============================================
ES_MOVIL = es_movil()

st.set_page_config(
    page_title="Agenda Escolar | Plataforma Educativa",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

if ES_MOVIL:
    aplicar_css_movil()

# =============================================
# ESTILOS CSS PERSONALIZADOS (ESTÉTICA MODERNA)
# =============================================
st.markdown("""
<style>
    /* Estilos globales */
    .main {
        background-color: #F8FAFC;
    }
    
    /* Encabezado y títulos */
    h1, h2, h3 {
        color: #0F172A;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Tarjeta de usuario en el sidebar */
    .user-badge {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        padding: 16px;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .user-badge h4 {
        margin: 0;
        color: #F8FAFC;
        font-size: 1rem;
    }
    .user-badge p {
        margin: 4px 0 0 0;
        color: #94A3B8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Botones primarios y de navegación */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    /* Ocultar menú nativo innecesario */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================
# CONTROL DE SESIÓN
# =============================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login.mostrar_login()
else:
    # Sincronizar permisos y roles con Supabase
    username = st.session_state.usuario
    headers = get_headers()
    
    try:
        url = f"{SUPABASE_URL}/rest/v1/usuarios_login?username=eq.{username}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json():
            user_data = response.json()[0]
            st.session_state.user_data['roles'] = user_data.get('roles', [])
            st.session_state.user_data['rol'] = user_data.get('rol', '')
            
            if st.session_state.get('rol_actual') not in st.session_state.user_data['roles']:
                st.session_state.rol_actual = st.session_state.user_data['roles'][0] if st.session_state.user_data['roles'] else ''
    except Exception:
        pass

    rol_actual = st.session_state.get('rol_actual', st.session_state.user_data.get('rol', ''))

    # =============================================
    # BARRA LATERAL (SIDEBAR COMÚN)
    # =============================================
    with st.sidebar:
        # Ficha elegante del usuario
        st.markdown(f"""
        <div class="user-badge">
            <h4>👤 {username}</h4>
            <p>Rol Activo: <b>{rol_actual.replace('_grupo', '').upper()}</b></p>
        </div>
        """, unsafe_allow_html=True)

        # Selector de perfil múltiple (si aplica)
        user_roles = [r for r in st.session_state.user_data.get('roles', []) if r]
        if len(user_roles) > 1:
            st.caption("🔄 CAMBIAR PERFIL")
            nuevo_rol = st.selectbox(
                "Selecciona rol de trabajo",
                options=user_roles,
                index=user_roles.index(rol_actual) if rol_actual in user_roles else 0,
                format_func=lambda x: f"🎓 {x.replace('_grupo', '').capitalize()}",
                label_visibility="collapsed"
            )
            if nuevo_rol != rol_actual:
                st.session_state.rol_actual = nuevo_rol
                st.rerun()
            st.divider()

    # =============================================
    # NAVEGACIÓN Y VISTAS PARA ADMINISTRADOR
    # =============================================
    if rol_actual == 'admin':
        with st.sidebar:
            st.caption("📌 MENÚ ADMINISTRATIVO")
            
            # Navegación compacta por categorías
            categoria = st.radio(
                "Módulos del Sistema",
                options=[
                    "📊 Panel General",
                    "👥 Comunidad Escolar",
                    "📚 Gestión Académica",
                    "⏰ Horarios y Jornadas",
                    "⚙️ Institución y Festivos"
                ],
                label_visibility="collapsed"
            )

            st.divider()
            if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
                st.session_state.logged_in = False
                st.rerun()

        # Renderizado de vistas según la categoría seleccionada
        if categoria == "📊 Panel General":
            admin.mostrar(st.session_state.user_data)
            
        elif categoria == "👥 Comunidad Escolar":
            sub_comunidad = st.radio("Gestión de personas:", ["Estudiantes y Matrículas", "Docentes"], horizontal=True)
            if sub_comunidad == "Estudiantes y Matrículas":
                admin.gestion_estudiantes()
            else:
                admin.gestion_docentes()

        elif categoria == "📚 Gestión Académica":
            sub_acad = st.radio("Configuración académica:", ["Niveles", "Asignaturas", "Cursos / Grados", "Directores de Grupo", "Asignación Docente"], horizontal=True)
            if sub_acad == "Niveles":
                admin.configurar_niveles()
            elif sub_acad == "Asignaturas":
                admin.gestionar_asignaturas()
            elif sub_acad == "Cursos / Grados":
                admin.gestionar_grados()
            elif sub_acad == "Directores de Grupo":
                admin.gestion_directores_grupo()
            elif sub_acad == "Asignación Docente":
                admin.asignar_docentes_curso()

        elif categoria == "⏰ Horarios y Jornadas":
            sub_horarios = st.radio("Horarios:", ["Franjas por Nivel", "Jornadas Laborales", "Horarios por Curso"], horizontal=True)
            if sub_horarios == "Franjas por Nivel":
                admin.configurar_horas_nivel()
            elif sub_horarios == "Jornadas Laborales":
                admin.configurar_jornada_nivel()
            elif sub_horarios == "Horarios por Curso":
                admin.configurar_horario_curso()

        elif categoria == "⚙️ Institución y Festivos":
            sub_inst = st.radio("Ajustes generales:", ["Datos del Colegio", "Calendario y Festivos", "Reportes Globales"], horizontal=True)
            if sub_inst == "Datos del Colegio":
                admin.mostrar_sistema()
            elif sub_inst == "Calendario y Festivos":
                admin.gestion_festivos()
            elif sub_inst == "Reportes Globales":
                admin.reportes_academicos()

    # =============================================
    # VISTAS PARA OTROS ROLES (DOCENTE, FAMILIA, ETC.)
    # =============================================
    else:
        with st.sidebar:
            st.divider()
            if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
                st.session_state.logged_in = False
                st.rerun()

        ROLES_VALIDOS = {
            'estudiante': estudiante.mostrar,
            'docente': docente.mostrar,
            'acudiente': acudiente.mostrar,
            'director': director.mostrar,
            'coordinador': coordinador.mostrar,
            'secretaria': secretaria.mostrar,
            'supervisor': supervisor.mostrar
        }

        vista_func = ROLES_VALIDOS.get(rol_actual)
        if vista_func:
            vista_func(st.session_state.user_data)
        else:
            st.error(f"⚠️ Rol no reconocido: {rol_actual}")
            st.info("Roles válidos en el sistema: " + ", ".join(ROLES_VALIDOS.keys()))
