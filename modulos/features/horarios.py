import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from utils import SUPABASE_URL, get_headers

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def parse_hora(hora_str):
    """Convierte string de hora a objeto time"""
    if isinstance(hora_str, time):
        return hora_str
    if isinstance(hora_str, str):
        partes = hora_str.split(':')
        if len(partes) >= 2:
            return time(int(partes[0]), int(partes[1]))
    return time(7, 0)


# ============================================
# ADMIN - CONFIGURACIÓN
# ============================================

def configurar_niveles(headers):
    st.subheader("📚 Niveles Educativos")
    
    response = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    
    if response.status_code == 200:
        niveles = response.json()
        if niveles:
            st.write("**Niveles existentes:**")
            for n in niveles:
                st.write(f"- {n['nombre']}")
    
    with st.expander("➕ Agregar nivel"):
        nuevo_nivel = st.text_input("Nombre del nivel")
        if st.button("Agregar nivel"):
            if nuevo_nivel:
                data = {"nombre": nuevo_nivel, "orden": len(niveles) + 1 if niveles else 1}
                r = requests.post(f"{SUPABASE_URL}/rest/v1/niveles", headers=headers, json=data)
                if r.status_code == 201:
                    st.success(f"✅ Nivel '{nuevo_nivel}' agregado")
                    st.rerun()


def configurar_jornada_nivel(headers):
    st.subheader("⏰ Configurar Jornada por Nivel")
    
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
    
    url_config = f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nivel_id}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200 and response_config.json():
        config = response_config.json()[0]
        dias_laborales_default = config.get('dias_laborales', [1,2,3,4,5])
        horario_rotativo_default = config.get('horario_rotativo', False)
    else:
        dias_laborales_default = [1,2,3,4,5]
        horario_rotativo_default = False
    
    dias_opciones = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    dias_seleccionados = st.multiselect(
        "Días de clase",
        options=list(dias_opciones.keys()),
        format_func=lambda x: dias_opciones[x],
        default=dias_laborales_default
    )
    
    horario_rotativo = st.checkbox("Horario rotativo", value=horario_rotativo_default)
    
    if st.button("💾 Guardar configuración", type="primary"):
        data_config = {
            "nivel_id": nivel_id,
            "dias_laborales": dias_seleccionados,
            "horario_rotativo": horario_rotativo
        }
        
        if response_config.status_code == 200 and response_config.json():
            config_id = response_config.json()[0]['id']
            requests.patch(f"{SUPABASE_URL}/rest/v1/config_horario_nivel?id=eq.{config_id}", 
                          headers=headers, json=data_config)
        else:
            requests.post(f"{SUPABASE_URL}/rest/v1/config_horario_nivel", headers=headers, json=data_config)
        
        st.success("✅ Configuración guardada")
        st.rerun()


