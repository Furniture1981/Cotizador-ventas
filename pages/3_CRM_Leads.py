import streamlit as st
import pandas as pd
from database import (guardar_lead, obtener_leads, actualizar_estado_lead,
                      stats_leads)

st.set_page_config(page_title="CRM Leads", page_icon="📇", layout="wide")
st.title("📇 CRM — Leads & Seguimiento")
st.caption("Fuente principal: Apollo.io | Estado de pipeline MAGNEX INTERNATIONAL")

# ── Stats ─────────────────────────────────────────────────────────────────────
stats = stats_leads()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Leads", stats["total"])
c2.metric("Nuevos",      stats["por_estado"].get("nuevo", 0))
c3.metric("Contactados", stats["por_estado"].get("contactado", 0))
c4.metric("Emails enviados", stats["emails"])

st.divider()
tab1, tab2 = st.tabs(["📋 Pipeline", "➕ Agregar Lead Manual"])

ESTADOS = ["nuevo", "contactado", "respondio", "interesado", "negociando", "cerrado", "descartado"]
PRODUCTOS = ["Pintura Industrial", "Aceite de Palma", "Fertilizantes", "Acero Estructural",
             "Furniture Cleans"]
PAISES = ["Panamá", "Costa Rica", "Colombia", "Guatemala", "República Dominicana",
          "Honduras", "El Salvador", "México", "Ecuador", "Perú", "Chile", "Otro"]

# ── TAB 1: PIPELINE ───────────────────────────────────────────────────────────
with tab1:
    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        filtro_estado = st.selectbox("Filtrar por estado", ["todos"] + ESTADOS)
    with col_filtro2:
        filtro_prod = st.selectbox("Filtrar por producto", ["todos"] + PRODUCTOS)

    estado_arg = None if filtro_estado == "todos" else filtro_estado
    leads = obtener_leads(estado=estado_arg)
    if filtro_prod != "todos":
        leads = [l for l in leads if l["producto"] == filtro_prod]

    if not leads:
        st.info("Sin leads con ese filtro.")
    else:
        for lead in leads:
            with st.expander(f"**{lead['empresa']}** — {lead['nombre']} | {lead['producto']} | {lead['estado'].upper()}"):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"📧 {lead['email']} | 🌎 {lead['pais']} | 💼 {lead['cargo']}")
                    if lead["notas"]:
                        st.caption(f"Notas: {lead['notas']}")
                    st.caption(f"Fuente: {lead['fuente']} — Agregado: {lead['fecha']}")
                with col_b:
                    nuevo_estado = st.selectbox(
                        "Estado", ESTADOS,
                        index=ESTADOS.index(lead["estado"]),
                        key=f"est_{lead['id']}"
                    )
                    if st.button("Actualizar", key=f"upd_{lead['id']}"):
                        actualizar_estado_lead(lead["id"], nuevo_estado)
                        st.success("✅ Actualizado")
                        st.rerun()

    st.divider()
    leads_all = obtener_leads(limit=1000)
    if leads_all:
        df = pd.DataFrame(leads_all)[["fecha","nombre","empresa","cargo","email",
                                       "pais","producto","estado","fuente"]]
        df.columns = ["Fecha","Nombre","Empresa","Cargo","Email","País","Producto","Estado","Fuente"]
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Exportar todos los leads CSV", csv, "leads_magnex.csv", "text/csv")

# ── TAB 2: AGREGAR LEAD ───────────────────────────────────────────────────────
with tab2:
    st.subheader("Agregar lead manualmente")
    with st.form("form_lead"):
        c1, c2 = st.columns(2)
        nombre_l  = c1.text_input("Nombre")
        empresa_l = c2.text_input("Empresa")
        cargo_l   = c1.text_input("Cargo / Título")
        email_l   = c2.text_input("Email")
        pais_l    = c1.selectbox("País", PAISES)
        prod_l    = c2.selectbox("Producto de interés", PRODUCTOS)
        fuente_l  = c1.selectbox("Fuente", ["Apollo", "LinkedIn", "Referido", "Web", "Otro"])
        notas_l   = st.text_area("Notas", height=80)
        enviar_l  = st.form_submit_button("Guardar Lead", type="primary")

    if enviar_l:
        if not email_l:
            st.error("El email es obligatorio.")
        else:
            guardar_lead(nombre_l, empresa_l, cargo_l, email_l, pais_l, prod_l, fuente_l, notas_l)
            st.success(f"✅ Lead {nombre_l} guardado")
