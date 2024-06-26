import math
from flask import Flask, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib

import requests
from config import SERVICE_MYSQL, USER_PASSWORD, MYSQL_DATABASE, MYSQL_USER, APP_SECRET_KEY


app = Flask(__name__)
app.config['MYSQL_HOST'] = SERVICE_MYSQL
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = USER_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DATABASE
app.secret_key = APP_SECRET_KEY

mysql = MySQL(app)


#####################
###   REGISTER    ###
#####################

@app.route('/register', methods=['POST'])
def register():
    # ... (mover la lógica de registro de usuario aquí)
    data = request.json
    nombre = data.get('nombre')
    email = data.get('email')
    contra = data.get('contra')

    resultado = {
        'correcto': False,
        'error': '',
        'datos': None
    }

    try:
        hash = nombre + email + app.secret_key
        # Calcula el hash SHA-256 de la concatenación
        hash = hashlib.sha256(hash.encode())
        id = hash.hexdigest()

        hash = contra + app.secret_key
        hash = hashlib.sha256(hash.encode())
        contrasena_hash = hash.hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (id,))
        user=cursor.fetchone()

        if user:
            resultado['error'] = 'Ya existe el usuario. Prueba con otro email.'
        else:
            cursor.execute('INSERT INTO usuarios (id, nombre, email, contrasena) VALUES (%s, %s, %s, %s)', (id, nombre, email, contrasena_hash,))
            mysql.connection.commit()
            resultado['correcto'] = True
            resultado['datos'] = {'id': id}

            response = send_register_email(nombre, email)
            if not response.get('correcto'):
                resultado['correcto'] = False
                resultado['error'] = response.get('mensaje')

    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
    finally:
        cursor.close()

    return resultado

def send_register_email(nombre, email):
    db_url = "http://mensajeria:5002/register"  # Utiliza el nombre del servicio de la base de datos
    payload = {'username': nombre, 'email': email}
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
    
@app.route('/', methods=['POST'])
def login():
    # Establecer la conexión a la base de datos MySQL (asegúrate de que MySQL esté configurado)
    data = request.json
    email = data.get('email')
    contra = data.get('contra')

    resultado = {
        'correcto': False,
        'error': '',
        'datos': None
    }

    try:
        
        hash = contra + app.secret_key
        hash = hashlib.sha256(hash.encode())
        contraseña_hash = hash.hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE email = %s AND contrasena = %s', (email, contraseña_hash,))
        user = cursor.fetchone()  

        if user:
            resultado['correcto'] = True
            resultado['datos'] = {
                'id': user['id'],
                'nombre': user['nombre']
            }
        else:
            resultado['error'] = 'No existe el usuario'
            
        return resultado

    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el login de usuario: {e}")
        resultado['error'] = str(e)
        return resultado
    finally:
        cursor.close()




#####################
###   USER_MENU   ###
#####################   
    

@app.route('/user_menu', methods=['POST'])
def get_user_menu_data():
    # Establecer la conexión a la base de datos MySQL (asegúrate de que MySQL esté configurado)
    data = request.json
    id = data.get('id')

    resultado = {
        'correcto': False,
        'error': '',
        'datos': []
    }
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT proyecto.* FROM proyecto JOIN proyectosUsuario ON proyecto.id = proyectosUsuario.IdProyecto WHERE proyectosUsuario.IdUsuario = %s', (id,))
        proyectos = cursor.fetchall()

        if proyectos:
            data=[]
            for proyecto in proyectos:
                data.append({'idproyecto':proyecto['id'], 'nombre': proyecto['nombre']})
            resultado['correcto'] = True
            resultado['datos'] = data
        
    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
    finally:
        cursor.close()
    
    return resultado

#####################
###     CREATE    ###
#####################


