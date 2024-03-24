from flask import Flask, render_template, request, redirect, session, make_response, jsonify
import requests
import re
import pandas as pd
from sqlalchemy import create_engine, update, Column, String, Integer
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import psycopg2 as pg

app = Flask(__name__)
app.secret_key = 'SK'

Base = declarative_base()

class Empresa(Base):
    __tablename__ = 'tbempresa'

    empcnpj = Column(String, primary_key=True)
    empnumerofuncionarios = Column(String)
    empfatanualestimado = Column(String)
    empvendedor = Column(String)


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
    return redirect('/cadastrar_empresa') 
    
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
            if cnpj_existe(cnpj):
                return redirect('/alterar')
            else:
                return redirect('/cadastrar_empresa')
    except:
        return "Erro ao Inserir Empresa"

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
                    Empresa.empvendedor: vendedor})
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

def connect_db():
    connection = pg.connect(dbname='zanella', user='postgres', host='127.0.0.1', password='postgres', port='5432')
    return connection

@app.route('/api/empresas', methods=['GET'])
def get_empresas():
    conn = connect_db()
    cursor = conn.cursor()

    query = "SELECT * FROM TBempresa"
    cursor.execute(query)
    
    empresas = cursor.fetchall()

    empresas_list = []
    for empresa in empresas:
        empresa_dict = {
        'empcnpj' : empresa[0],
        'empnaturezajuridica' : empresa[1],
        'empnomerazao' : empresa[2],
        'empnomefantasia' : empresa[3],
        'empvendedor' : empresa[4],
        'empsituacao' : empresa[5],
        'emptipo' : empresa[6],
        'empuf' : empresa[7],
        'empmunicipio' : empresa[8],
        'empemail' : empresa[9],
        'empbairro' : empresa[10],
        'emplogradouro' : empresa[11],
        'empcep' : empresa[12],
        'empnumeroendereco' : empresa[13],
        'empcomplementoendereco' : empresa[14],
        'emptelefone' : empresa[15],
        'empstatus' : empresa[16],
        'empporte' : empresa[17],
        'empfatanualestimado' : empresa[18],
        'empcapitalsocial' : empresa[19],
        'empnumerofuncionarios' : empresa[20],
        'empdataabertura' : empresa[21],
        'empatividadepri' : empresa[22]

        }            

        empresas_list.append(empresa_dict)

    cursor.close()
    conn.close()

    return make_response(jsonify(empresas_list))

app.run()

