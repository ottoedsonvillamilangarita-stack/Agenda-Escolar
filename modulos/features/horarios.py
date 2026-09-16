# ==============================================================================
# modulos/features/horarios.py - GESTIÓN DE HORARIOS & JORNADAS (ZERO-SCROLL)
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
from datetime import time
from utils import SUPABASE_URL

DIAS_SEMANA_MAP = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes"
}
DIAS_INVERSO = {v: k for k, v in DIAS_SEMANA_MAP.items()}

# ==============================================================================
# 1. FRANJAS HORARIAS POR NIVEL
# ==============================================================================
def configurar_horas_nivel(headers):
    st.markdown("### ⏰ Franjas Horarias por Nivel Educativo")
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("⚠️ Primero debes crear los niveles educativos en el menú de Gestión Académica.")
        return

    nombres_niveles = [n['nombre'] for n in niveles]
    dict_niveles = {n['nombre']: n['id'] for n in niveles}

    col_sel, _ = st.columns([1.5, 2.5])
    with col_sel:
        nivel_sel = st.selectbox("Selecciona el nivel a parametrizar:", nombres_niveles, key="sel_franjas_nivel")
    
    nivel_id = dict_niveles[nivel_sel]
    
    # Consultar franjas del nivel
    r_franjas = requests.get(f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&order=numero_hora.asc", headers=headers)
    franjas = r_franjas.json() if r_franjas.status_code == 200 else []

    col_izq, col_der = st.columns([1.3, 1], gap="medium")

    # Columna Izquierda: Grilla actual de horas
    with col_izq:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Franjas Activas: {nivel_sel}</b>
        </div>
        """, unsafe_allow_html=True)

        if franjas:
            data_tabla = []
            for f in franjas:
                es_rec = f.get('tipo', 'Clase') == 'Descanso'
                data_tabla.append({
                    "#": f.get('numero_hora'),
                    "Horario": f"{f.get('hora_inicio', '')[:5]} - {f.get('hora_fin', '')[:5]}",
                    "Tipo de Bloque": "🥪 Descanso" if es_rec else "📖 Clase Pedagógica"
                })
            st.dataframe(pd.DataFrame(data_tabla), use_container_width=True, height=290)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                hora_borrar = st.selectbox("Eliminar bloque:", [f"Hora #{f['numero_hora']}" for f in franjas], label_visibility="collapsed")
            with c_del2:
                if st.button("🗑️ Eliminar", use_container_width=True, key="del_franja_btn"):
                    num_h = int(hora_borrar.replace("Hora #", ""))
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&numero_hora=eq.{num_h}", headers=headers)
                    st.success("Franja eliminada")
                    st.rerun()
        else:
            st.info(f"No hay bloques creados para {nivel_sel}. Puedes agregarlos a la derecha.")

    # Columna Derecha: Formulario manual y generador rápido
    with col_der:
        tab_manual, tab_auto = st.tabs(["➕ Agregar Bloque", "⚡ Cargar Estándar"])

        with tab_manual:
            with st.form("form_nueva_franja", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    num_bloque = st.number_input("Número de bloque:", min_value=1, max_value=12, value=len(franjas) + 1)
                with c2:
                    tipo_bloque = st.selectbox("Tipo:", ["Clase", "Descanso"])
                
                c3, c4 = st.columns(2)
                with c3:
                    h_ini = st.time_input("Hora inicio:", time(7, 0))
                with c4:
                    h_fin = st.time_input("Hora fin:", time(7, 55))

                if st.form_submit_button("💾 Guardar Franja", type="primary", use_container_width=True):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}&numero_hora=eq.{num_bloque}", headers=headers)
                    payload = {
                        "nivel_id": nivel_id,
                        "numero_hora": int(num_bloque),
                        "hora_inicio": str(h_ini),
                        "hora_fin": str(h_fin),
                        "tipo": tipo_bloque
                    }
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/horas_nivel", headers=headers, json=payload)
                    if r.status_code in [200, 201]:
                        st.success(f"Bloque #{num_bloque} guardado")
                        st.rerun()
                    else:
                        st.error(f"Error al guardar: {r.text}")

        with tab_auto:
            st.caption("Aplica una jornada clásica de 6 bloques pedagógicos de 55 min con descanso intermedio:")
            if st.button("🚀 Generar Jornada Estándar (7:00 a 13:00)", type="secondary", use_container_width=True):
                requests.delete(f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id}", headers=headers)
                franjas_def = [
                    {"nivel_id": nivel_id, "numero_hora": 1, "hora_inicio": "07:00:00", "hora_fin": "07:55:00", "tipo": "Clase"},
                    {"nivel_id": nivel_id, "numero_hora": 2, "hora_inicio": "07:55:00", "hora_fin": "08:50:00", "tipo": "Clase"},
                    {"nivel_id": nivel_id, "numero_hora": 3, "hora_inicio": "08:50:00", "hora_fin": "09:20:00", "tipo": "Descanso"},
                    {"nivel_id": nivel_id, "numero_hora": 4, "hora_inicio": "09:20:00", "hora_fin": "10:15:00", "tipo": "Clase"},
                    {"nivel_id": nivel_id, "numero_hora": 5, "hora_inicio": "10:15:00", "hora_fin": "11:10:00", "tipo": "Clase"},
                    {"nivel_id": nivel_id, "numero_hora": 6, "hora_inicio": "11:10:00", "hora_fin": "12:05:00", "tipo": "Clase"},
                    {"nivel_id": nivel_id, "numero_hora": 7, "hora_inicio": "12:05:00", "hora_fin": "13:00:00", "tipo": "Clase"},
                ]
                requests.post(f"{SUPABASE_URL}/rest/v1/horas_nivel", headers=headers, json=franjas_def)
                st.success("Jornada cargada correctamente")
                st.rerun()


# ==============================================================================
# 2. JORNADAS LABORALES
# ==============================================================================
def configurar_jornada_nivel(headers):
    st.markdown("### 🏛️ Jornadas Institucionales por Nivel")
    
    r_niveles = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r_niveles.json() if r_niveles.status_code == 200 else []
    
    if not niveles:
        st.warning("⚠️ No hay niveles configurados en la base de datos.")
        return

    nombres_niveles = [n['nombre'] for n in niveles]
    dict_niveles = {n['nombre']: n['id'] for n in niveles}
    id_a_nivel = {n['id']: n['nombre'] for n in niveles}

    r_jornadas = requests.get(f"{SUPABASE_URL}/rest/v1/jornadas_nivel", headers=headers)
    jornadas = r_jornadas.json() if r_jornadas.status_code == 200 else []
    map_jornadas = {j['nivel_id']: j for j in jornadas if j.get('nivel_id')}

    col_izq, col_der = st.columns([1.3, 1], gap="medium")

    # Columna Izquierda: Panorama general de horarios
    with col_izq:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Horarios de Entrada y Salida por Nivel</b>
        </div>
        """, unsafe_allow_html=True)

        resumen = []
        for n in niveles:
            n_id = n['id']
            j_data = map_jornadas.get(n_id)
            if j_data:
                resumen.append({
                    "Nivel": n['nombre'],
                    "Entrada": j_data.get('hora_entrada', '')[:5],
                    "Salida": j_data.get('hora_salida', '')[:5],
                    "Días Lectivos": j_data.get('dias', 'Lunes a Viernes')
                })
            else:
                resumen.append({
                    "Nivel": n['nombre'],
                    "Entrada": "07:00",
                    "Salida": "13:00",
                    "Días Lectivos": "Lunes a Viernes (Por Defecto)"
                })
        st.dataframe(pd.DataFrame(resumen), use_container_width=True, height=270)

    # Columna Derecha: Configuración del nivel seleccionado
    with col_der:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">✏️ Parametrizar Nivel</b>
        </div>
        """, unsafe_allow_html=True)

        niv_config = st.selectbox("Nivel a modificar:", nombres_niveles, key="jornada_niv_sel")
        n_id_sel = dict_niveles[niv_config]
        actual = map_jornadas.get(n_id_sel, {})

        with st.form(f"form_jornada_{n_id_sel}"):
            c1, c2 = st.columns(2)
            with c1:
                h_ingreso = st.time_input("Hora de Ingreso:", time(7, 0))
            with c2:
                h_salida = st.time_input("Hora de Salida:", time(13, 0))
            
            dias_lect = st.text_input("Días lectivos:", value=actual.get('dias', 'Lunes a Viernes'))

            if st.form_submit_button("💾 Guardar Jornada", type="primary", use_container_width=True):
                requests.delete(f"{SUPABASE_URL}/rest/v1/jornadas_nivel?nivel_id=eq.{n_id_sel}", headers=headers)
                payload = {
                    "nivel_id": n_id_sel,
                    "hora_entrada": str(h_ingreso),
                    "hora_salida": str(h_salida),
                    "dias": dias_lect
                }
                r = requests.post(f"{SUPABASE_URL}/rest/v1/jornadas_nivel", headers=headers, json=payload)
                if r.status_code in [200, 201]:
                    st.success("✅ Jornada actualizada exitosamente")
                    st.rerun()
                else:
                    st.error(f"Error: {r.text}")


# ==============================================================================
# 3. HORARIOS POR CURSO (MALLA SEMANAL ZERO-SCROLL)
# ==============================================================================
def configurar_horario_curso(headers):
    st.markdown("### 📅 Malla Curricular Semanal por Curso")
    
    r_grados = requests.get(f"{SUPABASE_URL}/rest/v1/grados?select=curso,nivel_id&order=curso.asc", headers=headers)
    grados = r_grados.json() if r_grados.status_code == 200 else []
    
    if not grados:
        st.warning("⚠️ Registra los cursos en Gestión Académica para armar sus horarios.")
        return

    cursos_disp = sorted(list(set([g['curso'] for g in grados if g.get('curso')])))
    dict_curso_nivel = {g['curso']: g.get('nivel_id') for g in grados}

    # Barra superior ultra compacta
    col_cur, col_info_top = st.columns([1.5, 2.5])
    with col_cur:
        curso_sel = st.selectbox("Seleccionar Curso:", cursos_disp, key="horario_curso_sel")
    
    nivel_id_curso = dict_curso_nivel.get(curso_sel)

    # 1. Obtener Franjas de este nivel
    r_franjas = requests.get(f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nivel_id_curso}&order=numero_hora.asc", headers=headers) if nivel_id_curso else None
    franjas = r_franjas.json() if r_franjas and r_franjas.status_code == 200 and r_franjas.json() else []

    # Si no tiene franjas configuradas, usar 6 estándar de respaldo
    if not franjas:
        franjas = [
            {"numero_hora": 1, "hora_inicio": "07:00", "hora_fin": "07:55", "tipo": "Clase"},
            {"numero_hora": 2, "hora_inicio": "07:55", "hora_fin": "08:50", "tipo": "Clase"},
            {"numero_hora": 3, "hora_inicio": "08:50", "hora_fin": "09:20", "tipo": "Descanso"},
            {"numero_hora": 4, "hora_inicio": "09:20", "hora_fin": "10:15", "tipo": "Clase"},
            {"numero_hora": 5, "hora_inicio": "10:15", "hora_fin": "11:10", "tipo": "Clase"},
            {"numero_hora": 6, "hora_inicio": "11:10", "hora_fin": "12:05", "tipo": "Clase"},
            {"numero_hora": 7, "hora_inicio": "12:05", "hora_fin": "13:00", "tipo": "Clase"},
        ]

    # 2. Cargar Asignación Académica (Docentes por Materia en este curso)
    r_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}", headers=headers)
    asignaciones = [a for a in r_asig.json() if "DIRECCION" not in str(a.get('asignatura', '')).upper()] if r_asig.status_code == 200 else []
    docente_por_materia = {a['asignatura']: a.get('documento_docente') for a in asignaciones}
    materias_curso = sorted(list(docente_por_materia.keys()))

    # Docentes para resolución de nombres
    r_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    docentes = r_doc.json() if r_doc.status_code == 200 else []
    doc_nombres = {d['documento_docente']: f"{d['nombre_docente'].split()[0]} {d['apellidos_docente'].split()[0]}" for d in docentes}

    # 3. Cargar Horario Registrado en Supabase
    r_horario = requests.get(f"{SUPABASE_URL}/rest/v1/horarios_curso?curso=eq.{curso_sel}", headers=headers)
    horario_items = r_horario.json() if r_horario.status_code == 200 else []

    matriz_horario = {}
    for it in horario_items:
        d = it.get('dia_semana')
        h = it.get('numero_hora')
        asig = it.get('asignatura', '')
        doc_d = it.get('documento_docente')
        prof_nom = doc_nombres.get(doc_d, "")
        matriz_horario[(d, h)] = f"{asig}\n({prof_nom})" if prof_nom else asig

    with col_info_top:
        st.markdown(f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px 12px; margin-top: 18px; font-size: 11.5px; color: #475569;">
            📚 <b>Materias Vinculadas:</b> {len(materias_curso)} | 👨‍🏫 <b>Docentes con Carga:</b> {len(set(docente_por_materia.values()))}
        </div>
        """, unsafe_allow_html=True)

    # LAYOUT 2 COLUMNAS (MALLA SEMANAL 70% | GESTIÓN RÁPIDA 30%)
    col_matriz, col_asignar = st.columns([1.8, 1.1], gap="medium")

    with col_matriz:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13px;">🗓️ Horario Semanal: Grado {curso_sel}</b>
        </div>
        """, unsafe_allow_html=True)

        filas = []
        for f in franjas:
            h_num = f['numero_hora']
            h_label = f"#{h_num} ({f['hora_inicio'][:5]}-{f['hora_fin'][:5]})"
            es_descanso = f.get('tipo') == 'Descanso'

            if es_descanso:
                fila = {
                    "Bloque": h_label,
                    "Lunes": "🥪 RECESO",
                    "Martes": "🥪 RECESO",
                    "Miércoles": "🥪 RECESO",
                    "Jueves": "🥪 RECESO",
                    "Viernes": "🥪 RECESO"
                }
            else:
                fila = {
                    "Bloque": h_label,
                    "Lunes": matriz_horario.get((1, h_num), "—"),
                    "Martes": matriz_horario.get((2, h_num), "—"),
                    "Miércoles": matriz_horario.get((3, h_num), "—"),
                    "Jueves": matriz_horario.get((4, h_num), "—"),
                    "Viernes": matriz_horario.get((5, h_num), "—")
                }
            filas.append(fila)

        st.dataframe(pd.DataFrame(filas).set_index("Bloque"), use_container_width=True, height=330)

    # Panel lateral derecho para asignar materia a la casilla
    with col_asignar:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13px;">✏️ Asignar Asignatura a Casilla</b>
        </div>
        """, unsafe_allow_html=True)

        bloques_clase = [f['numero_hora'] for f in franjas if f.get('tipo') != 'Descanso']

        with st.form("form_asignar_bloque"):
            c_d, c_h = st.columns(2)
            with c_d:
                dia_nom = st.selectbox("Día de la semana:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])
            with c_h:
                bloque_sel = st.selectbox("Franja / Hora:", bloques_clase, format_func=lambda x: f"Hora #{x}")

            dia_cod = DIAS_INVERSO[dia_nom]

            if materias_curso:
                asig_sel = st.selectbox("Asignatura:", materias_curso)
                doc_doc_auto = docente_por_materia.get(asig_sel)
                prof_asoc = doc_nombres.get(doc_doc_auto, "Sin docente asignado")
                st.caption(f"👨‍🏫 Imparte: **{prof_asoc}**")
            else:
                st.warning("No hay asignaturas vinculadas a este curso. Agrégalas en Gestión Académica.")
                asig_sel = None
                doc_doc_auto = None

            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                guardar_slot = st.form_submit_button("💾 Guardar Casilla", type="primary", use_container_width=True)
            with c_btn2:
                borrar_slot = st.form_submit_button("🗑️ Vaciar Casilla", use_container_width=True)

            if guardar_slot:
                if asig_sel:
                    # Eliminar ocupación previa de esa casilla en el curso
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horarios_curso?curso=eq.{curso_sel}&dia_semana=eq.{dia_cod}&numero_hora=eq.{bloque_sel}", headers=headers)
                    
                    payload = {
                        "curso": curso_sel,
                        "dia_semana": dia_cod,
                        "numero_hora": bloque_sel,
                        "asignatura": asig_sel,
                        "documento_docente": doc_doc_auto
                    }
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/horarios_curso", headers=headers, json=payload)
                    if r.status_code in [200, 201]:
                        st.success(f"{asig_sel} asignada al {dia_nom}")
                        st.rerun()
                    else:
                        st.error(f"Error: {r.text}")

            if borrar_slot:
                requests.delete(f"{SUPABASE_URL}/rest/v1/horarios_curso?curso=eq.{curso_sel}&dia_semana=eq.{dia_cod}&numero_hora=eq.{bloque_sel}", headers=headers)
                st.info(f"Casilla de {dia_nom} vaciada")
                st.rerun()


# ==============================================================================
# 4. GESTIÓN DE FESTIVOS & CALENDARIO
# ==============================================================================
def gestion_festivos(headers):
    st.markdown("### 🏖️ Calendario Escolar y Días No Lectivos")
    
    r_festivos = requests.get(f"{SUPABASE_URL}/rest/v1/festivos?order=fecha.asc", headers=headers)
    festivos = r_festivos.json() if r_festivos.status_code == 200 else []

    col_izq, col_der = st.columns([1.3, 1], gap="medium")

    with col_izq:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">📋 Días Festivos y Recesos Registrados</b>
        </div>
        """, unsafe_allow_html=True)

        if festivos:
            df_f = pd.DataFrame(festivos)[['fecha', 'descripcion']].rename(columns={'fecha': 'Fecha', 'descripcion': 'Motivo / Festividad'})
            st.dataframe(df_f, use_container_width=True, height=270)

            c_del1, c_del2 = st.columns([2, 1])
            with c_del1:
                f_del = st.selectbox("Eliminar festivo:", [f['fecha'] for f in festivos], label_visibility="collapsed")
            with c_del2:
                if st.button("🗑️ Quitar", use_container_width=True):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?fecha=eq.{f_del}", headers=headers)
                    st.success("Día festivo eliminado")
                    st.rerun()
        else:
            st.info("No hay días festivos registrados en la vigencia.")

    with col_der:
        st.markdown("""
        <div style="background: white; border: 1px solid #E2E8F0; border-radius: 8px; padding: 9px 12px; margin-bottom: 8px;">
            <b style="color: #0F172A; font-size: 13.5px;">➕ Registrar Día No Lectivo</b>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_nuevo_festivo", clear_on_submit=True):
            fecha_fest = st.date_input("Fecha del festivo / receso:")
            desc_fest = st.text_input("Motivo (Ej: Día Cívico, Semana Santa, Feriado Nacional):")

            if st.form_submit_button("💾 Guardar Día Festivo", type="primary", use_container_width=True):
                if desc_fest:
                    requests.delete(f"{SUPABASE_URL}/rest/v1/festivos?fecha=eq.{str(fecha_fest)}", headers=headers)
                    payload = {"fecha": str(fecha_fest), "descripcion": desc_fest.strip()}
                    r = requests.post(f"{SUPABASE_URL}/rest/v1/festivos", headers=headers, json=payload)
                    if r.status_code in [200, 201]:
                        st.success(f"✅ Festivo del {fecha_fest} registrado")
                        st.rerun()
                    else:
                        st.error(f"Error: {r.text}")
