import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers

def mostrar(data):
    st.title("👨‍👩‍👧 Panel del Acudiente")
    
    # data contiene: username, password_hash, rol, documento
    documento_acudiente = data.get('documento')
    
    st.write(f"Bienvenido, Acudiente")
    st.write(f"Documento: {documento_acudiente}")
    
    headers = get_headers()
    
    # Buscar los hijos de este acudiente en la tabla estudiantes
    url = f"{SUPABASE_URL}/rest/v1/estudiantes?documento_acudiente=eq.{documento_acudiente}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        datos = response.json()
        if datos:
            st.success(f"✅ Acudiente encontrado con {len(datos)} hijo(s)")
            
            for hijo in datos:
                with st.expander(f"📘 {hijo.get('nombre_estudiante', 'N/A')}"):
                    st.write(f"**Nombre:** {hijo.get('nombre_estudiante', 'N/A')}")
                    st.write(f"**Apellidos:** {hijo.get('apellidos_estudiante', 'N/A')}")
                    st.write(f"**Curso:** {hijo.get('curso', 'N/A')}")
                    st.write(f"**Parentesco:** {hijo.get('parentesco', 'N/A')}")
                    st.write(f"**Teléfono:** {hijo.get('telefono_acudiente', 'N/A')}")
        else:
            st.warning("No se encontraron hijos asociados a este acudiente")
    else:
        st.error(f"Error {response.status_code}: {response.text}")
    
    st.subheader("📊 Seguimiento Académico")
    st.write("Próximamente: Notas, asistencia y comunicados de tus hijos")
