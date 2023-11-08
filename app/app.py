from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'mysql'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'database'

mysql = MySQL(app)

@app.route('/', methods=['POST', 'GET'])
def login():
    valor_error = ''
    if request.method == 'POST':
        email = request.form["email2"]
        contra = request.form["contrasena2"]
        
        # Establecer la conexión a la base de datos MySQL (asegúrate de que MySQL esté configurado)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute(f'SELECT * FROM usuarios WHERE email = {email} AND contrasena = {contra}')
        
        user = cursor.fetchone()
        
        cursor.close()
        
        if user:
            session['username'] = user['nombre']
            session['email'] = email
            session['ID_USER'] = user['id']
            return redirect(url_for('user_menu'))
        else:
            valor_error = 'No existe el usuario.'
            return redirect(url_for('login', error=valor_error))

    return render_template('index.html', error=valor_error)

@app.route('/', methods=['POST', 'GET'])
def register():
    valor_error = ''
    if request.method == 'POST':
        nombre = request.form["nombre"]
        email = request.form["email"]
        contra = request.form["contrasena"]

        concatenated_data = nombre + email

        # Calcula el hash SHA-256 de la concatenación
        sha256 = hashlib.sha256()
        sha256.update(concatenated_data.encode('utf-8'))
        id = sha256.hexdigest()

        sha256.update(contra.encode('utf-8'))
        contraseña_hash = sha256.hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'INSERT INTO usuarios (id, nombre, email, contrasena) VALUES ({id}, {nombre}, {email}, {contraseña_hash})')
        user = cursor.fetchone()
        cursor.close()

        if user:
            valor_error = 'Ya existe un usuario con ese email y nombre.'
            return redirect(url_for('login', error=valor_error))
        else:
            session['username'] = user['nombre']
            session['email'] = email
            session['ID_USER'] = user['id']
            return redirect(url_for('user_menu'))
        
    return render_template('index.html', error=valor_error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
