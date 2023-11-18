from flask import Flask, request, render_template
import requests
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from t_gmail import EMAIL_T

app = Flask(__name__)


#####################
###   REGISTRO    ###
#####################
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    username = data.get('username')

    remitente = "proyectoasmaitane@gmail.com"
    destinatario = email # Suponiendo que tienes un formulario con un campo 'destinatario'
    mensaje = f'''<html>
                    <body>
                        <div>
                        <h1>¡Hola {username}!</h1>
                        <p>Te damos la bienvenida a nuestra plataforma de gestión de presupuestos de proyectos. Estamos emocionados de que hayas decidido unirte a nosotros.</p>
                        <p>En BudgetBuddy, podrás organizar y supervisar los presupuestos de tus proyectos de manera eficiente. Explora nuestras potentes herramientas de gestión y mantén un control total sobre los costos y recursos de cada proyecto.</p>
                        <br>
                        <p>Invita a otros usuarios a unirse a tus proyectos facilitándoles el ID y la contraseña de estos </p>
                        <p>Recuerda siempre utilizar contraseñas seguras y compartir la información solo con aquellos que necesitan acceso. </p>
                        <br>
                        <p>Si necesitas ayuda en cualquier momento, no dudes en ponerte en contacto con nuestro equipo de soporte. Estamos aquí para asegurarnos de que tengas la mejor experiencia posible.</p>
                        <p>¡Comienza a gestionar tus proyectos y presupuestos ahora mismo!</p>
                        <p>Saludos,<br>
                        <br>
                        <p>BudgetBuddy</p>
                        </div>
                    </body>
                </html>''' 

    email = MIMEMultipart()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = "Registro en BudgetBuddy"
    email.attach(MIMEText(mensaje, 'html'))

    try:
        smtp = smtplib.SMTP_SSL("smtp.gmail.com")
        smtp.login(remitente, EMAIL_T)
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()
        mensaje = "¡Correo enviado con éxito!"
        correcto = True
    except Exception as e:
        mensaje = f"Error al enviar el correo: {str(e)}"
        correcto = False
    finally:
        return {'mensaje': mensaje, 'correcto': correcto}



#####################
###     JOIN      ###
#####################
@app.route('/join', methods=['POST'])
def join():
    data = request.json
    email = data.get('email')
    newuser = data.get('newuser')
    proyecto = data.get('proyecto')

    remitente = "proyectoasmaitane@gmail.com"
    destinatario = email # Suponiendo que tienes un formulario con un campo 'destinatario'
    mensaje = f'''<html>
                    <body>
                        <div>
                        <h1>¡Hola!</h1>
                        <p>Te informamos que el usuario {newuser} se ha unido a tu proyecto {proyecto}.</p>
                        <p>Ahora podéis gestionar juntos el proyecto.</p>
                        <br><br>
                        <p>¡Gracias por usar nuestro servicio!</p>
                        <br>
                        <p>BudgetBuddy</p>
                        </div>
                    </body>
                </html>''' 

    email = MIMEMultipart()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = "Nuevo Usuario en tu Proyecto!"
    email.attach(MIMEText(mensaje, 'html'))

    try:
        smtp = smtplib.SMTP_SSL("smtp.gmail.com")
        smtp.login(remitente, EMAIL_T)
        smtp.sendmail(remitente, destinatario, email.as_string())
        smtp.quit()
        mensaje = "¡Correo enviado con éxito!"
        correcto = True
    except Exception as e:
        mensaje = f"Error al enviar el correo: {str(e)}"
        correcto = False
    finally:
        return {'mensaje': mensaje, 'correcto': correcto}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)