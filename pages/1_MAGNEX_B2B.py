import streamlit as st
import pandas as pd
from database import guardar_cotizacion_magnex, obtener_cotizaciones_magnex

st.set_page_config(page_title="MAGNEX B2B", page_icon="⚡", layout="wide")
st.title("⚡ Cotizador B2B — MAGNEX INTERNATIONAL")
st.caption("Broker | Sin inventario | Comisión vía LC + NCNDA/IMFPA")
st.divider()

PRODUCTOS = {
    "Pintura Industrial": {
        "unidades": ["galón", "barril (55 gal)", "litro", "tonelada"],
        "precio_ref": 18.0,
        "comision_default": 4.0,
        "descripcion": "Anticorrosiva, epóxica, marina — target: astilleros, constructoras, mantenimiento",
    },
    "Aceite de Palma": {
        "unidades": ["tonelada métrica", "litro", "tambor (200L)"],
        "precio_ref": 850.0,
        "comision_default": 3.5,
        "descripcion": "Crudo / refinado — target: industria alimentaria, jabonería, cosmética",
    },
    "Fertilizantes": {
        "unidades": ["tonelada métrica", "saco (50kg)", "contenedor 20'"],
        "precio_ref": 450.0,
        "comision_default": 3.0,
        "descripcion": "NPK, úrea, fosfato — target: agroindustria",
    },
    "Acero Estructural": {
        "unidades": ["tonelada métrica", "varilla (c/u)", "contenedor 40'"],
        "precio_ref": 780.0,
        "comision_default": 3.0,
        "descripcion": "Perfiles, barras, láminas — target: constructoras grandes",
    },
}

PAISES = ["Panamá", "Costa Rica", "Colombia", "Guatemala", "República Dominicana",
          "Honduras", "El Salvador", "México", "Ecuador", "Perú", "Chile", "Otro"]
INCOTERMS = ["FOB", "CIF", "EXW", "CFR", "DAP"]
PAGOS = ["LC at sight", "LC 30 días", "LC 60 días", "T/T anticipado", "T/T contra documentos", "Otro"]

tab1, tab2 = st.tabs(["📋 Nueva Cotización", "📊 Historial"])

# ── TAB 1: NUEVA COTIZACIÓN ──────────────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("👤 Datos del Comprador")
        empresa  = st.text_input("Empresa / Comprador")
        contacto = st.text_input("Nombre del Contacto")
        email    = st.text_input("Email")
        pais     = st.selectbox("País", PAISES)

        st.subheader("📦 Producto")
        producto = st.selectbox("Producto", list(PRODUCTOS.keys()))
        info_prod = PRODUCTOS[producto]
        st.caption(f"ℹ️ {info_prod['descripcion']}")

        c1, c2 = st.columns(2)
        with c1:
            cantidad = st.number_input("Cantidad", min_value=0.1, value=1.0, step=0.5)
        with c2:
            unidad = st.selectbox("Unidad", info_prod["unidades"])

        st.subheader("💰 Precio y Comisión")
        c3, c4 = st.columns(2)
        with c3:
            precio_fob = st.number_input(
                "Precio FOB (USD)", min_value=0.0,
                value=float(info_prod["precio_ref"]), step=10.0
            )
        with c4:
            incoterm = st.selectbox("Incoterm", INCOTERMS)

        c5, c6 = st.columns(2)
        with c5:
            comision_pct = st.number_input(
                "Comisión (%)", min_value=0.0, max_value=20.0,
                value=float(info_prod["comision_default"]), step=0.5
            )
        with c6:
            pago = st.selectbox("Condición de Pago", PAGOS)

        notas = st.text_area("Notas / Especificaciones", height=80)

    with col_right:
        st.subheader("📊 Resumen")
        valor_total       = round(cantidad * precio_fob, 2)
        comision_estimada = round(valor_total * comision_pct / 100, 2)

        st.metric("Valor Total (USD)", f"${valor_total:,.2f}")
        st.metric("Comisión Estimada", f"${comision_estimada:,.2f}",
                  delta=f"{comision_pct}% sobre ${valor_total:,.2f}")

        st.divider()
        st.markdown("**Resumen FCO (borrador):**")
        fco = f"""
**FULL CORPORATE OFFER — MAGNEX INTERNATIONAL**

Producto    : {producto}
Cantidad    : {cantidad} {unidad}
Incoterm    : {incoterm}
Precio FOB  : USD {precio_fob:,.2f} / {unidad}
Valor Total : USD {valor_total:,.2f}
Pago        : {pago}
Comprador   : {empresa or '___'} — {pais}
Contacto    : {contacto or '___'} | {email or '___'}
"""
        st.code(fco, language=None)

        if st.button("💾 GUARDAR COTIZACIÓN", type="primary", use_container_width=True):
            if not empresa or not contacto or not email:
                st.error("Completa empresa, contacto y email.")
            else:
                guardar_cotizacion_magnex({
                    "empresa": empresa, "contacto": contacto, "email": email,
                    "pais": pais, "producto": producto, "cantidad": cantidad,
                    "unidad": unidad, "precio_fob": precio_fob, "incoterm": incoterm,
                    "pago": pago, "comision_pct": comision_pct,
                    "valor_total": valor_total, "comision_estimada": comision_estimada,
                    "notas": notas,
                })
                st.success("✅ Cotización guardada")
                st.balloons()

# ── TAB 2: HISTORIAL ─────────────────────────────────────────────────────────
with tab2:
    data = obtener_cotizaciones_magnex()
    if not data:
        st.info("Sin cotizaciones aún.")
    else:
        df = pd.DataFrame(data)[["fecha","empresa","pais","producto","cantidad","unidad",
                                  "valor_total","comision_pct","comision_estimada","pago"]]
        df.columns = ["Fecha","Empresa","País","Producto","Cantidad","Unidad",
                      "Valor USD","Com%","Comisión USD","Pago"]
        st.dataframe(df, use_container_width=True, hide_index=True)
        total_com = df["Comisión USD"].sum()
        st.metric("Total comisiones acumuladas", f"${total_com:,.2f}")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar CSV", csv, "magnex_cotizaciones.csv", "text/csv",
                           use_container_width=True)
