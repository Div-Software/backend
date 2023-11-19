from flask import Flask, Blueprint, request, jsonify, make_response
from flask_mail import Mail, Message
import requests

app = Flask(__name__)
mail = Mail(app)

def generate_email_template(subject, message, button_text=None, button_link=None, language="es"):
        logo_url = "https://apidgalerydos.devtop.online/static/logo.png"
        
        # Generamos el botón solo si ambos argumentos, texto y enlace, están presentes.
        button_html = ''
        if button_text and button_link:
                button_html = f'<a href="{button_link}" style="display:inline-block; padding: 10px 20px; color: #fff; background: linear-gradient(25deg, #000000 0%, #ff004f 100%); border-radius: 5px; text-decoration: none; font-size: 18px;">{button_text}</a>'
        
        return f'''
        <!DOCTYPE html>
        <html lang="{language}" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <meta name="x-apple-disable-message-reformatting">
            <title>{subject}</title>
            <style>
                table, td, div, h1, p {{font-family: Arial, sans-serif;}}
            </style>
        </head>
        <body style="margin:0;padding:0;">
            <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:#ffffff;">
                <tr>
                    <td align="center" style="padding:0;">
                        <table role="presentation" style="width:602px;border-collapse:collapse;border:1px solid #cccccc;border-spacing:0;text-align:left;">
                            <tr>
                                <td align="center" style="padding:40px 0 30px 0;background: linear-gradient(25deg, #000000 0%, #301080 100%);">
                                    <img src="{logo_url}" alt="Logo de la empresa" width="200" style="height:auto;display:block;" />
                                </td>
                            </tr>
                            <tr>
                                <td style="padding:36px 30px 20px 30px;">
                                    <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;">
                                        <tr>
                                            <td style="padding:0 0 0 0;color:#153643;">
                                                <h1 style="font-size:24px;margin:0 0 20px 0;font-family: Arial, sans-serif;">{subject}</h1>
                                                <p style="margin:0 0 12px 0;font-size:16px;line-height:24px;font-family: Arial, sans-serif;">{message}</p>
                                                {button_html}
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        '''


@app.route('/api/v1/contact', methods=['POST'])
def contact_form():
    try:
        # Obtener los campos del formulario de contacto
        name = request.get_json().get("name", "")
        email = request.get_json().get("email", "").lower()
        recaptcha_response = request.get_json().get("recaptchaResponse", "")
        message = request.get_json().get("message", "")
        source = request.get_json().get("source", "")


        # Validar campos requeridos
        if not all([name, email, message]):
            response_message = "Missing required fields"
            return jsonify({"error": response_message}), 400
        
        # Verificar reCAPTCHA
        if not verify_recaptcha(recaptcha_response):
            response_message = "Invalid reCAPTCHA"
            return jsonify({"error": response_message}), 400
        
        # Preparar el correo para el administrador
        send_contact_email(name, email, message, source)

        response_message = "Contact message sent successfully"
        return jsonify({"message": response_message}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def verify_recaptcha(recaptcha_response):
    payload = {
        'secret': app.config['RECAPTCHA_SECRET_KEY'],
        'response': recaptcha_response
    }
    
    response = requests.post(app.config['RECAPTCHA_VERIFY_URL'], data=payload)
    result = response.json()

    return result.get('success')

def send_contact_email(name, email, message, source=None, language="es"):
    print(f"Language in send_contact_email: {language}")

    subject = "Nuevo mensaje de contacto de " + name
    content = f'''
        Has recibido un nuevo mensaje de contacto:<br><br>
        <strong>Nombre</strong>: {name}<br>
        <strong>Correo Electrónico</strong>: {email}<br>
        <strong>Mensaje</strong>:<br>
    {message}
'''
    # Usar la función de plantilla para obtener el cuerpo del correo
    body = generate_email_template(subject, content)

    msg = Message(subject=subject, sender=app.config['MAIL_USERNAME'], recipients=[app.config['ADMIN_EMAIL']])
    msg.html = body
    
    with app.app_context():
        mail.send(msg)

def generate_email_template(subject, content):
    # Implement the logic to generate the email template
    pass


