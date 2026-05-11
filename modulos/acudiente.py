import streamlit as st
import pandas as pd
import plotly.express as px

def mostrar(data):
    st.title(f"👨‍👩‍👧 Panel del Acudiente")
    st.write(f"Bienvenido, {data['nombre']}")
    
    # Selector de hijo (simulado)
    hijo = st.selectbox(
        "Seleccionar hijo",
        ["Laura Méndez (11°A)", "Andrés Méndez (10°A)"]
    )
    
    # Datos de ejemplo según el hijo seleccionado
    if "Laura" in hijo:
        notas_ejemplo = [
            {"materia": "Matemáticas", "nota": 4.5, "periodo": 1},
            {"materia": "Ciencias", "nota": 3.8, "periodo": 1},
            {"materia": "Español", "nota": 4.2, "periodo": 1},
        ]
        grado = "11°A"
    else:
        notas_ejemplo = [
            {"materia": "Matemáticas", "nota": 3.5, "periodo": 1},
            {"materia": "Ciencias", "nota": 4.0, "periodo": 1},
            {"materia": "Español", "nota": 3.8, "periodo": 1},
        ]
        grado = "10°A"
    
    st.subheader(f"📖 Notas de {hijo}")
    st.caption(f"Grado: {grado}")
    
    # Crear DataFrame
    df_notas = pd.DataFrame(notas_ejemplo)
    
    # Calcular promedio general
    promedio_general = df_notas["nota"].mean()
    
    # Mostrar notas
    for _, row in df_notas.iterrows():
        st.write(f"**{row['materia']}:** {row['nota']}")
    
    st.divider()
    st.write(f"**📊 Promedio General:** {promedio_general:.1f}")
    
    # Gráfico
    fig = px.bar(
        df_notas,
        x="materia",
        y="nota",
        title=f"Calificaciones de {hijo}",
        color="nota",
        color_continuous_scale=["red", "yellow", "green"],
        range_color=[0, 5],
        text="nota"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Agendar reunión (opcional)
    st.subheader("📅 Acciones")
    if st.button("📞 Solicitar reunión con docente"):
        st.info("Próximamente: Sistema de agendamiento de reuniones")
