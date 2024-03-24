
CREATE TABLE public.tbempresa (
                empcnpj VARCHAR(14) NOT NULL,
                empnaturezajuridica VARCHAR(150),
                empnomerazao VARCHAR(255),
                empnomefantasia VARCHAR(255),
                empvendedor VARCHAR(255),
                empsituacao VARCHAR(150),
                emptipo VARCHAR(15),
                empuf VARCHAR(2),
                empmunicipio VARCHAR(100),
                empemail VARCHAR(150),
                empbairro VARCHAR(100),
                emplogradouro VARCHAR(100),
                empcep VARCHAR(10),
                empnumeroendereco VARCHAR,
                empcomplementoendereco VARCHAR,
                emptelefone VARCHAR(16),
                empstatus VARCHAR(10),
                empporte VARCHAR(15),
                empfatanualestimado NUMERIC(15,2),
                empcapitalsocial NUMERIC(15,2),
                empnumerofuncionarios INTEGER,
                empdataabertura DATE,
                empatividadepri VARCHAR,
                CONSTRAINT pk_tbempresa PRIMARY KEY (empcnpj)
);
COMMENT ON TABLE public.tbempresa IS 'Tabela Para Armazenar Empresas e Suas Informações.';