def configurar_horario_curso(headers):
    st.subheader("📅 Configurar Horario por Curso")
    
    cursos = ["901", "902", "903", "1001", "1002", "1003", "1101"]
    
    response_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = response_niveles.json() if response_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("No hay niveles configurados")
        return
    
    curso = st.selectbox("Curso", cursos)
    nivel_curso = st.selectbox("Nivel", [n['nombre'] for n in niveles], key="nivel_curso")
    nivel_id = next(n['id'] for n in niveles if n['nombre'] == nivel_curso)
    
    # Obtener días laborales del nivel
    url_config = f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nivel_id}"
    response_config = requests.get(url_config, headers=headers)
    
    if response_config.status_code == 200 and response_config.json():
        config = response_config.json()[0]
        dias_laborales = config.get('dias_laborales', [1,2,3,4,5])
    else:
        st.warning("Primero configura la jornada para este nivel")
        return
    
    # Obtener horario actual
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,hora_inicio.asc"
    response_horario = requests.get(url_horario, headers=headers)
    horarios = response_horario.json() if response_horario.status_code == 200 else []
    
    # Obtener docentes
    response_docentes = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes = response_docentes.json() if response_docentes.status_code == 200 else []
    docentes_dict = {d['documento_docente']: f"{d['nombre_docente']} {d['apellidos_docente']}" for d in docentes}
    
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    # Mostrar horario actual
    if horarios:
        st.write("**Horario actual:**")
        df = pd.DataFrame(horarios)
        df['dia'] = df['dia_semana'].map(dias)
        # Convertir hora a string de forma segura
        df['hora_inicio'] = df['hora_inicio'].apply(lambda x: str(x)[:5] if x else "")
        df['hora_fin'] = df['hora_fin'].apply(lambda x: str(x)[:5] if x else "")
        st.dataframe(df[['dia', 'hora_inicio', 'hora_fin', 'asignatura', 'salon']], use_container_width=True)
    
    st.divider()
    st.write("**Configurar horario (cada clase con su propia hora):**")
    
    # Para cada día
    for dia in dias_laborales:
        with st.expander(f"📅 {dias[dia]}"):
            clases_dia = [h for h in horarios if h['dia_semana'] == dia]
            # Ordenar de forma segura
            try:
                clases_dia.sort(key=lambda x: str(x.get('hora_inicio', '00:00')) if x.get('hora_inicio') else '00:00')
            except:
                clases_dia.sort(key=lambda x: str(x.get('hora_inicio', '00:00')))
            
            # Mostrar clases existentes
            for idx, clase in enumerate(clases_dia):
                # Convertir hora de forma segura
                hora_inicio_val = pd.to_datetime(str(clase['hora_inicio'])).time() if clase.get('hora_inicio') else time(7, 0)
                hora_fin_val = pd.to_datetime(str(clase['hora_fin'])).time() if clase.get('hora_fin') else time(8, 0)
                
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                with col1:
                    nueva_hora_inicio = st.time_input("Hora inicio", value=hora_inicio_val, 
                                                key=f"inicio_{curso}_{dia}_{clase['id']}")
                with col2:
                    nueva_hora_fin = st.time_input("Hora fin", value=hora_fin_val, 
                                            key=f"fin_{curso}_{dia}_{clase['id']}")
                with col3:
                    asignatura = st.text_input("Asignatura", value=clase.get('asignatura', ''),
                                              key=f"asig_{curso}_{dia}_{clase['id']}")
                with col4:
                    docente = st.selectbox("Docente", options=[""] + list(docentes_dict.keys()),
                                          format_func=lambda x: docentes_dict.get(x, "Seleccionar") if x else "Ninguno",
                                          key=f"doc_{curso}_{dia}_{clase['id']}")
                with col5:
                    if st.button("🗑️", key=f"del_{curso}_{dia}_{clase['id']}"):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{clase['id']}", headers=headers)
                        st.rerun()
                
                # Actualizar si hay cambios
                if nueva_hora_inicio and nueva_hora_fin and asignatura:
                    data_update = {
                        "hora_inicio": str(nueva_hora_inicio),
                        "hora_fin": str(nueva_hora_fin),
                        "asignatura": asignatura,
                        "documento_docente": docente if docente else None,
                        "salon": clase.get('salon', '')
                    }
                    requests.patch(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{clase['id']}", 
                                  headers=headers, json=data_update)
                
                st.divider()
            
            # Botón para agregar nueva clase
            with st.container():
                st.write("**➕ Agregar nueva clase**")
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                with col1:
                    nueva_hora_inicio = st.time_input("Hora inicio", key=f"nueva_inicio_{curso}_{dia}", value=None)
                with col2:
                    nueva_hora_fin = st.time_input("Hora fin", key=f"nueva_fin_{curso}_{dia}", value=None)
                with col3:
                    nueva_asignatura = st.text_input("Asignatura", key=f"nueva_asig_{curso}_{dia}")
                with col4:
                    nuevo_docente = st.selectbox("Docente", options=[""] + list(docentes_dict.keys()),
                                                format_func=lambda x: docentes_dict.get(x, "Seleccionar") if x else "Ninguno",
                                                key=f"nueva_doc_{curso}_{dia}")
                
                if st.button("➕ Agregar", key=f"agregar_{curso}_{dia}"):
                    if nueva_hora_inicio and nueva_hora_fin and nueva_asignatura:
                        data_insert = {
                            "curso": curso,
                            "nivel_id": nivel_id,
                            "dia_semana": dia,
                            "hora_inicio": str(nueva_hora_inicio),
                            "hora_fin": str(nueva_hora_fin),
                            "asignatura": nueva_asignatura,
                            "documento_docente": nuevo_docente if nuevo_docente else None,
                            "salon": ""
                        }
                        requests.post(f"{SUPABASE_URL}/rest/v1/horario_base", headers=headers, json=data_insert)
                        st.success("✅ Clase agregada")
                        st.rerun()
    
    if st.button("💾 Guardar todos los cambios", type="primary"):
        st.success("✅ Horario guardado")
        st.rerun()

