from flask import Flask, request
import requests
import pandas as pd
from sqlalchemy import create_engine


# Definir informações de conexão com o banco de dados
db_username = 'postgres'
db_password = 'postgres'
db_host = '192.168.15.83'
db_port = '5432'
db_name = 'zanella'

# Criar uma conexão com o banco de dados usando SQLAlchemy
engine = create_engine(f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

def processar_cnpj():
    cnpj = input('Digite o cnpj: ')
    cnpj = cnpj.replace('/', '').replace('.', '').replace('-', '')
    rf_url = f'https://receitaws.com.br/v1/cnpj/{cnpj}'
    

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
        'empcnpj': data['cnpj'],
        'empstatus': data['status'],
        'empnomefantasia': data['fantasia'],
        'empcapitalsocial': data['capital_social'],
        'empatividadepri': data['atividade_principal'][0]['text'],
        'empnumerofuncionarios' : '',
        'empfatanualestimado' : ''
    }

    # Criar um DataFrame com os dados da empresa
    df_empresa = pd.DataFrame([dados_empresa])

    # Criar uma tabela para a empresa no banco de dados e inserir os dados
    table_name_empresa = 'tbempresa'
    df_empresa.to_sql(table_name_empresa, engine, if_exists='append', index=False)

    # Extrair as atividades secundárias
    atividades_secundarias = data['atividades_secundarias']

    # Converter as atividades secundárias para DataFrame
    df_atividades_secundarias = pd.DataFrame(atividades_secundarias)

    # Adicionar a coluna de CNPJ
    df_atividades_secundarias['cnpj'] = data['cnpj']

    # Renomear as colunas
    df_atividades_secundarias = df_atividades_secundarias.rename(columns={'code': 'codigo', 'text': 'descricao'})

    # Criar uma tabela para atividades secundárias no banco de dados e inserir os dados
    table_name_atividades_secundarias = 'atividades_secasdasdundarias'
    df_atividades_secundarias.to_sql(table_name_atividades_secundarias, engine, if_exists='append', index=False)

    # Fechar a conexão
    engine.dispose()

if __name__ == '__main__':
    processar_cnpj()
