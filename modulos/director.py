    # 2. MOSTRAR HORARIO DEL CURSO
    st.subheader(f"📅 Horario de {curso_dirige}")
    
    url_horario = f"{SUPABASE_URL}/rest/v1/horario_base?curso=eq.{curso_dirige}&order=dia_semana.asc,orden_clase.asc"
    response_horario = requests.get(url_horario, headers=headers)
    
    if response_horario.status_code == 200:
        horarios = response_horario.json()
        if horarios:
            # Mostrar horario con tipo "estudiante" (muestra asignatura + docente)
            mostrar_horario_unificado(horarios, f"📅 Horario de {curso_dirige}", "estudiante")
        else:
            st.info(f"⚠️ No hay horario configurado para {curso_dirige}")
    else:
        st.info(f"⚠️ No se pudo cargar el horario de {curso_dirige}")
