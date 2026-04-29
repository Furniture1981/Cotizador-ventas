mport streamlit as st
import pandas as pd

st.set_page_config(page_title="Furniture Cleans - Cotizador", page_icon="🧼")

st.title("🚀 Panel de Control de Ventas")

# Lista detallada de servicios basada en tus fotos
servicios_dict = {
    "--- Limpieza de Colchones ---": 0,
    "Colchón Twin (1 plaza) - $25": 25,
    "Colchón Full (2 plazas) - $35": 35,
    "Colchón Queen - $45": 45,
    "Colchón King - $55": 55,
    "--- Limpieza de Sofás ---": 0,
    "Sofá 1 Puesto - $15": 15,
    "Sofá 2 Puestos - $30": 30,
    "Sofá 3 Puestos - $45": 45,
    "Sofá en L (Pequeño) - $60": 60,
    "--- Sillas y Comedor ---": 0,
    "Silla de Comedor (C/U) - $5": 5,
    "Silla de Oficina - $10": 10,
    "Poltrona - $20": 20,
    "--- Alfombras ---": 0,
    "Alfombra Pequeña - $20": 20,
    "Alfombra Mediana - $40": 40,
    "Alfombra Grande - $60": 60,
    "--- Autos ---": 0,
    "Sedán (Solo Asientos) - $40": 40,
    "SUV (Solo Asientos) - $50": 50,
    "Interior Completo - $80": 80,
    "--- Otros Servicios ---": 0,
    "Pulimiento de Pisos (Cotizar)": 0,
    "Fumigación Básica - $35": 35,
    "Fumigación Reforzada - $50": 50
}

with st.sidebar:
    st.header("Datos del Servicio")
    nombre = st.text_input("Nombre del Cliente")
    whatsapp = st.text_input("WhatsApp (ej: 66778899)")
    
    opcion = st.selectbox("Seleccione el Servicio", list(servicios_dict.keys()))
    precio_sugerido = servicios_dict[opcion]
    
    precio_final = st.number_input("Precio Final ($)", value=float(precio_sugerido))

if st.button("FINALIZAR Y ENVIAR"):
    if nombre and whatsapp:
        link_wa = f"https://wa.me/507{whatsapp}?text=Hola%20{nombre},%20confirmamos%20tu%20servicio%20de%20{opcion}%20por%20${precio_final}"
        st.markdown(f'[📲 CLIC AQUÍ PARA ENVIAR WHATSAPP]({link_wa})', unsafe_allow_html=True)
        st.info("📡 Enviando señal de éxito a Meta Ads...")
    else:
        st.error("Por favor llena el nombre y el WhatsApp")
