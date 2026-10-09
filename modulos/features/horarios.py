# ==============================================================================
# modulos/features/horarios.py - GESTION Y VISTAS DE HORARIOS
# ==============================================================================

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, time
from utils import SUPABASE_URL, get_headers

DIAS_SEMANA_MAP = {
    1: "Lunes",
    2: "Martes",
    3: "Miercoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sabado"
}
DIAS_INVERSO = {v: k for k, v in DIAS_SEMANA_MAP.items()}

def parse_hora(hora_str):
    if isinstance(hora_str, time):
        return hora_str
    if isinstance(hora_str, str):
        partes = hora_str.split(':')
        if len(partes) >= 2:
            return time(int(partes[0]), int(partes[1]))
    return time(7, 0)

def formatear_nombre_corto(nombre_completo):
    if not nombre_completo:
        return ""
    partes = str(nombre_completo).strip().split()
    if len(partes) >= 2:
        return f"{partes[0].capitalize()} {partes[1].capitalize()}"
    return partes[0].capitalize() if partes else ""

# 1. NIVELES EDUCATIVOS
def configurar_niveles(headers=None):
    if headers is None:
        headers = get_headers()
    st.subheader("Niveles Educativos")
    r = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r.json() if r.status_code == 200 else []
    c1, c2 = st.columns([1.3, 1])
    with c1:
        if niveles:
            st.dataframe(pd.DataFrame(niveles)[['orden', 'nombre']].rename(columns={'orden': 'Orden', 'nombre': 'Nivel'}), use_container_width=True)
        else:
            st.info("Sin niveles registrados.")
    with c2:
        with st.form("form_nuevo_nivel", clear_on_submit=True):
            nom = st.text_input("Nuevo nivel:")
            if st.form_submit_button("Guardar", type="primary"):
                if nom:
                    requests.post(f"{SUPABASE_URL}/rest/v1/niveles", headers=headers, json={"nombre": nom.strip(), "orden": len(niveles) + 1})
                    st.success("Nivel agregado")
                    st.rerun()

# 2. FRANJAS HORARIAS
def configurar_horas_nivel(headers=None):
    if headers is None:
        headers = get_headers()
    st.subheader("Franjas Horarias")
    r = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r.json() if r.status_code == 200 else []
    if not niveles:
        st.warning("Registra los niveles primero.")
        return
    nombres = [n['nombre'] for n in niveles]
    dict_n = {n['nombre']: n['id'] for n in niveles}
    sel = st.selectbox("Nivel:", nombres, key="hn_sel")
    nid = dict_n[sel]
    r_h = requests.get(f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nid}&order=orden.asc", headers=headers)
    horas = r_h.json() if r_h.status_code == 200 else []
    c1, c2 = st.columns([1.3, 1])
    with c1:
        if horas:
            st.dataframe(pd.DataFrame(horas)[['orden', 'hora_inicio', 'hora_fin', 'descripcion']], use_container_width=True)
        else:
            st.info("Sin franjas.")
    with c2:
        with st.form("form_add_h", clear_on_submit=True):
            orden = st.number_input("Orden:", min_value=1, value=len(horas)+1)
            h_ini = st.time_input("Inicio:", value=time(7, 0))
            h_fin = st.time_input("Fin:", value=time(7, 50))
            desc = st.text_input("Descripcion:", value=f"Hora #{orden}")
            if st.form_submit_button("Guardar Franja", type="primary"):
                requests.post(f"{SUPABASE_URL}/rest/v1/horas_nivel", headers=headers, json={"nivel_id": nid, "orden": int(orden), "hora_inicio": str(h_ini), "hora_fin": str(h_fin), "descripcion": desc})
                st.success("Guardado")
                st.rerun()

# 3. DIAS LABORALES
def configurar_jornada_nivel(headers=None):
    if headers is None:
        headers = get_headers()
    st.subheader("Dias Laborales")
    r = requests.get(f"{SUPABASE_URL}/rest/v1/niveles?order=orden.asc", headers=headers)
    niveles = r.json() if r_niveles.status_code == 200 else []
    if not niveles:
        return
    nombres = [n['nombre'] for n in niveles]
    dict_n = {n['nombre']: n['id'] for n in niveles}
    sel = st.selectbox("Nivel:", nombres, key="jn_sel")
    nid = dict_n[sel]
    r_c = requests.get(f"{SUPABASE_URL}/rest/v1/config_horario_nivel?nivel_id=eq.{nid}", headers=headers)
    conf = r_c.json()[0] if r_c.status_code == 200 and r_c.json() else {}
    with st.form("form_jn"):
        dias = st.multiselect("Dias activos:", list(DIAS_SEMANA_MAP.keys()), default=conf.get('dias_laborales', [1,2,3,4,5]), format_func=lambda x: DIAS_SEMANA_MAP[x])
        rot = st.checkbox("Rotativo", value=conf.get('horario_rotativo', False))
        if st.form_submit_button("Guardar Jornada", type="primary"):
            payload = {"nivel_id": nid, "dias_laborales": dias, "horario_rotativo": rot}
            if conf.get('id'):
                requests.patch(f"{SUPABASE_URL}/rest/v1/config_horario_nivel?id=eq.{conf['id']}", headers=headers, json=payload)
            else:
                requests.post(f"{SUPABASE_URL}/rest/v1/config_horario_nivel", headers=headers, json=payload)
            st.success("Guardado")
            st.rerun()

