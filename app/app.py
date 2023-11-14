from flask import Flask, render_template, json, request, request, redirect, session, url_for
import requests

app = Flask(__name__)

app.secret_key = '123456789'

def get_presupuesto(idproyecto):
    db_url = "http://flask-api:5001/project_menu"  
    payload = {'idproyecto': idproyecto}
    response = requests.get(db_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return None

#####################
###    LOGOUT     ###
#####################
@app.route('/logout')
def logout():
    print('!!!!!!!!!!!!!!!!!!!!LOGOUT!!!!!!!!!!!!!!!!!!!!')
    session.pop('username', None)
    session.pop('project', None)
    session.pop('transaction', None)
    session.pop('email', None)
    session.pop('ID_USER', None)
    return redirect(url_for('register'))


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
            session['transaction'] = ''
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
            session['transaction'] = ''
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
        return redirect(url_for('register', error='Vuelve a iniciar sesión.'))
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
        return redirect(url_for('register', error='Vuelve a iniciar sesión.'))
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
        return redirect(url_for('register', error='Vuelve a iniciar sesión.'))
    else:
        if request.method == 'POST':
            idproyecto = request.form["idproyecto"]
            contra = request.form["contrasena"]
            response = acceder_proyecto(id, idproyecto, contra)
            
            if response.get('correcto'):
                d = response.get('datos')
                datos['error'] = response.get('error')
                session['project'] = d['idproyecto']

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
    if request.method == 'POST':
        if request.form["idproyecto"] is not None:
            session['project'] = request.form["idproyecto"]
    idproyecto=session['project']

    if id is None:
        return redirect(url_for('register', error='Vuelve a iniciar sesión.'))
    else:
        response = get_presupuesto(idproyecto)  
        d=response.get('datos')
        datos = {
                'user': session['username'],
                'error': '',
                'idproyecto': idproyecto,
                'presupuesto': d['presupuesto'],
                'datos': d
            }      
        return render_template('project_menu.html', datos=datos)

    
# def project_menu_datos(idproyecto):
#     db_url = "http://flask-api:5001/project_menu"  
#     payload = {'idproyecto': idproyecto}
#     response = requests.get(db_url, json=payload)
#     if response.status_code == 200:
#         data = response.json()
#         return data
#     else:
#         print(f"Error en la solicitud. Código de estado: {response.status_code}")
#         return None

#####################
###  TRANSACTION  ###
#####################
@app.route('/transaction_menu', methods=['POST', 'GET'])
def transaction_menu():
    id=session['ID_USER']
    idproyecto=session['project']
    datos = {
                'user': session['username'],
                'error': '',
                'transactionId': '', 
                'idproyecto': idproyecto,
                'presupuesto': None,
                'datos': None
            }      
    if id is None:
        return redirect(url_for('register', error='Vuelve a iniciar sesión.'))
    else:
        postea = False
        if request.method == 'POST':
            postea = True
            nombre = request.form["nombre"]
            opcion = request.form["opcion"]

            elementos_dinamicos = []

            # Obtén los datos de los elementos dinámicos
            elementos_dinamicos.append({
                        'nombreproducto': request.form["nombreproducto"],
                        'cantidad': int(request.form["cantidad"]),
                        'precio': float(request.form["precio"]),
                        'categoria': request.form["categoria"],
                     })

            response = anadir_transaccion(id, idproyecto, nombre, opcion, elementos_dinamicos)
            
            if response.get('correcto'):
                d = response.get('datos')
                datos['error'] = response.get('error')
                datos['transactionId'] = d['transactionId']
                datos['idproyecto'] = idproyecto
                datos['datos']={'mensaje':'Se ha añadido correctamente la transacción.'}
                return redirect(url_for('transaction_menu', datos=datos))
            else:
                datos['error'] = response.get('error')
                datos['datos'] = 'todo mal'
        if not postea: datos['datos'] = 'No ha hecho post'

        response = get_presupuesto(idproyecto)
        d = response.get('datos')
        datos['presupuesto'] = d['presupuesto']
        
        return render_template('transaction_menu.html', datos=datos)

    
def anadir_transaccion(userid, idproyecto, nombre, opcion, productos):
    db_url = "http://flask-api:5001/transaction_menu"  
    payload = {'userid': userid, 'idproyecto': idproyecto, 'nombre': nombre, 'opcion': opcion, 'productos': productos}
    response = requests.post(db_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return None
# @app.route('/transaction_menu', methods=['POST', 'GET'])
# def transaction_menu():
#     id=session['ID_USER']
#     idproyecto=session['project']
#     datos = {
#                 'user': session['username'],
#                 'error': '',
#                 'transactionId': '', 
#                 'idproyecto': idproyecto,
#                 'presupuesto': None,
#                 'datos': None
#             }      
#     if id is None:
#         return redirect(url_for('register', error='Vuelve a iniciar sesión.'))
#     else:
#         postea = False
#         if request.method == 'POST':
#             postea = True
#             nombre = request.form["nombre"]
#             opcion = request.form["opcion"]

#             elementos_dinamicos = []

#             # Obtén los datos de los elementos dinámicos
#             for key, value in request.form.items():
#                 if key.startswith('nombreproducto_'):
#                     elemento_id = key.split('_')[-1]
#                     elemento = {
#                         'nombreproducto': value,
#                         'cantidad': request.form.get('cantidad_' + elemento_id),
#                         'precio': request.form.get('precio_' + elemento_id),
#                         'categoria': request.form.get('categoria_' + elemento_id),
#                     }
#                     elementos_dinamicos.append(elemento)

#             response = anadir_transaccion(id, idproyecto, nombre, opcion, elementos_dinamicos)
            
#             if response.get('correcto'):
#                 d = response.get('datos')
#                 datos['error'] = response.get('error')
#                 datos['transactionId'] = d['transactionId']
#                 datos['idproyecto'] = idproyecto
#                 datos['datos']={'mensaje':'Se ha añadido correctamente la transacción.'}
#                 return redirect(url_for('transaction_menu', datos=datos))
#             else:
#                 datos['error'] = response.get('error')
#                 datos['datos'] = 'todo mal'
#         if not postea: datos['datos'] = 'No ha hecho post'

#         response = get_presupuesto(idproyecto)
#         d = response.get('datos')
#         datos['presupuesto'] = d['presupuesto']
        
#         return render_template('transaction_menu.html', datos=datos)

    
# def anadir_transaccion(userid, idproyecto, nombre, opcion, productos):
#     db_url = "http://flask-api:5001/transaction_menu"  
#     payload = {'userid': userid, 'idproyecto': idproyecto, 'nombre': nombre, 'opcion': opcion, 'productos': productos}
#     response = requests.post(db_url, json=payload)
#     if response.status_code == 200:
#         data = response.json()
#         return data
#     else:
#         print(f"Error en la solicitud. Código de estado: {response.status_code}")
#         return None



# #####################
# ###  ADD PRODUCT  ###
# #####################

# @app.route('/add_product', methods=['POST', 'GET'])
# def add_product():
#     id=session['ID_USER']
#     idproyecto=session['project']
#     datos = {
#                 'user': session['username'],
#                 'error': '',
#                 'transactionId': '', 
#                 'idproyecto': '',
#                 'datos': None
#             }      

#     if id is None:
#         return redirect(url_for('/', error='Vuelve a iniciar sesión.'))
#     else:
#         if request.method == 'POST':
#             nombre = request.form["nombre"]
#             opcion = True
#             if request.form["opcion"] == 'FALSE':
#                 opcion = False
#             response = anadir_producto_a_transaccion(id, idproyecto, nombre, opcion)
            
#             if response.get('correcto'):
#                 d = response.get('datos')
#                 datos['error'] = response.get('error')
#                 datos['transactionId'] = d['transactionId']
#                 datos['idproyecto'] = idproyecto
#                 return redirect(url_for('add_product', datos=datos))
#             else:
#                 datos['error'] = response.get('error')
        
#     return render_template('transaction_menu.html', datos=datos)

    
# def anadir_producto_a_transaccion(userid, idproyecto, nombre, opcion):
#     db_url = "http://flask-api:5001/create_project"  
#     payload = {'userid': userid, 'idproyecto': idproyecto, 'nombre': nombre, 'opcion': opcion}
#     response = requests.post(db_url, json=payload)
#     if response.status_code == 200:
#         data = response.json()
#         return data
#     else:
#         print(f"Error en la solicitud. Código de estado: {response.status_code}")
#         return None


#####################
###  DASHBOARDS  ###
#####################


@app.route('/dashboards', methods=['POST', 'GET'])
def dashboards():
    id=session['ID_USER']
    idproyecto=session['project']

    if id is None:
        return redirect(url_for('register', error='Vuelve a iniciar sesión.'))
    else:
        response = dashboards_por_categoria(idproyecto) 
        d= response.get('datos')
        response2 = get_presupuesto(idproyecto) 
        d2 = response2.get('datos')
        datos = {
                'user': session['username'],
                'error': '',
                'idproyecto': idproyecto,
                'presupuesto': d2['presupuesto'],
                'datos': {
                    'restante': int(d2['presupuesto']/d['presupuestoInicial'])*100,
                    'categorias': d['categorias']
                }
            }      
        return render_template('dashboards.html', datos=datos)

    
def dashboards_por_categoria(idproyecto):
    db_url = "http://flask-api:5001/dashboards"  
    payload = {'idproyecto': idproyecto}
    response = requests.get(db_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return {
        'correcto': False,
        'error': '',
        'datos': response.status_code
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
