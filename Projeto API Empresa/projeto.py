from flask import Flask, render_template, request, redirect, session
import requests
import re
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = 'vasco'
# Classe para conexão com banco da empresa
class Banco_Empresa:
    def __init__(self, username, password, host, port, name):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.name = name

    def get_engine(self):
        connection = f'postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}'
        return create_engine(connection)

# Instanciação do banco de dados
banco = Banco_Empresa('postgres', 'postgres', '192.168.15.83', '5432', 'zanella').get_engine()

# Função para verificar se o CNPJ já está cadastrado no banco de dados
def cnpj_existe(cnpj):
    sql_verifica_cnpj = f"SELECT * FROM PUBLIC.TBEMPRESA WHERE EMPCNPJ = '{cnpj}'"
    df = pd.read_sql_query(sql_verifica_cnpj, banco)
    return not df.empty

# Rota para cadastrar empresa
@app.route('/cadastrar_empresa')
def cadastrar_empresa():
    return render_template('cadastraempresa.html')

# Rota para login
@app.route('/')
def login():
    return render_template('login.html')

# Rota para autenticar usuário
@app.route('/autenticar', methods=['POST'])
def autenticar_usuario():
    if '123' == request.form['password']:
        return redirect('/cadastrar_empresa')
    else:
        return redirect('/')    

# Função para verificar se a URL é válida
def verificar_url(url):
    try:
        req = requests.get(url)
        req = req.json()
        return req['status'] != 'ERROR'
    except:
        return False

# Rota para verificar se a empresa existe e decidir onde redirecionar
@app.route('/verificar', methods=['POST'])
def verificar_empresa_existe():
    cnpj = re.sub(r'\D', '', request.form['campo'])
    
    if 'cadastrar' in request.form:
        url = f'https://receitaws.com.br/v1/cnpj/{cnpj}'
        session['url_api'] = url
        
        if verificar_url(url) and not cnpj_existe(cnpj):
            session['cnpj'] = cnpj
            return redirect('/crud')  
        else:
            return redirect('/cadastrar_empresa')

# Rota para CRUD de empresa
@app.route('/crud')
def crud_empresa():
    inserir_empresa()
    return render_template('crud.html')

def inserir_empresa():

    rf_url = session.get('url_api', None)
    cnpj = session.get('cnpj', None)
    data = requests.get(rf_url, timeout=5).json()
        
    dados_empresa = {
        'empdataabertura': data['abertura'],
        'empsituacao': data['situacao'],
        'emptipo': data['tipo'],
        'empnomerazao': data['nome'],
        'empporte': data['porte'],
        'empnaturezajuridica': data['natureza_juridica'],
        'emplogradouro': data['logradouro'],
        'empnumeroendereco': data['numero'],
        'empcomplementoendereco': data['complemento'],
        'empmunicipio': data['municipio'],
        'empbairro': data['bairro'],
        'empuf': data['uf'],
        'empcep': data['cep'],
        'empemail': data['email'],
        'emptelefone': data['telefone'],
        'empcnpj': cnpj,
        'empstatus': data['status'],
        'empnomefantasia': data['fantasia'],
        'empcapitalsocial': data['capital_social'],
        'empatividadepri': data['atividade_principal'][0]['text'],
        'empnumerofuncionarios' : '123',
        'empfatanualestimado' : '112312'
    }

    # Criar um DataFrame com os dados da empresa
    df_empresa = pd.DataFrame([dados_empresa])

    # Criar uma tabela para a empresa no banco de dados e inserir os dados
    table_name_empresa = 'tbempresa'
    df_empresa.to_sql(table_name_empresa, banco, if_exists='append', index=False)
app.run()
