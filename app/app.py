from flask import Flask, render_template, json, request, request, redirect, session, url_for
import requests

app = Flask(__name__)

app.secret_key = '123456789'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        nombre = request.form["nombre"]
        email = request.form["email"]
        contra = request.form["contrasena"]

        response = register_user(nombre, email, contra)
        print(type(response))

        if response.get('correcto'):
            datos = response.get('datos')
            session['username'] = nombre
            session['email'] = email
            session['ID_USER'] = datos.get('id')
            return redirect(url_for('user_menu'))
        else:
            return redirect(url_for('login', error=response.get('error')))
    return render_template('index.html', error='')

def register_user(nombre, email, contra):
    db_url = "http://flask-api:5001/register"  # Utiliza el nombre del servicio de la base de datos
    payload = {'nombre': nombre, 'email': email, 'contra': contra}
    response = requests.post(db_url, json=payload)
    return response

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email2"]
        contra = request.form["contrasena2"]

        response = login_user(email, contra)
        if response.get('correcto'):
            datos = response.get('datos')
            session['username'] = datos.get('nombre')
            session['email'] = email
            session['ID_USER'] = datos.get('id')
            return redirect(url_for('user_menu'))
        else:
            return redirect(url_for('login', error=response.get('error')))

    return render_template('index.html', error='')

def login_user(email, contra):
    db_url = "http://flask-api:5001/login"  # Utiliza el nombre del servicio de la base de datos
    payload = {'email': email, 'contra': contra}
    response = requests.post(db_url, json=payload)
    return response

@app.route('/user_menu', methods=['POST', 'GET'])
def user_menu():
    id=session['ID_USER']
    proyecto_json = ''

    if id is None:
        return redirect(url_for('login', error='Vuelve a iniciar sesión.'))
    else:
        response = user_menu_datos(id)
        proyecto_json = response.get('datos')
        
    datos = {
        'user': session['username'],
        'proyectos': proyecto_json 
    }
    return render_template('user_menu.html', datos=datos)

    
def user_menu_datos(id):
    db_url = "http://flask-api:5001/user_menu"  
    payload = {'id': id}
    response = requests.post(db_url, json=payload)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