# 4. HORARIO POR CURSO
def configurar_horario_curso(headers=None):
    if headers is None:
        headers = get_headers()
    st.subheader("Malla Curricular por Curso")
    r_g = requests.get(f"{SUPABASE_URL}/rest/v1/grados?order=curso.asc", headers=headers)
    grados = r_g.json() if r_g.status_code == 200 else []
    cursos = [g['curso'] for g in grados if g.get('curso')] if grados else ["901", "902", "903"]
    map_n = {g['curso']: g.get('nivel_id') for g in grados}
    c_sel, c_sync = st.columns([1.5, 1.5])
    with c_sel:
        curso_sel = st.selectbox("Curso:", cursos, key="cur_h_sel")
    nid = map_n.get(curso_sel, 1)

    r_asig = requests.get(f"{SUPABASE_URL}/rest/v1/asignacion_academica?curso=eq.{curso_sel}", headers=headers)
    asigs = r_asig.json() if r_asig.status_code == 200 else []
    mapa_doc = {}
    mats = []
    for a in asigs:
        m = str(a.get('asignatura', '')).strip().upper()
        if m and "DIRECCION" not in m:
            mapa_doc[m] = str(a.get('documento_docente') or '')
            if m not in mats:
                mats.append(m)
    mats.sort()

    with c_sync:
        st.write("")
        if st.button("Sincronizar Carga Academica", use_container_width=True):
            r_cl = requests.get(f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso_sel}", headers=headers)
            clases = r_cl.json() if r_cl.status_code == 200 else []
            upd = 0
            for cl in clases:
                asig_m = str(cl.get('asignatura', '')).strip().upper()
                doc_m = mapa_doc.get(asig_m)
                if doc_m and str(cl.get('documento_docente')) != doc_m:
                    requests.patch(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{cl['id']}", headers=headers, json={"documento_docente": doc_m})
                    upd += 1
            st.success(f"{upd} clases sincronizadas")
            st.rerun()

    r_h = requests.get(f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso_sel}&order=orden_clase.asc,dia_semana.asc", headers=headers)
    horarios_curso = r_h.json() if r_h.status_code == 200 else []

    r_horas = requests.get(f"{SUPABASE_URL}/rest/v1/horas_nivel?nivel_id=eq.{nid}&order=orden.asc", headers=headers)
    horas_db = r_horas.json() if r_horas.status_code == 200 else []
    horas_map = {int(h['orden']): {"orden": int(h['orden']), "inicio": str(h.get('hora_inicio','07:00'))[:5], "fin": str(h.get('hora_fin','07:50'))[:5]} for h in horas_db}
    for item in horarios_curso:
        o = item.get('orden_clase')
        if o is not None and int(o) not in horas_map:
            horas_map[int(o)] = {"orden": int(o), "inicio": str(item.get('hora_inicio','07:00'))[:5], "fin": str(item.get('hora_fin','07:50'))[:5]}
    if not horas_map:
        for idx in range(1, 7):
            horas_map[idx] = {"orden": idx, "inicio": f"{6+idx:02d}:00", "fin": f"{6+idx:02d}:50"}
    lista_horas = [horas_map[k] for k in sorted(horas_map.keys())]

    r_doc = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    doc_dict = {str(d['documento_docente']): f"{d.get('nombre_docente','')} {d.get('apellidos_docente','')}".strip() for d in (r_doc.json() if r_doc.status_code == 200 else [])}

    matriz = {}
    for cl in horarios_curso:
        try:
            matriz[(int(cl.get('dia_semana')), int(cl.get('orden_clase')))] = cl
        except Exception:
            pass

    col_malla, col_edit = st.columns([1.8, 1.1])
    with col_malla:
        st.write(f"**Horario Semanal: Grado {curso_sel}** ({len(horarios_curso)} clases)")
        dias_cols = [1, 2, 3, 4, 5]
        if any(int(h.get('dia_semana', 0)) == 6 for h in horarios_curso):
            dias_cols.append(6)
        
        c_hdr = st.columns(len(dias_cols) + 1)
        c_hdr[0].write("**Hora**")
        for i_d, d_num in enumerate(dias_cols):
            c_hdr[i_d + 1].write(f"**{DIAS_SEMANA_MAP[d_num][:3]}**")

        for h_info in lista_horas:
            o_num = h_info['orden']
            c_row = st.columns(len(dias_cols) + 1)
            c_row[0].write(f"#{o_num} ({h_info['inicio']}-{h_info['fin']})")
            for i_d, d_num in enumerate(dias_cols):
                cl = matriz.get((d_num, o_num))
                if cl:
                    nom_d = formatear_nombre_corto(doc_dict.get(str(cl.get('documento_docente') or ''), ''))
                    sal = f"[{cl.get('salon')}]" if cl.get('salon') else ""
                    txt_asig = cl.get('asignatura', '')
                    c_row[i_d + 1].info(f"{txt_asig}\n{nom_d} {sal}")
                else:
                    c_row[i_d + 1].write("—")

    with col_edit:
        st.write("**Asignar o Editar Casilla**")
        c_d, c_h = st.columns(2)
        with c_d:
            dia_sel_nom = st.selectbox("Dia:", ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"], key="d_slot")
        with c_h:
            hora_sel = st.selectbox("Hora:", [h['orden'] for h in lista_horas], format_func=lambda x: f"Hora #{x}", key="h_slot")
        
        d_num = DIAS_INVERSO[dia_sel_nom]
        h_obj = next((h for h in lista_horas if h['orden'] == hora_sel), lista_horas[0])
        exist = matriz.get((d_num, hora_sel))

        asig_val = exist.get('asignatura', '') if exist else ''
        if mats:
            opcs = [""] + mats + ["OTRA..."]
            idx_m = opcs.index(asig_val) if asig_val in opcs else 0
            sel_m = st.selectbox("Asignatura *:", opcs, index=idx_m, key="asig_sel_c")
            asig_final = st.text_input("Nombre materia:", value=asig_val).strip().upper() if sel_m == "OTRA..." else sel_m
        else:
            asig_final = st.text_input("Asignatura *:", value=asig_val).strip().upper()

        doc_sug = mapa_doc.get(asig_final, '')
        doc_act = str(exist.get('documento_docente') or '') if exist else doc_sug
        docs_opts = [""] + list(doc_dict.keys())
        idx_doc = docs_opts.index(doc_act) if doc_act in docs_opts else 0
        doc_final = st.selectbox("Docente:", docs_opts, index=idx_doc, format_func=lambda x: doc_dict.get(x, "Sin docente") if x else "Ninguno", key="doc_sel_c")
        salon_in = st.text_input("Salon:", value=exist.get('salon', '') if exist else "")

        b1, b2 = st.columns(2)
        with b1:
            if st.button("Guardar Casilla", type="primary", use_container_width=True):
                if not asig_final:
                    st.error("Ingresa la asignatura")
                else:
                    payload = {"curso": curso_sel, "nivel_id": nid, "dia_semana": d_num, "orden_clase": hora_sel, "hora_inicio": f"{h_obj['inicio']}:00", "hora_fin": f"{h_obj['fin']}:00", "asignatura": asig_final, "documento_docente": doc_final if doc_final else None, "salon": salon_in.strip().upper()}
                    if exist and exist.get('id'):
                        requests.patch(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{exist['id']}", headers=headers, json=payload)
                    else:
                        requests.post(f"{SUPABASE_URL}/rest/v1/horario_base", headers=headers, json=payload)
                    st.success("Guardado")
                    st.rerun()
        with b2:
            if st.button("Vaciar Casilla", use_container_width=True):
                if exist and exist.get('id'):
                    requests.delete(f"{SUPABASE_URL}/rest/v1/horario_base?id=eq.{exist['id']}", headers=headers)
                    st.info("Vaciada")
                    st.rerun()

# 5. GESTION DE FESTIVOS
def gestion_festivos(headers=None):
    if headers is None:
        headers = get_headers()
    st.subheader("Festivos")
    year = st.selectbox("Ano:", [2025, 2026, 2027], index=1)
    r = requests.get(f"{SUPABASE_URL}/rest/v1/festivos?year=eq.{year}&order=fecha.asc", headers=headers)
    fests = r.json() if r.status_code == 200 else []
    c1, c2 = st.columns([1.3, 1])
    with c1:
        if fests:
            st.dataframe(pd.DataFrame(fests)[['fecha', 'descripcion']], use_container_width=True)
        else:
            st.info("Sin festivos.")
    with c2:
        with st.form("form_fest", clear_on_submit=True):
            f_date = st.date_input("Fecha:")
            f_desc = st.text_input("Motivo:")
            if st.form_submit_button("Guardar Festivo", type="primary"):
                if f_desc.strip():
                    requests.post(f"{SUPABASE_URL}/rest/v1/festivos", headers=headers, json={"fecha": str(f_date), "descripcion": f_desc.strip(), "year": f_date.year})
                    st.success("Guardado")
                    st.rerun()

# 6. MENU COMPLETO ADMIN
def gestion_horarios_admin(data):
    st.title("Configuracion de Horarios")
    headers = get_headers()
    tabs = st.tabs(["Niveles", "Horas por Nivel", "Dias Laborales", "Asignar Materias", "Festivos"])
    with tabs[0]:
        configurar_niveles(headers)
    with tabs[1]:
        configurar_horas_nivel(headers)
    with tabs[2]:
        configurar_jornada_nivel(headers)
    with tabs[3]:
        configurar_horario_curso(headers)
    with tabs[4]:
        gestion_festivos(headers)

# 7. VISUALIZACION UNIFICADA (DOCENTE / ESTUDIANTE / ACUDIENTE)
def mostrar_horario_unificado(horarios, titulo="Mi Horario Semanal", tipo_vista="estudiante"):
    if not horarios:
        st.info("No hay horario disponible")
        return
    headers = get_headers()
    r_docs = requests.get(f"{SUPABASE_URL}/rest/v1/docentes", headers=headers)
    map_doc = {str(d['documento_docente']): f"{d.get('nombre_docente','')} {d.get('apellidos_docente','')}".strip() for d in (r_docs.json() if r_docs.status_code == 200 else [])}

    h_dict = {}
    h_labels = {}
    for cl in horarios:
        o = cl.get('orden_clase') or 1
        ini = str(cl.get('hora_inicio',''))[:5]
        fin = str(cl.get('hora_fin',''))[:5]
        h_labels[o] = f"#{o} ({ini}-{fin})" if (ini and fin) else f"#{o}"
        if o not in h_dict:
            h_dict[o] = {d: None for d in DIAS_SEMANA_MAP.values()}
        d_num = int(cl.get('dia_semana', 1))
        d_nom = DIAS_SEMANA_MAP.get(d_num, "Lunes")
        doc_nom = formatear_nombre_corto(map_doc.get(str(cl.get('documento_docente') or ''), ''))
        h_dict[o][d_nom] = {"asig": str(cl.get('asignatura','?')).upper(), "curso": str(cl.get('curso','')), "salon": str(cl.get('salon','')).strip(), "doc": doc_nom}

    st.subheader(titulo)
    dias_activos = [1, 2, 3, 4, 5]
    if any(cl.get('dia_semana') == 6 for cl in horarios):
        dias_activos.append(6)

    cols = st.columns(len(dias_activos) + 1)
    cols[0].write("**Hora**")
    for idx, d_num in enumerate(dias_activos):
        cols[idx + 1].write(f"**{DIAS_SEMANA_MAP[d_num][:3]}**")

    for o_num in sorted(h_dict.keys()):
        cols = st.columns(len(dias_activos) + 1)
        cols[0].write(h_labels[o_num])
        for idx, d_num in enumerate(dias_activos):
            dia_nom = DIAS_SEMANA_MAP[d_num]
            c = h_dict[o_num].get(dia_nom)
            if c:
                sal = f"[{c['salon']}]" if c['salon'] else ""
                if tipo_vista == "docente":
                    asig_txt = c['asig']
                    cur_txt = c['curso']
                    cols[idx + 1].info(f"{asig_txt}\nGrado {cur_txt} {sal}")
                else:
                    doc_txt = c['doc'] if c['doc'] else "Sin docente"
                    asig_txt = c['asig']
                    cols[idx + 1].info(f"{asig_txt}\n{doc_txt} {sal}")
            else:
                cols[idx + 1].write("—")

def mostrar_horario_docente_tabla(documento_docente, headers=None):
    if headers is None:
        headers = get_headers()
    r = requests.get(f"{SUPABASE_URL}/rest/v1/horario_base?documento_docente=eq.{documento_docente}&order=orden_clase.asc,dia_semana.asc", headers=headers)
    if r.status_code != 200 or not r.json():
        st.info("No tienes clases asignadas.")
        return
    mostrar_horario_unificado(r.json(), "Mi Horario Semanal", "docente")

def mostrar_horario_estudiante_tabla(curso, headers=None):
    if headers is None:
        headers = get_headers()
    r = requests.get(f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso}&order=orden_clase.asc,dia_semana.asc", headers=headers)
    if r.status_code != 200 or not r.json():
        st.info(f"No hay clases registradas para el grado {curso}.")
        return
    mostrar_horario_unificado(r.json(), f"Horario Semanal - Grado {curso}", "estudiante")
