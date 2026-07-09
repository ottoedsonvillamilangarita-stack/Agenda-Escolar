import streamlit as st 
import requests
import pandas as pd
from utils import SUPABASE_URL, get_headers
from modulos.features.calificaciones import mostrar_configuracion_notas, mostrar_ingreso_notas
from modulos.features.asistencia import mostrar_asistencia_docente
from modulos.features.reportes import mostrar_reportes_docente
from modulos.features.horarios import mostrar_horario_docente_tabla
from modulos import mensajeria


def mostrar(data):

    st.title("👨‍🏫 Panel del Docente")
    
    documento_docente = data.get('documento')
    st.write(f"Bienvenido, {data.get('username', 'Docente')}")
    
    headers = get_headers()
    
    # Obtener asignaciones
    url = f"{SUPABASE_URL}/rest/v1/asignacion_academica?documento_docente=eq.{documento_docente}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error("Error al cargar datos")
        return
    
    asignaciones = response.json()
    
    if not asignaciones:
        st.warning("No tienes asignaciones académicas")
        return
    
   # Mostrar si es director - FORZAR ACTUALIZACIÓN
direcciones = [a for a in asignaciones if a.get('asignatura') == 'Dirección de Curso']

if direcciones:
    st.success("🎓 Eres Director de Curso")
    
    # FORZAR ACTUALIZACIÓN DE user_roles si no tiene el rol
    username = data.get('username')
    check_rol_url = f"{SUPABASE_URL}/rest/v1/user_roles?username=eq.{username}&rol=eq.director_grupo"
    check_rol_resp = requests.get(check_rol_url, headers=get_headers())
    
    if check_rol_resp.status_code == 200 and not check_rol_resp.json():
        # El usuario tiene asignación pero no el rol → agregarlo
        requests.post(
            f"{SUPABASE_URL}/rest/v1/user_roles",
            headers=get_headers(),
            json={"username": username, "rol": "director_grupo"}
        )
        st.rerun()
    
    for d in direcciones:
        st.info(f"📌 Curso: {d.get('curso')}")
else:
    # Si no tiene asignación pero tiene el rol, eliminarlo
    username = data.get('username')
    check_rol_url = f"{SUPABASE_URL}/rest/v1/user_roles?username=eq.{username}&rol=eq.director_grupo"
    check_rol_resp = requests.get(check_rol_url, headers=get_headers())
    
    if check_rol_resp.status_code == 200 and check_rol_resp.json():
        rol_id = check_rol_resp.json()[0]['id']
        requests.delete(
            f"{SUPABASE_URL}/rest/v1/user_roles?id=eq.{rol_id}",
            headers=get_headers()
        )
        st.rerun()
        
    
    # ============================================
    # HORARIO PERSONAL DEL DOCENTE
    # ============================================
    
    st.subheader("📅 Mi Horario Semanal")
    mostrar_horario_docente_tabla(documento_docente, headers)
    
    st.divider()
    st.subheader("📌 Funciones disponibles")
    
    opcion_menu = st.selectbox(
        "Seleccionar una función",
        [
            "📚 Mis Cursos",
            "📝 Ingresar Notas",
            "⚙️ Configurar Notas",
            "📋 Asistencia",
            "📊 Reportes",
            "🤝 Convivencia",
            "✏️ Evaluaciones",
            "💬 Mensajes",
            "📈 Mi Rendimiento"
        ],
        key="menu_docente"
    )
    
    st.divider()
    
    if opcion_menu == "📚 Mis Cursos":
        mostrar_mis_cursos(asignaciones)
        
    elif opcion_menu == "📝 Ingresar Notas":
        mostrar_ingreso_notas(data)
        
    elif opcion_menu == "⚙️ Configurar Notas":
        mostrar_configuracion_notas(data)
        
    elif opcion_menu == "📋 Asistencia":
        mostrar_asistencia_docente(data)
        
    elif opcion_menu == "📊 Reportes":
        mostrar_reportes_docente(data)

    elif opcion_menu == "💬 Mensajes":
        mensajeria.mostrar(data)
        
    else:
        st.info("🚧 Módulo en desarrollo")


def mostrar_mis_cursos(asignaciones):

    st.subheader("📚 Mis Cursos")
    
    materias = [
        a for a in asignaciones
        if a.get('asignatura') != 'Dirección de Curso'
    ]
    
    if not materias:
        st.info("No tienes cursos asignados")
        return
    
    cursos_dict = {}
    
    for m in materias:
        
        curso = m.get('curso')
        asignatura = m.get('asignatura')
        
        if curso not in cursos_dict:
            cursos_dict[curso] = []
            
        cursos_dict[curso].append(asignatura)
    
    for curso, materias_lista in cursos_dict.items():
        
        with st.expander(f"📖 Curso {curso}"):
            
            for materia in materias_lista:
                st.write(f"- {materia}")
