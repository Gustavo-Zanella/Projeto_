
CREATE TABLE public.tbempresa (
                empcnpj VARCHAR(14) NOT NULL,
                empnaturezajuridica VARCHAR(150),
                empnomerazao VARCHAR(255),
                empnomefantasia VARCHAR(255),
                empsituacao VARCHAR(15),
                emptipo VARCHAR(15),
                empuf VARCHAR(2),
                empmunicipio VARCHAR(100),
                empemail VARCHAR(150) NOT NULL,
                empbairro VARCHAR(100),
                emplogradouro VARCHAR(100),
                empcep VARCHAR(10) NOT NULL,
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


CREATE TABLE public.tbsocioempresa (
                socnome VARCHAR(255) NOT NULL,
                socqualificacao VARCHAR(100) NOT NULL,
                empcnpj VARCHAR(14) NOT NULL,
                CONSTRAINT pk_tbsocioempresa PRIMARY KEY (socnome, socqualificacao, empcnpj)
);


CREATE TABLE public.tbempresaatividadesec (
                empcnpj VARCHAR(14) NOT NULL,
                empatividade VARCHAR NOT NULL,
                CONSTRAINT pk_tbempresaatividadesec PRIMARY KEY (empcnpj)
);


ALTER TABLE public.tbempresaatividadesec ADD CONSTRAINT tbempresa_tbempresaatividade_fk
FOREIGN KEY (empcnpj)
REFERENCES public.tbempresa (empcnpj)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.tbsocioempresa ADD CONSTRAINT tbempresa_tbsocioempresa_fk
FOREIGN KEY (empcnpj)
REFERENCES public.tbempresa (empcnpj)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;