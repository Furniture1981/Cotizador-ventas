import streamlit as st
import os
from email_sender import enviar_email, probar_conexion
from database import obtener_leads, registrar_email_enviado, actualizar_estado_lead

st.set_page_config(page_title="Automatización Email", page_icon="📧", layout="wide")
st.title("📧 Automatización de Emails — MAGNEX INTERNATIONAL")
st.caption("Powered by Zoho Mail SMTP")

# ── Config ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ Configuración SMTP")
    smtp_user = st.text_input("Email remitente", value=os.getenv("ZOHO_EMAIL", ""))
    smtp_pass = st.text_input("Contraseña Zoho", type="password",
                              value=os.getenv("ZOHO_PASSWORD", ""))
    st.caption("O configúralos en el archivo .env")

    if st.button("🔌 Probar Conexión"):
        ok, msg = probar_conexion(smtp_user, smtp_pass)
        if ok:
            st.success(f"✅ {msg}")
        else:
            st.error(f"❌ {msg}")

st.divider()

TEMPLATES = {
    "Pintura Industrial — Primer contacto": {
        "asunto": "Cotización Pintura Industrial — MAGNEX INTERNATIONAL",
        "cuerpo": """Estimado/a {nombre},

Mi nombre es Miguel González, CEO de MAGNEX INTERNATIONAL, empresa panameña especializada en intermediación de commodities industriales.

Me comunico porque entiendo que {empresa} trabaja en el sector de {sector}, y contamos con acceso a proveedores certificados de pintura industrial (anticorrosiva, epóxica, marina) a precios FOB competitivos.

Estaría encantado de enviarle una oferta preliminar (FCO) sin ningún compromiso.

¿Tiene 15 minutos esta semana para una llamada rápida?

Saludos,
Miguel González
CEO — MAGNEX INTERNATIONAL
mgonzalez@magnexinternational.com
+507 6593-3059
"Connecting Markets. Delivering Trust."
""",
    },
    "Aceite de Palma — Primer contacto": {
        "asunto": "Suministro Aceite de Palma — MAGNEX INTERNATIONAL",
        "cuerpo": """Estimado/a {nombre},

Soy Miguel González, CEO de MAGNEX INTERNATIONAL. Nos especializamos en intermediación de aceite de palma crudo y refinado desde productores certificados en Latinoamérica.

Entiendo que {empresa} podría tener interés en este commodity. Podemos ofrecerle:
• Contratos mensuales recurrentes
• Documentación completa (certificado de origen, análisis de calidad)
• Condiciones: FOB / CIF a su puerto

¿Le gustaría recibir nuestra propuesta formal?

Saludos,
Miguel González
MAGNEX INTERNATIONAL | mgonzalez@magnexinternational.com
""",
    },
    "Seguimiento — Sin respuesta": {
        "asunto": "Seguimiento — MAGNEX INTERNATIONAL",
        "cuerpo": """Estimado/a {nombre},

Hace unos días le escribí sobre nuestros servicios de intermediación de {producto}.

Quería hacer un seguimiento breve — ¿tuvo oportunidad de revisar mi mensaje?

Si el momento no es el adecuado, con gusto lo contacto en otro período.

Saludos,
Miguel González
MAGNEX INTERNATIONAL
""",
    },
}

tab1, tab2 = st.tabs(["📤 Envío por Lote", "✏️ Email Individual"])

# ── TAB 1: ENVÍO EN LOTE ──────────────────────────────────────────────────────
with tab1:
    st.subheader("Enviar a múltiples leads")

    col1, col2 = st.columns(2)
    with col1:
        template_sel = st.selectbox("Plantilla de email", list(TEMPLATES.keys()))
        estado_filtro = st.selectbox("Leads con estado", ["nuevo", "contactado", "respondio"])
    with col2:
        prod_filtro = st.selectbox("Producto", ["todos", "Pintura Industrial", "Aceite de Palma",
                                                "Fertilizantes", "Acero Estructural"])
        max_envios = st.number_input("Máximo de envíos", min_value=1, max_value=50, value=10)

    leads_disp = obtener_leads(estado=estado_filtro)
    if prod_filtro != "todos":
        leads_disp = [l for l in leads_disp if l["producto"] == prod_filtro]
    leads_disp = leads_disp[:max_envios]

    st.info(f"Se enviarán emails a **{len(leads_disp)} leads**")

    if leads_disp:
        preview = TEMPLATES[template_sel]
        lead_ej = leads_disp[0]
        preview_cuerpo = preview["cuerpo"].format(
            nombre=lead_ej.get("nombre", ""),
            empresa=lead_ej.get("empresa", ""),
            sector="su industria",
            producto=lead_ej.get("producto", ""),
        )
        with st.expander("Vista previa del email"):
            st.write(f"**Asunto:** {preview['asunto']}")
            st.text(preview_cuerpo)

    if st.button("🚀 ENVIAR EMAILS", type="primary", disabled=not leads_disp):
        if not smtp_user or not smtp_pass:
            st.error("Configura el email y contraseña en la barra lateral.")
        else:
            prog = st.progress(0)
            ok_count = 0
            for i, lead in enumerate(leads_disp):
                cuerpo_final = TEMPLATES[template_sel]["cuerpo"].format(
                    nombre=lead.get("nombre", ""),
                    empresa=lead.get("empresa", ""),
                    sector="su industria",
                    producto=lead.get("producto", ""),
                )
                exito, _ = enviar_email(
                    smtp_user, smtp_pass,
                    lead["email"],
                    TEMPLATES[template_sel]["asunto"],
                    cuerpo_final,
                )
                estado_nuevo = "contactado" if exito else lead["estado"]
                actualizar_estado_lead(lead["id"], estado_nuevo)
                registrar_email_enviado(lead["id"], lead["email"],
                                        TEMPLATES[template_sel]["asunto"],
                                        "enviado" if exito else "error")
                if exito:
                    ok_count += 1
                prog.progress((i + 1) / len(leads_disp))

            st.success(f"✅ {ok_count}/{len(leads_disp)} emails enviados correctamente")

# ── TAB 2: EMAIL INDIVIDUAL ───────────────────────────────────────────────────
with tab2:
    st.subheader("Enviar email individual")
    with st.form("form_email_ind"):
        dest   = st.text_input("Destinatario (email)")
        asunto = st.text_input("Asunto")
        cuerpo = st.text_area("Cuerpo del mensaje", height=250)
        enviar = st.form_submit_button("Enviar", type="primary")

    if enviar:
        if not smtp_user or not smtp_pass:
            st.error("Configura email y contraseña en la barra lateral.")
        elif not dest:
            st.error("Ingresa el destinatario.")
        else:
            ok, msg = enviar_email(smtp_user, smtp_pass, dest, asunto, cuerpo)
            if ok:
                st.success(f"✅ Email enviado a {dest}")
            else:
                st.error(f"❌ Error: {msg}")
