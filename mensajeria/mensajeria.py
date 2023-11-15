from flask import Flask
import requests

app = Flask(__name__)


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