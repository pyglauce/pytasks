from flask import Flask, json, redirect, render_template, request, url_for
from flask_mysqldb import MySQL
from datetime import datetime, timedelta

app = Flask(__name__)


# Configurações de acesso ao MySQL
app.config['MYSQL_HOST'] = 'localhost'          # Servidor do MySQL
app.config['MYSQL_USER'] = 'root'               # Usuário do MySQL
app.config['MYSQL_PASSWORD'] = ''               # Senha do MySQL
app.config['MYSQL_DB'] = 'pytasksdb'            # Nome da base de dados
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Retorna dados como DICT
# Usa a conversão unicode para caracteres
app.config['MYSQL_USE_UNICODE'] = True
app.config['MYSQL_CHARSET'] = 'utf8mb4'         # Transações em UTF-8

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

    action = request.args.get('ac')

    sql = '''
        SELECT * FROM `task`
        WHERE status != 'deleted'
        ORDER BY status, expire;
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql)
    tasks = cur.fetchall()
    cur.close()

    print('\n\n\n', json.dumps(tasks, indent=4, ensure_ascii=False), '\n\n\n')

    page = {
        'href': '/new',
        'label': 'Nova tarefa',
        'tasks': tasks,
        'action': action
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

    data_atual = datetime.now()  # Obter a data e hora atual
    data_futura = data_atual + timedelta(days=30)  # Adicionar 30 dias
    # Formatar a data no formato desejado
    data_formatada = data_futura.strftime('%Y-%m-%d %H:%M:%S')

    page = {
        'href': '/',
        'label': 'Ver tarefas',
        'created': created,
        'date30': data_formatada
    }

    return render_template('new.html', page=page)


@app.route('/del/<id>')
def delete(id):

    sql = '''
        UPDATE task 
        SET status = 'deleted'
        WHERE id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('home', ac='del'))


@app.route('/check/<id>')
def check(id):

    sql = '''
        UPDATE task 
        SET status = 'completed'
        WHERE id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('home', ac='com'))


@app.route('/uncheck/<id>')
def uncheck(id):

    sql = '''
        UPDATE task 
        SET status = 'pending'
        WHERE id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('home', ac='pen'))


@app.errorhandler(404)
def error(e):
    return f'Erro 404 {e}', 404


if __name__ == '__main__':
    app.run(debug=True)
