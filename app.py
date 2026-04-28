import streamlit as st
# --- TUS CÓDIGOS DE META ---
ID_PIXEL = "885240155980714"
TOKEN_META = "EAAOhBgcrIZCABRTjghUKzQeYiDdzL1MoU3nrpPZCqSRUpPAkYlUiOOZBYaLtC0rIn35T25ZAyHmn47Q9dGx8oA0kFTDYy0QjtQzZACO2HVltVMa6wfmw9ZBRD5pZB418RBDwihmTZBOAbTtTZB8QZAIO5b48vSqVJikgHH4bbzr95XcIvcZBh3a2FiRQgMj2cGbqXyzaQZDZD"
import pandas as pd
import urllib.parse

# --- CONFIGURACIÓN PRO ---
st.set_page_config(page_title="Sistema Pro - Limpieza & Fumigación", layout="wide")

st.title("🚀 Panel de Control de Ventas & Optimización")

# --- LÓGICA DE FILTRO (Para Jessica) ---
with st.sidebar:
    st.header("🎯 Filtro de Calidad")
    zona = st.selectbox("Zona del Cliente", ["Panamá Centro", "San Miguelito", "Panamá Oeste", "Otros"])
    presupuesto_estimado = st.number_input("Presupuesto del cliente ($)", min_value=0)
    
    if st.button("Calificar Prospecto"):
        if zona == "Otros" or presupuesto_estimado < 35:
            st.error("⚠️ Prospecto de BAJA CALIDAD (No enviar a WhatsApp)")
        else:
            st.success("✅ Prospecto CALIFICADO (Proceder)")

# --- GENERADOR DE COTIZACIÓN PROFESIONAL ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Datos del Servicio")
    cliente = st.text_input("Nombre del Cliente")
    tel = st.text_input("WhatsApp (ej: 66778899)")
    servicio = st.selectbox("Servicio", ["Fumigación 24/7", "Limpieza Industrial", "Lavado de Sofás"])
    monto = st.number_input("Precio Final ($)", min_value=0.0)

with col2:
    st.subheader("📊 Optimización de Meta (IA)")
    enviar_a_meta = st.checkbox("Enviar conversión a Meta Ads", value=True)
    st.info("Al marcar esto, el algoritmo de Facebook aprenderá que este cliente SÍ compró y buscará gente igual.")

# --- BOTÓN DE CIERRE ---
if st.button("FINALIZAR Y ENVIAR"):
    # Lógica de WhatsApp
    mensaje = f"Hola {cliente}, adjunto cotización por {servicio} de su empresa de confianza. Total: ${monto}"
    link_wa = f"https://wa.me/507{tel}?text={urllib.parse.quote(mensaje)}"
    
    st.markdown(f'[📲 CLIC AQUÍ PARA ENVIAR WHATSAPP]({link_wa})', unsafe_allow_html=True)
    
    if enviar_a_meta:
        # Aquí se activa la señal secreta para Meta
        st.write("📡 Enviando señal de éxito a Meta Ads...")
        # (Aquí conectamos tu Token de Meta en el siguiente paso)