@app.route('/create_project', methods=['POST'])
def create_project():
    data = request.json
    nombre = data.get('nombre')
    userid = data.get('userid')
    contra = data.get('contra')
    presupuesto = data.get('presupuesto')

    resultado = {
        'correcto': False,
        'error': 'ERROR',
        'datos': None
    }

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) as count FROM proyecto')
        num=cursor.fetchone()
        idproyecto = '#' + nombre + str(num['count'])

        # Calcula el hash SHA-256 de la concatenación
        hash = contra + app.secret_key
        hash = hashlib.sha256(hash.encode())
        contrasena_hash = hash.hexdigest()

        cursor.execute('SELECT * FROM proyecto WHERE id = %s', (idproyecto,))
        proyecto=cursor.fetchone()

        if proyecto:
            resultado['error'] = 'Ya existe el proyecto. Prueba con otro nombre.'
        else:
            # Conseguimos el email del main user:
            cursor.execute('SELECT email FROM usuarios WHERE id = %s', (userid,))
            email=cursor.fetchone() 

            if email:
                cursor.execute('INSERT INTO proyecto (id, nombre, contrasena, presupuesto, presupuestoInicial, main) VALUES (%s, %s, %s, %s, %s, %s)', (idproyecto, nombre, contrasena_hash, presupuesto, presupuesto, email['email'],))
                mysql.connection.commit()

                hash = userid + idproyecto
                hash = hashlib.sha256(hash.encode())
                id_p_u = hash.hexdigest()

                cursor.execute('INSERT INTO proyectosUsuario (id, IdUsuario, IdProyecto) VALUES (%s, %s, %s)', (id_p_u, userid, idproyecto,))
                mysql.connection.commit()

                resultado['correcto'] = True
                resultado['error'] = 'NO HAY ERROR'
                resultado['datos'] = {'idproyecto': idproyecto}
            else:
                resultado['error'] = 'Problemas con el email.'
        return resultado
    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de proyecto: {e}")
        resultado['error'] = str(e)
        mysql.connection.rollback()
        return resultado
    finally:
        cursor.close()

    
#####################
###     JOIN      ###
#####################


@app.route('/join_project', methods=['POST'])
def join_project():
    data = request.json
    idproyecto = data.get('idproyecto')
    userid = data.get('userid')
    contra = data.get('contra')
    sessionUsername = data.get('sessionUsername')

    resultado = {
        'correcto': False,
        'error': '',
        'datos': None
    }

    try:
        # Calcula el hash SHA-256 de la concatenación
        hash = contra + app.secret_key
        hash = hashlib.sha256(hash.encode())
        contrasena_hash = hash.hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM proyecto WHERE id = %s and contrasena = %s', (idproyecto, contrasena_hash,))
        proyecto=cursor.fetchone()

        if not proyecto:
            resultado['error'] = 'El ID o la contraseña del proyecto no son correctos.'
        else:
            hash = userid + idproyecto
            hash = hashlib.sha256(hash.encode())
            id_p_u = hash.hexdigest()

            cursor.execute('INSERT INTO proyectosUsuario (id, IdUsuario, IdProyecto) VALUES (%s, %s, %s)', (id_p_u, userid, idproyecto,))
            mysql.connection.commit()

            resultado['correcto'] = True
            resultado['error'] = 'NO HAY ERROR'
            resultado['datos'] = {'idproyecto': idproyecto, 'nombreProyecto':proyecto['nombre'], 'email': proyecto['main']}
            
            response = send_join_email(proyecto['main'], sessionUsername, idproyecto)
            if not response.get('correcto'):
                resultado['correcto'] = False
                resultado['error'] = response.get('mensaje')

        
        return resultado
    except Exception as e:
    # Manejo de excepciones
        print(f"Error al acceder al proyecto: {e}")
        resultado['error'] = str(e)
        return resultado
    finally:
        cursor.close()


