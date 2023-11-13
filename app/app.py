from flask import Flask, render_template, json, request, request, redirect, session, url_for
import requests

app = Flask(__name__)

app.secret_key = '123456789'

#####################
###    LOGOUT     ###
#####################
@app.route('/logout')
def logout():

    session.pop('username', None)
    session.pop('project', None)
    session.pop('transaction', None)
    session.pop('email', None)
    session.pop('ID_USER', None)
    return redirect(url_for('login'))


#####################
###   REGISTER    ###
#####################


@app.route('/register', methods=['POST', 'GET'])
def register():
    var_error = ''
    if request.method == 'POST':
        nombre = request.form["nombre"]
        email = request.form["email"]
        contra = request.form["contrasena"]

        response = register_user(nombre, email, contra)

        if response.get('correcto'):
            datos = response.get('datos')
            session['username'] = nombre
            session['email'] = email
            session['project'] = ''
            session['ID_USER'] = datos.get('id')
            return redirect(url_for('user_menu'))
        else:
            var_error = response.get('error')
    
    return render_template('index.html', error=var_error)

def register_user(nombre, email, contra):
    db_url = "http://flask-api:5001/register"  # Utiliza el nombre del servicio de la base de datos
    payload = {'nombre': nombre, 'email': email, 'contra': contra}
    response = requests.post(db_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return None



#####################
###     LOGIN     ###
#####################

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
            session['project'] = ''
            session['ID_USER'] = datos.get('id')
            return redirect(url_for('user_menu'))
        else:
            return render_template('index.html', error1=response.get('error'))
    else:
        return render_template('index.html', error1='')

def login_user(email, contra):
    db_url = "http://flask-api:5001/"  # Utiliza el nombre del servicio de la base de datos
    payload = {'email': email, 'contra': contra}
    response = requests.post(db_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return data


#####################
###   USER_MENU   ###
#####################


@app.route('/user_menu', methods=['POST', 'GET'])
def user_menu():
    id=session['ID_USER']
    proyecto_json = ''

    if id is None:
        return redirect(url_for('/', error='Vuelve a iniciar sesión.'))
    else:
        response = user_menu_datos(id)
        proyecto_json = response.get('datos')
        
    datos = {
        'user': session['username'],
        'info': proyecto_json 
    }
    return render_template('user_menu.html', datos=datos)

    
def user_menu_datos(id):
    db_url = "http://flask-api:5001/user_menu"  
    payload = {'id': id}
    response = requests.post(db_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return None



#####################
###     CREATE    ###
#####################

@app.route('/create_project', methods=['POST', 'GET'])
def create_project():
    id=session['ID_USER']
    datos = {
                'user': session['username'],
                'error': '',
                'idproyecto': '',
                'datos': None
            }

    if id is None:
        return redirect(url_for('/', error='Vuelve a iniciar sesión.'))
    else:
        if request.method == 'POST':
            nombre = request.form["nombre"]
            contra = request.form["contrasena"]
            presupuesto = request.form["presupuesto"]
            response = crear_proyecto(id, nombre, contra, presupuesto)
            
            if response.get('correcto'):
                d = response.get('datos')
                datos['error'] = response.get('error')

                # TODO IGUAL DEVOLVER EL ID DEL PROYECTO CUANDO REDIRIJAMOS AL MENU DEL PROYECTO
                session['project'] = d['idproyecto']
                datos['idproyecto'] = d['idproyecto']
                return redirect(url_for('project_menu', datos=datos))
            else:
                datos['error'] = response.get('error')
        
    return render_template('create_project.html', datos=datos)

    
def crear_proyecto(id, nombre, contra, presupuesto):
    db_url = "http://flask-api:5001/create_project"  
    payload = {'userid': id, 'nombre': nombre, 'contra': contra, 'presupuesto': presupuesto}
    response = requests.post(db_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return None



#####################
###     JOIN      ###
#####################

@app.route('/join_project', methods=['POST', 'GET'])
def join_project():
    id=session['ID_USER']
    datos = {
                'user': session['username'],
                'error': '',
                'idproyecto': '',
                'datos': None
            }      

    if id is None:
        return redirect(url_for('/', error='Vuelve a iniciar sesión.'))
    else:
        if request.method == 'POST':
            idproyecto = request.form["idproyecto"]
            contra = request.form["contrasena"]
            response = acceder_proyecto(id, idproyecto, contra)
            session['project'] = d['idproyecto']
            
            if response.get('correcto'):
                d = response.get('datos')
                datos['error'] = response.get('error')

                # TODO IGUAL DEVOLVER EL ID DEL PROYECTO CUANDO REDIRIJAMOS AL MENU DEL PROYECTO
                
                datos['idproyecto'] = d['idproyecto']
                return redirect(url_for('project_menu', datos=datos))
            else:
                datos['error'] = response.get('error')
        
    return render_template('join_project.html', datos=datos)

    
def acceder_proyecto(userid, idproyecto, contra):
    db_url = "http://flask-api:5001/create_project"  
    payload = {'userid': userid, 'idproyecto': idproyecto, 'contra': contra}
    response = requests.post(db_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return None




#####################
###  PROJECT_MENU ###
#####################


@app.route('/project_menu', methods=['POST', 'GET'])
def project_menu():
    id=session['ID_USER']
    
    if request.form["idproyecto"] is not None:
        session['project'] = request.form["idproyecto"]
    idproyecto=session['project']

    if id is None:
        return redirect(url_for('/', error='Vuelve a iniciar sesión.'))
    else:  
        datos = {
                'user': session['username'],
                'error': '',
                'idproyecto': idproyecto,
                'datos': None
            }      
        return render_template('project_menu.html', datos=datos)

    
# def project_menu_datos(id):
#     db_url = "http://flask-api:5001/project_menu"  
#     payload = {'id': id}
#     response = requests.get(db_url, json=payload)
#     if response.status_code == 200:
#         data = response.json()
#         return data
#     else:
#         print(f"Error en la solicitud. Código de estado: {response.status_code}")
#         return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
