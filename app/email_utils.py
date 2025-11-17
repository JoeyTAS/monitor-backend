import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

def send_alert_email(recipient: str, down_sites: list):
    subject = "⚠ Alerta: Sitios caídos detectados"

    # Crear tabla HTML
    rows = "".join(
        f"<tr><td style='padding: 8px; border: 1px solid #ddd;'>{url}</td></tr>"
        for url in down_sites
    )

    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #c0392b;">⚠ Alerta de Sitios Caídos</h2>

        <p>Se detectaron los siguientes sitios caídos durante el escaneo:</p>

        <table style="border-collapse: collapse; width: 100%; max-width: 500px;">
            <tr style="background: #f2f2f2;">
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">
                    Sitio detectado como caído
                </th>
            </tr>
            {rows}
        </table>

        <p style="margin-top: 20px; color: #888;">
            Monitor Backend – Python<br>
            Reporte generado automáticamente.
        </p>
    </div>
    """

    # Config email
    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
            print("📧 Email enviado con éxito.")
            return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False
