import streamlit as st

st.set_page_config(page_title="Furniture Cleans - Cotizador", page_icon="🧼")

st.title("🧼 Cotizador de Servicios")

# Lista detallada basada en tus fotos
servicios_dict = {
    "--- COLCHONES ---": 0,
    "Colchón Twin (Limpieza) - $25": 25,
    "Colchón Full (Limpieza) - $35": 35,
    "Colchón Queen (Limpieza) - $45": 45,
    "Colchón King (Limpieza) - $55": 55,
    "--- SOFÁS / MUEBLES ---": 0,
    "Sofá 1 Puesto - $15": 15,
    "Sofá 2 Puestos - $30": 30,
    "Sofá 3 Puestos - $45": 45,
    "Sofá en L - $60": 60,
    "Silla de Comedor (c/u) - $5": 5,
    "Silla de Oficina - $10": 10,
    "Poltrona - $20": 20,
    "--- ALFOMBRAS ---": 0,
    "Alfombra Pequeña - $20": 20,
    "Alfombra Mediana - $40": 40,
    "Alfombra Grande - $60": 60,
    "--- AUTOS ---": 0,
    "Sedán (Asientos) - $40": 40,
    "SUV (Asientos) - $50": 50,
    "Camioneta (Asientos) - $60": 60,
    "Interior Completo - $80": 80,
    "--- OTROS ---": 0,
    "Fumigación Básica - $35": 35,
    "Fumigación Reforzada - $50": 50,
    "Pulimiento de Pisos (Ver inspección)": 0
}

with st.form("cotizador_form"):
    st.subheader("Datos de la Venta")
    nombre = st.text_input("Nombre del Cliente")
    whatsapp = st.text_input("WhatsApp (sin el 507)")
    
    servicio = st.selectbox("Seleccione el Servicio", list(servicios_dict.keys()))
    
    # El precio se puede editar si el vendedor hace un descuento o cargo extra
    precio_sugerido = servicios_dict[servicio]
    precio_final = st.number_input("Confirmar Precio ($)", value=float(precio_sugerido))
    
    enviar = st.form_submit_button("GENERAR COTIZACIÓN")

if enviar:
    if nombre and whatsapp:
        # Aquí se crea el mensaje para WhatsApp
        mensaje = f"Hola%20{nombre},%20te%20confirmamos%20el%20servicio%20de%20{servicio}%20por%20un%20valor%20de%20${precio_final}."
        link_wa = f"https://wa.me/507{whatsapp}?text={mensaje}"
        
        st.success("✅ Cotización generada con éxito")
        st.markdown(f'''
            <a href="{link_wa}" target="_blank">
                <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                    📲 Enviar WhatsApp al Cliente
                </button>
            </a>
            ''', unsafe_allow_html=True)
    else:
        st.error("⚠️ Por favor rellena el nombre y el WhatsApp")
