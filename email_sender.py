import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ZOHO_SMTP_HOST = "smtppro.zoho.com"
ZOHO_SMTP_PORT = 587


def get_zoho_creds():
    """Lee credenciales de Streamlit secrets o variables de entorno."""
    try:
        import streamlit as st
        email = st.secrets.get("ZOHO_EMAIL", os.getenv("ZOHO_EMAIL", ""))
        password = st.secrets.get("ZOHO_PASSWORD", os.getenv("ZOHO_PASSWORD", ""))
    except Exception:
        email = os.getenv("ZOHO_EMAIL", "")
        password = os.getenv("ZOHO_PASSWORD", "")
    return email, password


def enviar_email(smtp_user: str, smtp_pass: str, destinatario: str,
                 asunto: str, cuerpo: str) -> tuple[bool, str]:
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = smtp_user
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

        with smtplib.SMTP(ZOHO_SMTP_HOST, ZOHO_SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, destinatario, msg.as_string())

        return True, "Email enviado"
    except smtplib.SMTPAuthenticationError:
        return False, "Credenciales incorrectas — verifica email y contraseña Zoho"
    except smtplib.SMTPException as e:
        return False, f"Error SMTP: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def probar_conexion(smtp_user: str, smtp_pass: str) -> tuple[bool, str]:
    try:
        with smtplib.SMTP(ZOHO_SMTP_HOST, ZOHO_SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
        return True, f"Conexión exitosa como {smtp_user}"
    except smtplib.SMTPAuthenticationError:
        return False, "Credenciales incorrectas"
    except Exception as e:
        return False, str(e)
