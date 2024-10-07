from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)


# Configurações de acesso ao MySQL
app.config['MYSQL_HOST'] = 'localhost'          # Servidor do MySQL
app.config['MYSQL_USER'] = 'root'               # Usuário do MySQL
app.config['MYSQL_PASSWORD'] = ''               # Senha do MySQL
app.config['MYSQL_DB'] = 'pytasksdb'            # Nome da base de dados
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # REtorna dados como DICT

# Variável de conexão com o MySQL
mysql = MySQL(app)


# Configura a conexão com o MySQL para usar utf8mb4 e português do Brasil
@app.before_request
def before_request():
    cur = mysql.connection.cursor()
    cur.execute("SET NAMES utf8mb4")
    cur.execute("SET character_set_connection=utf8mb4")
    cur.execute("SET character_set_client=utf8mb4")
    cur.execute("SET character_set_results=utf8mb4")
    cur.execute("SET lc_time_names = 'pt_BR'")
    cur.close()


@app.route('/')
def home():

    page = {
        'href': '/new',
        'label': 'Nova tarefa'
    }

    return render_template('home.html', page=page)


@app.route('/new', methods=['GET', 'POST'])
def new():

    created = False

    if request.method == 'POST':
        form = dict(request.form)
        # print('\n\n\n', form, '\n\n\n')

        if form['expire'] == '':
            subquery = 'DATE_ADD(NOW(), INTERVAL 30 DAY)'
        else:
            subquery = form['expire'].replace('T', ' ')

        sql = '''
            INSERT INTO task (name, description, expire)
            VALUES (%s, %s, %s);
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['name'], form['description'], subquery,))
        mysql.connection.commit()
        cur.close()

        created = True

    page = {
        'href': '/',
        'label': 'Ver tarefas',
        'created': created
    }

    return render_template('new.html', page=page)


@app.errorhandler(404)
def error(e):
    return f'Erro 404 {e}', 404


if __name__ == '__main__':
    app.run(debug=True)
