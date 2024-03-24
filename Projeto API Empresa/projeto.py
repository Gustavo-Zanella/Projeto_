from flask import Flask, render_template, request, redirect, session, make_response, jsonify
import requests
import re
import pandas as pd
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, Session

from empresas import Empresa


app = Flask(__name__)
app.secret_key = 'SK'

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

banco = Banco_Empresa('postgres', 'postgres', '127.0.0.1', '5432', 'zanella').get_engine()

Session = sessionmaker(bind=banco) 

def cnpj_existe(cnpj):
    sql_verifica_cnpj = f"SELECT * FROM PUBLIC.TBEMPRESA WHERE EMPCNPJ = '{cnpj}'"
    df = pd.read_sql_query(sql_verifica_cnpj, banco)
    return not df.empty

@app.route('/cadastrar_empresa')
def cadastrar_empresa():
    df = pd.read_sql("SELECT * FROM PUBLIC.TBEMPRESA", banco)
    empresas = df.to_dict(orient='records')
    return render_template('cadastraempresa.html', empresas=empresas)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/api/dados', methods=['GET'])
def get_dados():
    empresas = "SELECT * FROM PUBLIC.TBEMPRESA"
    df = pd.read_sql(empresas, banco)

    print(df.to_dict)

    return make_response(jsonify(df.to_json(orient='records', lines=True)))

@app.route('/autenticar', methods=['POST'])
def autenticar_usuario():
    if '123' == request.form['password']:
        return redirect('/cadastrar_empresa')
    else:
        return redirect('/')    
    
def verificar_url(url):
    try:
        req = requests.get(url)
        req = req.json()
        return req['status'] != 'ERROR'
    except:
        return False

@app.route('/verificar', methods=['POST'])
def verificar_empresa_existe():
    cnpj = re.sub(r'\D', '', request.form['campo'])
    session['cnpj'] = cnpj
    url = f'https://receitaws.com.br/v1/cnpj/{cnpj}'
    session['url_api'] = url

    try:
        if 'cadastrar' in request.form:
            if verificar_url(url) and not cnpj_existe(cnpj):
                inserir_empresa()
                return redirect('/cadastrar_empresa')  
            else:
                return redirect('/cadastrar_empresa')
        elif 'visualizar' in request.form:
            if cnpj_existe(cnpj):
                return redirect('/visualizar')
            else:
                return redirect('/cadastrar_empresa')
        else:
           return redirect('/alterar') 
    except:
        return redirect('/cadastrar_empresa')

@app.route('/voltar_alterar', methods=['POST'])
def voltar_alterar():
    if 'Alterar' in request.form:
        cnpj = session.get('cnpj', None)
        vendedor = request.form['vendedor_responsavel']
        faturamento = request.form['faturamento_anual']
        funcionarios = request.form['numero_funcionarios']    
        if alterar_empresa(cnpj, vendedor, faturamento, funcionarios):
            return redirect('/cadastrar_empresa')
        else:
            return "Erro ao alterar a empresa"
    else:
        return redirect('/cadastrar_empresa')

def alterar_empresa(cnpj, vendedor, faturamento, funcionarios):
    try:    
        session = Session()
        session.query(Empresa).\
            filter(Empresa.empcnpj == cnpj).\
            update({Empresa.empnumerofuncionarios: funcionarios,
                    Empresa.empfatanualestimado: faturamento,
                    Empresa.empvendedor: vendedor,})
        session.commit()
        return True
    except:
        session.rollback()
        return False
    finally:
        session.close()

@app.route('/visualizar')
def visualizar_empresa():
    df = pd.read_sql(f"SELECT * FROM PUBLIC.TBEMPRESA WHERE EMPCNPJ = '{session.get('cnpj', None)}'", banco)
    empresas_ = df.to_dict(orient='records')
    return render_template('visualizar.html', empresas=empresas_)    

@app.route('/alterar')
def alterar_empresa_page():
    df = pd.read_sql(f"SELECT * FROM PUBLIC.TBEMPRESA WHERE EMPCNPJ = '{session.get('cnpj', None)}'", banco)
    empresas_ = df.to_dict(orient='records')
    return render_template('alterar.html', empresas=empresas_) 

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
        'empnumerofuncionarios' : '0',
        'empfatanualestimado' : '0'
    }

    df_empresa = pd.DataFrame([dados_empresa])

    table_name_empresa = 'tbempresa'
    df_empresa.to_sql(table_name_empresa, banco, if_exists='append', index=False)

app.run()