def send_join_email(email, newuser, proyecto):
    db_url = "http://mensajeria:5002/join"  # Utiliza el nombre del servicio de la base de datos
    payload = {'email': email, 'newuser': newuser, 'proyecto': proyecto}
    response = requests.post(db_url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return None
#####################
### PROJECT MENU  ###
#####################

@app.route('/project_menu', methods=['POST', 'GET'])
def project_menu():
    # ... (mover la lógica de registro de usuario aquí)
    data = request.json
    idproyecto = data.get('idproyecto')

    resultado = {
        'correcto': False,
        'error': '',
        'datos': None
    }

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT presupuesto FROM proyecto WHERE id = %s', (idproyecto,))
        presupuesto=cursor.fetchone()['presupuesto']
        if presupuesto:
            resultado['correcto'] = True
            resultado['datos'] = {'presupuesto': presupuesto}
        else:
            resultado['error'] = 'No hay ese proyecto'
            resultado['datos'] = {'presupuesto': 0}
        return resultado
    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
        resultado['datos'] = {'presupuesto': 0}
        return resultado
    finally:
        cursor.close()

#####################
###  TRANSACTION  ###
#####################

@app.route('/transaction_menu', methods=['POST'])
def transaction_menu():
    # ... (mover la lógica de registro de usuario aquí)
    data = request.json
    userid = data.get('userid')
    idproyecto = data.get('idproyecto')
    nombre = data.get('nombre')
    opcion = data.get('opcion')
    productos = data.get('productos')

    resultado = {
        'correcto': False,
        'error': '',
        'datos': None
    }

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO transaccion (nombre, gasto, IdUsuario, IdProyecto) VALUES (%s, %s, %s, %s)', (nombre, opcion, userid, idproyecto,))
        transactionId = cursor.lastrowid
        mysql.connection.commit()

        precioTotal = 0
        for producto in productos:
            precioTotal += producto['cantidad'] * producto['precio']
            cursor.execute('INSERT INTO producto (nombre, categoria, cantidad, precioUnidad, IdTransaccion) VALUES (%s, %s, %s, %s, %s)', (producto['nombreproducto'], producto['categoria'], producto['cantidad'], producto['precio'],transactionId,))
            mysql.connection.commit()
        
        cursor.execute('UPDATE transaccion SET valor = %s WHERE id = %s', (precioTotal, transactionId))
        mysql.connection.commit()

        cursor.execute('SELECT presupuesto, presupuestoInicial FROM proyecto WHERE id = %s', (idproyecto,))
        info = cursor.fetchone()
        presupuesto = info['presupuesto']
        presupuestoInicial = info['presupuestoInicial']

        # Actualizar el presupuesto del proyecto
        if opcion == '1':
            presupuesto -= precioTotal
            cursor.execute('UPDATE proyecto SET presupuesto = %s WHERE id = %s', (presupuesto, idproyecto))
            mysql.connection.commit()
        else:
            presupuesto += precioTotal
            presupuestoInicial += precioTotal
            cursor.execute('UPDATE proyecto SET presupuesto = %s WHERE id = %s', (presupuesto, idproyecto))
            mysql.connection.commit()
            cursor.execute('UPDATE proyecto SET presupuestoInicial = %s WHERE id = %s', (presupuestoInicial, idproyecto))
            mysql.connection.commit()
            

        resultado['correcto'] = True
        resultado['datos'] = {'transactionId': transactionId}
        return resultado
    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
        return resultado
    finally:
        cursor.close()


#####################
###  DASHBOARDS   ###
#####################

@app.route('/dashboards', methods=['POST', 'GET'])
def dashboards():
    data = request.json
    idproyecto = data.get('idproyecto')

    resultado = {
        'correcto': False,
        'error': '',
        'datos': None
    }

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT presupuestoInicial FROM proyecto WHERE id = %s', (idproyecto,))
        presupuestoInicial = cursor.fetchone()['presupuestoInicial']
        
        cursor.execute('SELECT presupuesto FROM proyecto WHERE id = %s', (idproyecto,))
        presupuesto = cursor.fetchone()['presupuesto']

        categorias = ['Otros', 'Comida', 'Vivienda', 'Ropa', 'Actividades', 'Material']
        porcentajes = {}

        for categoria in categorias:
            total_categoria = 0.0
            cursor.execute("SELECT SUM(cantidad * precioUnidad) AS total FROM transaccion JOIN producto ON transaccion.id = producto.IdTransaccion WHERE producto.categoria = %s and transaccion.IdProyecto = %s and transaccion.gasto = 1", (categoria, idproyecto,))
            total_categoria = cursor.fetchone()['total']
            if total_categoria is None:
                total_categoria = 0.0

            porcentaje_categoria = math.ceil((total_categoria / presupuestoInicial) * 100)
            porcentajes[categoria] = porcentaje_categoria

        resultado['correcto'] = True
        resultado['datos'] = {
            'presupuestoInicial': presupuestoInicial,
            'utilizado': presupuestoInicial - presupuesto,
            'restante': presupuesto,
            'categorias': porcentajes,
            'porcentaje_total': math.ceil((presupuestoInicial - presupuesto) / presupuestoInicial * 100)
        }
        return resultado
    except Exception as e:
        # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
        return resultado
    finally:
        cursor.close()



########################
### LIST_TRANSACTION ###
########################
@app.route('/list_transaction', methods=['POST', 'GET'])
def list_transaction():
    data = request.json
    idproyecto = data.get('idproyecto')

    resultado = {
        'correcto': False,
        'error': '',
        'datos': []
    }

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM transaccion WHERE IdProyecto = %s', (idproyecto,))
        transacciones = cursor.fetchall()
        
        if transacciones:
            resultado['correcto'] = True
            for transaccion in transacciones:
                simbolo='+'
                if transaccion['gasto']==1: simbolo='-'
                resultado['datos'].append({
                    'id': transaccion['id'],
                    'nombre':transaccion['nombre'],
                    'valor': simbolo + ' ' + str(transaccion['valor'])
                }) 
        return resultado
    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
        return resultado
    finally:
        cursor.close()


@app.route('/delete_transaction', methods=['POST', 'GET'])
def delete_transaction():
    data = request.json
    idTransaccion = data.get('idTransaccion')

    resultado = {
        'correcto': False,
        'error': '',
        'datos': None
    }

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT gasto, valor, IdProyecto FROM transaccion WHERE id = %s', (idTransaccion,))
        transaccion = cursor.fetchone()

        if transaccion:

            cursor.execute('SELECT presupuesto, presupuestoInicial FROM proyecto WHERE id = %s', (transaccion['IdProyecto'],))
            presupuesto = cursor.fetchone()

            if transaccion['gasto'] == 1:
                nuevoPresupuesto = presupuesto['presupuesto']+transaccion['valor']
                cursor.execute('UPDATE proyecto SET presupuesto = %s WHERE id = %s', (nuevoPresupuesto, transaccion['IdProyecto']))
                mysql.connection.commit()
            else:
                nuevoPresupuesto = presupuesto['presupuesto']-transaccion['valor']
                cursor.execute('UPDATE proyecto SET presupuesto = %s WHERE id = %s', (nuevoPresupuesto, transaccion['IdProyecto']))
                mysql.connection.commit()

                nuevoPresupuesto = presupuesto['presupuestoInicial']-transaccion['valor']
                cursor.execute('UPDATE proyecto SET presupuestoInicial = %s WHERE id = %s', (nuevoPresupuesto, transaccion['IdProyecto']))
                mysql.connection.commit()

            cursor.execute('DELETE FROM producto WHERE IdTransaccion = %s', (idTransaccion,))
            mysql.connection.commit()

            cursor.execute('DELETE FROM transaccion WHERE id = %s', (idTransaccion,))
            mysql.connection.commit()

            resultado['correcto'] = True
        
        return resultado
    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
        return resultado
    finally:
        cursor.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)