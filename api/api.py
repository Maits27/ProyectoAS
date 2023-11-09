from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'database'

mysql = MySQL(app)

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
        concatenated_data = nombre + email

        # Calcula el hash SHA-256 de la concatenación
        sha256 = hashlib.sha256()
        sha256.update(concatenated_data.encode('utf-8'))
        id = sha256.hexdigest()

        sha256.update(contra.encode('utf-8'))
        contraseña_hash = sha256.hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM usuarios WHERE id = %s', (id,))
        user=cursor.fetchone()

        if user:
            resultado['error'] = 'Ya existe el usuario. Prueba con otro email.'
            return jsonify(resultado)
        else:
            cursor.execute('INSERT INTO usuarios (id, nombre, email, contrasena) VALUES (%s, %s, %s, %s)', (id, nombre, email, contraseña_hash,))
            mysql.connection.commit()
            resultado['correcto'] = True
            resultado['datos'] = {'id': id}

    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
    finally:
        cursor.close()

    print(f"Respuesta: {type(resultado)}")
    return jsonify(resultado)

    
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
        sha256 = hashlib.sha256()
        sha256.update(contra.encode('utf-8'))
        contraseña_hash = sha256.hexdigest()

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

    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el login de usuario: {e}")
        resultado['error'] = str(e)
    finally:
        cursor.close()

    print(f"Respuesta: {resultado}")
    return jsonify(resultado)
    

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
        proyecto = cursor.fetchone()
        cursor.close()

        if proyecto:
            resultado['correcto'] = True
            resultado['datos'] = proyecto
        
        return jsonify(resultado)
    except Exception as e:
    # Manejo de excepciones
        print(f"Error en el registro de usuario: {e}")
        resultado['error'] = str(e)
        return jsonify(resultado)
    finally:
        cursor.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)