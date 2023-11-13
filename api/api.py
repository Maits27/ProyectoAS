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
                cursor.execute('INSERT INTO proyecto (id, nombre, contrasena, presupuesto, main) VALUES (%s, %s, %s, %s, %s)', (idproyecto, nombre, contrasena_hash, presupuesto, email['email'],))
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
            hash = userid + id
            hash = hashlib.sha256(hash.encode())
            id_p_u = hash.hexdigest()

            cursor.execute('INSERT INTO proyectosUsuario (id, IdUsuario, IdProyecto) VALUES (%s, %s, %s)', (id_p_u, userid, idproyecto,))
            mysql.connection.commit()

            resultado['correcto'] = True
            resultado['error'] = 'NO HAY ERROR'
            resultado['datos'] = {'idproyecto': idproyecto}
       
        return resultado
    except Exception as e:
    # Manejo de excepciones
        print(f"Error al acceder al proyecto: {e}")
        resultado['error'] = str(e)
        mysql.connection.rollback()
        return resultado
    finally:
        cursor.close()



# #####################
# ###  PROJECT_MENU ###
# #####################  
    

# @app.route('/project_menu', methods=['GET'])
# def get_project_menu_data():
#     # Establecer la conexión a la base de datos MySQL (asegúrate de que MySQL esté configurado)
#     data = request.json
#     id = data.get('id')

#     resultado = {
#         'correcto': False,
#         'error': '',
#         'datos': []
#     }
#     try:
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT proyecto.* FROM proyecto JOIN proyectosUsuario ON proyecto.id = proyectosUsuario.IdProyecto WHERE proyectosUsuario.IdUsuario = %s', (id,))
#         proyectos = cursor.fetchall()

#         if proyectos:
#             data=[]
#             for proyecto in proyectos:
#                 data.append({'idproyecto':proyecto['id'], 'nombre': proyecto['nombre']})
#             resultado['correcto'] = True
#             resultado['datos'] = data
        
#     except Exception as e:
#     # Manejo de excepciones
#         print(f"Error en el registro de usuario: {e}")
#         resultado['error'] = str(e)
#     finally:
#         cursor.close()
    
#     return resultado

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)