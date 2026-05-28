import streamlit as st
import pandas as pd
from urllib.parse import quote
from database import guardar_cotizacion, obtener_cotizaciones, stats_totales

st.set_page_config(
    page_title="MAGNEX INTERNATIONAL — Cotizador",
    page_icon="⚡",
    layout="wide",
)

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
if "cotizacion_enviada" not in st.session_state:
    st.session_state.cotizacion_enviada = False

# ── Sidebar navegación ──────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=MAGNEX+INT.", use_container_width=True)
    st.title("MAGNEX INTERNATIONAL")
    pagina = st.radio("Navegación", ["📋 Nueva Cotización", "📊 Historial", "📈 Resumen"])
    st.divider()
    stats = stats_totales()
    st.metric("Total Cotizaciones", stats["total_cot"])
    st.metric("Total Facturado", f"${stats['total_ventas'] or 0:,.2f}")

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — NUEVA COTIZACIÓN
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "📋 Nueva Cotización":
    st.title("📋 Nueva Cotización")

    if st.session_state.cotizacion_enviada:
        st.success("✅ Cotización guardada y lista para enviar")
        if st.button("🔄 Crear Nueva Cotización"):
            st.session_state.carrito = []
            st.session_state.cotizacion_enviada = False
            st.rerun()
        st.stop()

    # Datos del cliente
    st.subheader("👤 Cliente")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre del Cliente")
    with col2:
        whatsapp = st.text_input("WhatsApp (sin 507)")

    st.divider()

    # Agregar servicios
    st.subheader("➕ Agregar Servicio")
    c1, c2, c3 = st.columns([2, 3, 1])
    with c1:
        categoria = st.selectbox("Categoría", list(SERVICIOS.keys()))
    with c2:
        seleccion = st.selectbox("Servicio", list(SERVICIOS[categoria].keys()))
    with c3:
        cantidad = st.number_input("Cant.", min_value=1, value=1)

    precio_base = SERVICIOS[categoria][seleccion]
    c4, c5 = st.columns([3, 1])
    with c4:
        precio_unit = st.number_input("Precio unitario ($)", min_value=0.0,
                                      value=float(precio_base), step=1.0)
    with c5:
        st.write("")
        st.write("")
        if st.button("Agregar ➕", use_container_width=True):
            st.session_state.carrito.append({
                "servicio": seleccion,
                "cantidad": cantidad,
                "precio_unit": precio_unit,
                "subtotal": round(cantidad * precio_unit, 2),
            })
            st.rerun()

    st.divider()

    # Carrito
    st.subheader("🛒 Servicios en esta Cotización")
    if not st.session_state.carrito:
        st.info("Agrega servicios arriba para comenzar.")
    else:
        for i, item in enumerate(st.session_state.carrito):
            r1, r2, r3, r4 = st.columns([5, 1, 2, 1])
            r1.write(item["servicio"])
            r2.write(f'×{item["cantidad"]}')
            r3.write(f'**${item["subtotal"]:.2f}**')
            if r4.button("✕", key=f"rm_{i}"):
                st.session_state.carrito.pop(i)
                st.rerun()

        subtotal = sum(x["subtotal"] for x in st.session_state.carrito)
        st.divider()
        dc1, dc2 = st.columns(2)
        with dc1:
            descuento_pct = st.number_input("Descuento (%)", 0, 100, 0, step=5)
        with dc2:
            monto_desc = round(subtotal * descuento_pct / 100, 2)
            total = round(subtotal - monto_desc, 2)
            st.metric("TOTAL A COBRAR", f"${total:.2f}",
                      delta=f"-${monto_desc:.2f}" if descuento_pct else None,
                      delta_color="inverse")

        st.divider()
        if st.button("📤 GENERAR Y GUARDAR COTIZACIÓN", type="primary", use_container_width=True):
            if not nombre or not whatsapp:
                st.error("⚠️ Completa el nombre y WhatsApp del cliente.")
            else:
                guardar_cotizacion(
                    nombre, whatsapp,
                    st.session_state.carrito,
                    subtotal, descuento_pct, monto_desc, total,
                )
                lineas = "\n".join(
                    f"• {it['servicio']} ×{it['cantidad']} = ${it['subtotal']:.2f}"
                    for it in st.session_state.carrito
                )
                cuerpo = (
                    f"Hola {nombre}, aquí tu cotización de MAGNEX INTERNATIONAL:\n\n"
                    f"{lineas}\n\n"
                    + (f"Subtotal: ${subtotal:.2f}\nDescuento ({descuento_pct}%): -${monto_desc:.2f}\n"
                       if descuento_pct else "")
                    + f"*TOTAL: ${total:.2f}*\n\n¡Gracias por preferirnos! ⚡"
                )
                link_wa = f"https://wa.me/507{whatsapp}?text={quote(cuerpo)}"
                st.session_state.cotizacion_enviada = True
                st.session_state.link_wa = link_wa
                st.session_state.cuerpo_msg = cuerpo
                st.rerun()

    # Mostrar enlace si ya se generó
    if st.session_state.get("link_wa"):
        st.code(st.session_state.cuerpo_msg, language=None)
        st.markdown(
            f'<a href="{st.session_state.link_wa}" target="_blank">'
            f'<button style="background:#25D366;color:#fff;border:none;padding:14px;'
            f'border-radius:8px;cursor:pointer;font-size:16px;width:100%">'
            f'📲 Enviar por WhatsApp</button></a>',
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — HISTORIAL
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📊 Historial":
    st.title("📊 Historial de Cotizaciones")

    cotizaciones = obtener_cotizaciones()
    if not cotizaciones:
        st.info("Aún no hay cotizaciones registradas.")
    else:
        filas = []
        for c in cotizaciones:
            servicios_str = ", ".join(
                f"{it['servicio']} ×{it['cantidad']}" for it in c["items"]
            )
            filas.append({
                "Fecha": c["fecha"],
                "Cliente": c["cliente"],
                "WhatsApp": c["whatsapp"],
                "Servicios": servicios_str,
                "Descuento": f"{c['descuento_pct']}%",
                "Total": f"${c['total']:.2f}",
            })

        df = pd.DataFrame(filas)
        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Descargar CSV",
            csv,
            "cotizaciones_magnex.csv",
            "text/csv",
            use_container_width=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 3 — RESUMEN
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "📈 Resumen":
    st.title("📈 Resumen de Ventas")

    cotizaciones = obtener_cotizaciones(limit=500)
    if not cotizaciones:
        st.info("Sin datos aún.")
    else:
        df_raw = pd.DataFrame([
            {"Fecha": c["fecha"][:10], "Total": c["total"], "Cliente": c["cliente"]}
            for c in cotizaciones
        ])

        col1, col2, col3 = st.columns(3)
        col1.metric("Cotizaciones", len(df_raw))
        col2.metric("Total Facturado", f"${df_raw['Total'].sum():,.2f}")
        col3.metric("Promedio por Cot.", f"${df_raw['Total'].mean():,.2f}")

        st.divider()
        st.subheader("Ventas por Día")
        ventas_dia = df_raw.groupby("Fecha")["Total"].sum().reset_index()
        st.bar_chart(ventas_dia.set_index("Fecha"))

        st.subheader("Clientes Frecuentes")
        top = df_raw.groupby("Cliente").agg(
            Cotizaciones=("Total", "count"),
            Total_Comprado=("Total", "sum")
        ).sort_values("Total_Comprado", ascending=False).head(10)
        st.dataframe(top, use_container_width=True)
