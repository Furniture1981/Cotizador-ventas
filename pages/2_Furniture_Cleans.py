import streamlit as st
import pandas as pd
from urllib.parse import quote
from database import guardar_cotizacion, obtener_cotizaciones, stats_totales

st.set_page_config(page_title="Furniture Cleans", page_icon="🧼", layout="wide")
st.title("🧼 Cotizador — Furniture Cleans Service")

SERVICIOS = {
    "COLCHONES": {"Colchón Twin": 25, "Colchón Full": 35, "Colchón Queen": 45, "Colchón King": 55},
    "SOFÁS / MUEBLES": {"Sofá 1 Puesto": 15, "Sofá 2 Puestos": 30, "Sofá 3 Puestos": 45,
                        "Sofá en L": 60, "Silla de Comedor (c/u)": 5,
                        "Silla de Oficina": 10, "Poltrona": 20},
    "ALFOMBRAS": {"Alfombra Pequeña": 20, "Alfombra Mediana": 40, "Alfombra Grande": 60},
    "AUTOS": {"Sedán (Asientos)": 40, "SUV (Asientos)": 50,
              "Camioneta (Asientos)": 60, "Interior Completo": 80},
    "OTROS": {"Fumigación Básica": 35, "Fumigación Reforzada": 50, "Pulimiento de Pisos": 0},
}

if "carrito" not in st.session_state:
    st.session_state.carrito = []

tab1, tab2, tab3 = st.tabs(["📋 Nueva Cotización", "📊 Historial", "📈 Resumen"])

# ── TAB 1 ────────────────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre del Cliente")
    with col2:
        whatsapp = st.text_input("WhatsApp (sin 507)")

    st.divider()
    c1, c2, c3 = st.columns([2, 3, 1])
    with c1:
        cat = st.selectbox("Categoría", list(SERVICIOS.keys()))
    with c2:
        serv = st.selectbox("Servicio", list(SERVICIOS[cat].keys()))
    with c3:
        qty = st.number_input("Cant.", min_value=1, value=1)

    precio_base = SERVICIOS[cat][serv]
    c4, c5 = st.columns([3, 1])
    with c4:
        precio_u = st.number_input("Precio unitario ($)", min_value=0.0,
                                   value=float(precio_base), step=1.0)
    with c5:
        st.write("")
        st.write("")
        if st.button("Agregar ➕", use_container_width=True):
            st.session_state.carrito.append({
                "servicio": serv, "cantidad": qty,
                "precio_unit": precio_u,
                "subtotal": round(qty * precio_u, 2),
            })
            st.rerun()

    st.divider()
    st.subheader("🛒 Carrito")
    if not st.session_state.carrito:
        st.info("Agrega servicios arriba.")
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
            desc_pct = st.number_input("Descuento (%)", 0, 100, 0, step=5)
        with dc2:
            monto_desc = round(subtotal * desc_pct / 100, 2)
            total = round(subtotal - monto_desc, 2)
            st.metric("TOTAL", f"${total:.2f}",
                      delta=f"-${monto_desc:.2f}" if desc_pct else None,
                      delta_color="inverse")

        if st.button("📤 GENERAR COTIZACIÓN", type="primary", use_container_width=True):
            if not nombre or not whatsapp:
                st.error("Completa nombre y WhatsApp.")
            else:
                guardar_cotizacion(nombre, whatsapp, st.session_state.carrito,
                                   subtotal, desc_pct, monto_desc, total)
                lineas = "\n".join(
                    f"• {it['servicio']} ×{it['cantidad']} = ${it['subtotal']:.2f}"
                    for it in st.session_state.carrito
                )
                cuerpo = (
                    f"Hola {nombre}, aquí tu cotización de Furniture Cleans:\n\n{lineas}\n\n"
                    + (f"Subtotal: ${subtotal:.2f}\nDescuento ({desc_pct}%): -${monto_desc:.2f}\n"
                       if desc_pct else "")
                    + f"*TOTAL: ${total:.2f}*\n\n¡Gracias! 🧼"
                )
                link_wa = f"https://wa.me/507{whatsapp}?text={quote(cuerpo)}"
                st.success("✅ Cotización guardada")
                st.code(cuerpo, language=None)
                st.markdown(
                    f'<a href="{link_wa}" target="_blank">'
                    f'<button style="background:#25D366;color:#fff;border:none;padding:12px;'
                    f'border-radius:8px;cursor:pointer;font-size:16px;width:100%">'
                    f'📲 Enviar WhatsApp</button></a>',
                    unsafe_allow_html=True,
                )
                if st.button("🔄 Nueva Cotización"):
                    st.session_state.carrito = []
                    st.rerun()

# ── TAB 2 ────────────────────────────────────────────────────────────────────
with tab2:
    data = obtener_cotizaciones()
    if not data:
        st.info("Sin cotizaciones.")
    else:
        filas = [{"Fecha": c["fecha"], "Cliente": c["cliente"], "WhatsApp": c["whatsapp"],
                  "Servicios": ", ".join(f"{it['servicio']} ×{it['cantidad']}" for it in c["items"]),
                  "Descuento": f"{c['descuento_pct']}%", "Total": f"${c['total']:.2f}"}
                 for c in data]
        df = pd.DataFrame(filas)
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar CSV", csv, "furniture_cotizaciones.csv", "text/csv",
                           use_container_width=True)

# ── TAB 3 ────────────────────────────────────────────────────────────────────
with tab3:
    data = obtener_cotizaciones(500)
    if not data:
        st.info("Sin datos aún.")
    else:
        df = pd.DataFrame([{"Fecha": c["fecha"][:10], "Total": c["total"]} for c in data])
        c1, c2, c3 = st.columns(3)
        c1.metric("Cotizaciones", len(df))
        c2.metric("Total Facturado", f"${df['Total'].sum():,.2f}")
        c3.metric("Promedio", f"${df['Total'].mean():,.2f}")
        st.bar_chart(df.groupby("Fecha")["Total"].sum())
