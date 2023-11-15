from flask import Flask, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'database'
app.secret_key = '987654321'

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

    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
    finally:
        cursor.close()

    return resultado

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
            resultado['error'] = 'No existe el usuario.'
            
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
        return resultado
    except Exception as e:
    # Manejo de excepciones
        print(f"Error al acceder al proyecto: {e}")
        resultado['error'] = str(e)
        return resultado
    finally:
        cursor.close()

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

        cursor.execute("SELECT SUM(valor) AS total FROM transaccion JOIN producto ON transaccion.id = producto.IdTransaccion WHERE categoria = 'Otros' and transaccion.IdProyecto = %s", (idproyecto,))
        otros = cursor.fetchone()['total']
        if otros is None:
            otros = 0.0
        cursor.execute("SELECT SUM(valor) AS total FROM transaccion JOIN producto ON transaccion.id = producto.IdTransaccion WHERE categoria = 'Comida' and transaccion.IdProyecto = %s", (idproyecto,))
        comida = cursor.fetchone()['total']
        if comida is None:
            comida = 0.0
        cursor.execute("SELECT SUM(valor) AS total FROM transaccion JOIN producto ON transaccion.id = producto.IdTransaccion WHERE categoria = 'Vivienda' and transaccion.IdProyecto = %s", (idproyecto,))
        vivienda = cursor.fetchone()['total']
        if vivienda is None:
            vivienda = 0.0
        cursor.execute("SELECT SUM(valor) AS total FROM transaccion JOIN producto ON transaccion.id = producto.IdTransaccion WHERE categoria = 'Ropa' and transaccion.IdProyecto = %s", (idproyecto,))
        ropa = cursor.fetchone()['total']
        if ropa is None:
            ropa = 0.0
        cursor.execute("SELECT SUM(valor) AS total FROM transaccion JOIN producto ON transaccion.id = producto.IdTransaccion WHERE categoria = 'Actividades' and transaccion.IdProyecto = %s", (idproyecto,))
        actividades = cursor.fetchone()['total']
        if actividades is None:
            actividades = 0.0
        cursor.execute("SELECT SUM(valor) AS total FROM transaccion JOIN producto ON transaccion.id = producto.IdTransaccion WHERE categoria = 'Material' and transaccion.IdProyecto = %s", (idproyecto,))
        material = cursor.fetchone()['total']
        if material is None:
            material = 0.0


        resultado['correcto'] = True
        resultado['datos'] = {
            'presupuestoInicial': presupuestoInicial,
            'utilizado': presupuestoInicial-presupuesto,
            'restante': presupuesto,
            'categorias':{
                'Otros': int(otros/presupuestoInicial)*100,
                'Comida': int(comida/presupuestoInicial)*100,
                'Vivienda': int(vivienda/presupuestoInicial)*100,
                'Ropa': int(ropa/presupuestoInicial)*100,
                'Actividades': int(actividades/presupuestoInicial)*100,
                'Material': int(material/presupuestoInicial)*100
            }
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

        cursor.execute('SELECT gasto, valor, IdProyecto FROM transaccion WHERE IdTransaccion = %s', (idTransaccion,))
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
    app.run(host='0.0.0.0', port=5001, debug=True)