def gestion_festivos(headers):
    st.subheader("📆 Festivos")
    
    year = st.selectbox("Año", [2024, 2025, 2026])
    
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
                    if st.button("🗑️", key=f"del_{f['id']}"):
                        requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?id=eq.{f['id']}", headers=headers)
                        st.rerun()
    
    with st.expander("➕ Agregar festivo"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha")
        with col2:
            descripcion = st.text_input("Descripción")
        
        if st.button("Agregar"):
            data = {"fecha": str(fecha), "descripcion": descripcion, "year": fecha.year}
            requests.post(f"{SUPABASE_URL}/rest/v1/festivos", headers=headers, json=data)
            st.success("✅ Festivo agregado")
            st.rerun()


def gestion_horarios_admin(data):
    st.title("📅 Configuración de Horarios")
    
    headers = get_headers()
    
    tabs = st.tabs(["📚 Niveles", "⏰ Jornada por Nivel", "📅 Horario por Curso", "📆 Festivos"])
    
    with tabs[0]:
        configurar_niveles(headers)
    with tabs[1]:
        configurar_jornada_nivel(headers)
    with tabs[2]:
        configurar_horario_curso(headers)
    with tabs[3]:
        gestion_festivos(headers)


# ============================================
# VISUALIZACIÓN DE HORARIO - PARA TODOS LOS PERFILES
# ============================================

def mostrar_horario_tabla(curso, headers):
    """Muestra el horario de un curso en formato tabla (con horas variables)"""
    
    # Obtener horario del curso
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=dia_semana.asc,hora_inicio.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code != 200:
        st.info("No hay horario configurado")
        return
    
    horarios = response_horario.json()
    
    if not horarios:
        st.info("No hay horario configurado para este curso")
        return
    
    # Días
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    # Organizar por día
    horario_por_dia = {}
    for dia in dias.values():
        horario_por_dia[dia] = []
    
    for clase in horarios:
        dia = dias.get(clase.get('dia_semana'), "Lunes")
        horario_por_dia[dia].append({
            "hora_inicio": clase.get('hora_inicio', '')[:5] if clase.get('hora_inicio') else '',
            "hora_fin": clase.get('hora_fin', '')[:5] if clase.get('hora_fin') else '',
            "asignatura": clase.get('asignatura', '?'),
            "salon": clase.get('salon', 'N/A')
        })
    
    # Crear tabla
    st.markdown("---")
    
    # Encabezados
    cols = st.columns(len(dias))
    for idx, dia in enumerate(dias.values()):
        with cols[idx]:
            st.markdown(f"**{dia}**")
    
    # Encontrar el número máximo de clases por día
    max_clases = max([len(horario_por_dia[dia]) for dia in dias.values()]) if horarios else 0
    
    # Mostrar filas
    for fila in range(max_clases):
        cols = st.columns(len(dias))
        for idx, dia in enumerate(dias.values()):
            with cols[idx]:
                if fila < len(horario_por_dia[dia]):
                    clase = horario_por_dia[dia][fila]
                    st.write(f"**{clase['hora_inicio']} - {clase['hora_fin']}**")
                    st.write(clase['asignatura'])
                    st.caption(f"📌 {clase['salon']}")
                else:
                    st.write("")
                    st.write("")
                    st.write("")
    
    st.markdown("---")


def mostrar_horario_docente_tabla(documento_docente, headers):
    """Muestra el horario personal del docente en formato tabla"""
    
    # Obtener horario del docente directamente
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?documento_docente=eq.{documento_docente}&order=dia_semana.asc,hora_inicio.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code != 200:
        st.info("No hay horario asignado")
        return
    
    horarios = response_horario.json()
    
    if not horarios:
        st.info("No hay horario asignado para este docente")
        return
    
    # Días
    dias = {1: "Lunes", 2: "Martes", 3: "Miércoles", 4: "Jueves", 5: "Viernes", 6: "Sábado"}
    
    # Organizar por día
    horario_por_dia = {}
    for dia in dias.values():
        horario_por_dia[dia] = []
    
    for clase in horarios:
        dia = dias.get(clase.get('dia_semana'), "Lunes")
        horario_por_dia[dia].append({
            "hora_inicio": clase.get('hora_inicio', '')[:5] if clase.get('hora_inicio') else '',
            "hora_fin": clase.get('hora_fin', '')[:5] if clase.get('hora_fin') else '',
            "asignatura": clase.get('asignatura', '?'),
            "curso": clase.get('curso'),
            "salon": clase.get('salon', 'N/A')
        })
    
    # Crear tabla
    st.markdown("---")
    
    # Encabezados
    cols = st.columns(len(dias))
    for idx, dia in enumerate(dias.values()):
        with cols[idx]:
            st.markdown(f"**{dia}**")
    
    # Encontrar el número máximo de clases por día
    max_clases = max([len(horario_por_dia[dia]) for dia in dias.values()]) if horarios else 0
    
    # Mostrar filas
    for fila in range(max_clases):
        cols = st.columns(len(dias))
        for idx, dia in enumerate(dias.values()):
            with cols[idx]:
                if fila < len(horario_por_dia[dia]):
                    clase = horario_por_dia[dia][fila]
                    st.write(f"**{clase['hora_inicio']} - {clase['hora_fin']}**")
                    st.write(f"{clase['asignatura']} ({clase['curso']})")
                    st.caption(f"📌 {clase['salon']}")
                else:
                    st.write("")
                    st.write("")
                    st.write("")
    
    st.markdown("---")
