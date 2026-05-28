import streamlit as st
from urllib.parse import quote

st.set_page_config(page_title="Furniture Cleans - Cotizador", page_icon="🧼", layout="centered")

SERVICIOS = {
    "COLCHONES": {
        "Colchón Twin": 25,
        "Colchón Full": 35,
        "Colchón Queen": 45,
        "Colchón King": 55,
    },
    "SOFÁS / MUEBLES": {
        "Sofá 1 Puesto": 15,
        "Sofá 2 Puestos": 30,
        "Sofá 3 Puestos": 45,
        "Sofá en L": 60,
        "Silla de Comedor (c/u)": 5,
        "Silla de Oficina": 10,
        "Poltrona": 20,
    },
    "ALFOMBRAS": {
        "Alfombra Pequeña": 20,
        "Alfombra Mediana": 40,
        "Alfombra Grande": 60,
    },
    "AUTOS": {
        "Sedán (Asientos)": 40,
        "SUV (Asientos)": 50,
        "Camioneta (Asientos)": 60,
        "Interior Completo": 80,
    },
    "OTROS": {
        "Fumigación Básica": 35,
        "Fumigación Reforzada": 50,
        "Pulimiento de Pisos": 0,
    },
}

if "carrito" not in st.session_state:
    st.session_state.carrito = []

st.title("🧼 Cotizador de Servicios")
st.caption("Furniture Cleans — Panamá")

# --- Datos del cliente ---
st.subheader("👤 Datos del Cliente")
col1, col2 = st.columns(2)
with col1:
    nombre = st.text_input("Nombre del Cliente")
with col2:
    whatsapp = st.text_input("WhatsApp (sin 507)")

st.divider()

# --- Agregar servicios ---
st.subheader("➕ Agregar Servicios")
col_cat, col_serv, col_qty = st.columns([2, 3, 1])

with col_cat:
    categoria = st.selectbox("Categoría", list(SERVICIOS.keys()), label_visibility="collapsed",
                             placeholder="Categoría")

with col_serv:
    opciones = list(SERVICIOS[categoria].keys())
    seleccion = st.selectbox("Servicio", opciones, label_visibility="collapsed")

precio_base = SERVICIOS[categoria][seleccion]

with col_qty:
    cantidad = st.number_input("Cant.", min_value=1, value=1, label_visibility="collapsed")

col_precio, col_agregar = st.columns([2, 1])
with col_precio:
    precio_unitario = st.number_input(
        "Precio unitario ($)",
        min_value=0.0,
        value=float(precio_base),
        step=1.0,
        help="Puedes editar el precio para aplicar descuentos o ajustes"
    )
with col_agregar:
    st.write("")
    if st.button("Agregar al carrito", use_container_width=True):
        st.session_state.carrito.append({
            "servicio": seleccion,
            "cantidad": cantidad,
            "precio_unit": precio_unitario,
            "subtotal": round(cantidad * precio_unitario, 2),
        })
        st.rerun()

st.divider()

# --- Carrito ---
st.subheader("🛒 Servicios Seleccionados")

if not st.session_state.carrito:
    st.info("Aún no has agregado servicios.")
else:
    for i, item in enumerate(st.session_state.carrito):
        c1, c2, c3, c4 = st.columns([4, 1, 2, 1])
        c1.write(item["servicio"])
        c2.write(f'x{item["cantidad"]}')
        c3.write(f'**${item["subtotal"]:.2f}**')
        if c4.button("❌", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()

    subtotal = sum(item["subtotal"] for item in st.session_state.carrito)

    st.divider()
    col_desc, col_total = st.columns([2, 2])
    with col_desc:
        descuento_pct = st.number_input("Descuento (%)", min_value=0, max_value=100, value=0, step=5)
    with col_total:
        monto_descuento = round(subtotal * descuento_pct / 100, 2)
        total = round(subtotal - monto_descuento, 2)
        st.metric("TOTAL", f"${total:.2f}",
                  delta=f"-${monto_descuento:.2f} descuento" if descuento_pct > 0 else None,
                  delta_color="inverse")

    st.divider()

    # --- Generar cotización ---
    if st.button("📋 GENERAR COTIZACIÓN", type="primary", use_container_width=True):
        if not nombre or not whatsapp:
            st.error("⚠️ Por favor rellena el nombre y el WhatsApp del cliente.")
        else:
            lineas = "\n".join(
                f"• {it['servicio']} x{it['cantidad']} = ${it['subtotal']:.2f}"
                for it in st.session_state.carrito
            )
            if descuento_pct > 0:
                resumen = (
                    f"Hola {nombre}, aquí está tu cotización de Furniture Cleans:\n\n"
                    f"{lineas}\n\n"
                    f"Subtotal: ${subtotal:.2f}\n"
                    f"Descuento ({descuento_pct}%): -${monto_descuento:.2f}\n"
                    f"*TOTAL: ${total:.2f}*\n\n"
                    f"¡Gracias por preferirnos! 🧼"
                )
            else:
                resumen = (
                    f"Hola {nombre}, aquí está tu cotización de Furniture Cleans:\n\n"
                    f"{lineas}\n\n"
                    f"*TOTAL: ${total:.2f}*\n\n"
                    f"¡Gracias por preferirnos! 🧼"
                )

            link_wa = f"https://wa.me/507{whatsapp}?text={quote(resumen)}"

            st.success("✅ Cotización generada con éxito")
            st.code(resumen, language=None)
            st.markdown(
                f'<a href="{link_wa}" target="_blank">'
                f'<button style="background-color:#25D366;color:white;border:none;'
                f'padding:12px 24px;border-radius:8px;cursor:pointer;font-size:16px;width:100%">'
                f'📲 Enviar WhatsApp al Cliente</button></a>',
                unsafe_allow_html=True,
            )

            if st.button("🔄 Nueva Cotización"):
                st.session_state.carrito = []
                st.rerun()
