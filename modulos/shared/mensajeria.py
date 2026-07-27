import streamlit as st
import requests
from utils import SUPABASE_URL, get_headers


def mostrar(usuario_actual):

    st.title("📨 Mensajería")

    st.subheader("Redactar mensaje")

    destinatario = st.text_input("Destinatario (documento)")
    asunto = st.text_input("Asunto")
    mensaje = st.text_area("Mensaje")

    if st.button("Enviar mensaje"):

        datos = {
            "remitente_documento": usuario_actual.get("documento"),
            "remitente_nombre": usuario_actual.get("nombre"),
            "remitente_rol": usuario_actual.get("rol"),

            "destinatario_documento": destinatario,

            "asunto": asunto,
            "mensaje": mensaje
        }

        url = f"{SUPABASE_URL}/rest/v1/mensajes"

        headers = get_headers()

        response = requests.post(
            url,
            json=datos,
            headers=headers
        )

        if response.status_code == 201:
            st.success("✅ Mensaje enviado correctamente")
        else:
            st.error(f"❌ Error al enviar: {response.text}")
