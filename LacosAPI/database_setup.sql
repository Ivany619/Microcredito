-- Script de criação do esquema (PostgreSQL) para MasterLacosMicrocredito
-- Observação: execute o CREATE DATABASE e \c no psql se necessário, depois rode este script.

-- =========================
-- TABELAS E SEQUÊNCIAS
-- =========================

-- CLIENTES
CREATE TABLE public.clientes (
    cliente_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome text NOT NULL,
    sexo text NOT NULL,
    telefone text NOT NULL UNIQUE,
    email text UNIQUE,
    nacionalidade text DEFAULT 'Moçambicana' NOT NULL,
    data_cadastro timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    data_nascimento date NOT NULL,
    CONSTRAINT clientes_nacionalidade_check CHECK (nacionalidade IN ('Moçambicana', 'Estrangeira')),
    CONSTRAINT clientes_sexo_check CHECK (sexo IN ('Masculino','Feminino','Outro'))
);

-- AUTENTICACAO CLIENTES
CREATE TABLE public.autenticacao_clientes (
    autenticacao_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id bigint NOT NULL,
    username text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    data_criacao timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    ultimo_login timestamp with time zone,
    tentativas_login integer DEFAULT 0,
    bloqueado boolean DEFAULT false,
    data_bloqueio timestamp with time zone,
    CONSTRAINT autenticacao_clientes_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE
);

-- DOCUMENTOS
CREATE TABLE public.documentos (
    documento_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id bigint,
    tipo_documento text NOT NULL,
    numero_documento text NOT NULL UNIQUE,
    arquivo bytea,
    CONSTRAINT documentos_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE,
    CONSTRAINT documentos_tipo_documento_check CHECK (tipo_documento IN (
        'BI','Passaporte','Carta de Conducao','NUIT','Contrato Microcredito',
        'Livrete','DIRE','Certidao de Nascimento','Certificado de Habilitacoes',
        'Comprovativo de Residencia','Talao de Deposito','Outro'))
);

-- EMPRESTIMOS
CREATE TABLE public.emprestimos (
    emprestimo_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id bigint,
    valor numeric(10,2) NOT NULL,
    data_emprestimo timestamp with time zone NOT NULL,
    data_vencimento timestamp with time zone NOT NULL,
    status text DEFAULT 'Ativo' NOT NULL,
    CONSTRAINT emprestimos_status_check CHECK (status IN ('Ativo','Pago','Inadimplente')),
    CONSTRAINT emprestimos_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE
);

-- FUNCIONARIOS
CREATE TABLE public.funcionarios (
    funcionario_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username text NOT NULL UNIQUE,
    senha text NOT NULL,
    nome_completo text NOT NULL,
    email text NOT NULL UNIQUE,
    telefone text,
    nivel_acesso text NOT NULL,
    data_cadastro timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    ultimo_login timestamp with time zone,
    ativo boolean DEFAULT true,
    tentativas_login integer DEFAULT 0,
    bloqueado boolean DEFAULT false,
    data_bloqueio timestamp with time zone,
    CONSTRAINT funcionarios_nivel_acesso_check CHECK (nivel_acesso IN ('Administrador','Gestor','Operador','Consultor'))
);

-- HISTORICO DE CREDITO
CREATE TABLE public.historico_credito (
    historico_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id bigint,
    emprestimo_anterior numeric(10,2),
    status text NOT NULL,
    data_ultimo_pagamento timestamp with time zone,
    CONSTRAINT historico_credito_status_check CHECK (status IN ('Pago','Inadimplente','Atrasado')),
    CONSTRAINT historico_credito_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE
);

-- LOCALIZACAO
CREATE SEQUENCE public.localizacao_localizacao_id_seq;
CREATE TABLE public.localizacao (
    localizacao_id bigint NOT NULL DEFAULT nextval('public.localizacao_localizacao_id_seq'),
    cliente_id bigint,
    bairro text,
    numero_da_casa text,
    quarteirao text,
    cidade text NOT NULL,
    distrito text NOT NULL,
    provincia text NOT NULL,
    PRIMARY KEY (localizacao_id),
    CONSTRAINT localizacao_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE
);

-- NOTIFICACOES
CREATE TABLE public.notificacoes (
    notificacao_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id bigint,
    tipo text NOT NULL,
    mensagem text NOT NULL,
    data_envio timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    status text DEFAULT 'Pendente',
    CONSTRAINT notificacoes_status_check CHECK (status IN ('Enviado','Lido','Pendente')),
    CONSTRAINT notificacoes_tipo_check CHECK (tipo IN ('Lembrete de Pagamento','Atraso no Pagamento',
        'Confirmação de Pagamento','Confirmação de Empréstimo','Penalização Aplicada','Outro')),
    CONSTRAINT notificacoes_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE
);

-- OCUPACOES
CREATE TABLE public.ocupacoes (
    ocupacao_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id bigint NOT NULL,
    codigo varchar(10) NOT NULL,
    nome varchar(100) NOT NULL,
    descricao text,
    categoria_risco varchar(20) NOT NULL,
    renda_minima numeric(10,2),
    setor_economico varchar(50) NOT NULL,
    estabilidade_emprego varchar(20) NOT NULL,
    ativo boolean DEFAULT true,
    CONSTRAINT ocupacoes_categoria_risco_check CHECK (categoria_risco IN ('Muito Baixo','Baixo','Medio','Alto','Muito Alto')),
    CONSTRAINT ocupacoes_estabilidade_emprego_check CHECK (estabilidade_emprego IN ('Alta','Media','Baixa','Sazonal')),
    CONSTRAINT ocupacoes_setor_economico_check CHECK (setor_economico IN ('Primario','Secundario','Terciario','Quaternario')),
    CONSTRAINT ocupacoes_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE
);

-- OUTROS GANHOS
CREATE TABLE public.outros_ganhos (
    ganho_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id bigint,
    descricao text NOT NULL,
    valor numeric(10,2) NOT NULL,
    CONSTRAINT outros_ganhos_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE
);

-- PAGAMENTOS
CREATE TABLE public.pagamentos (
    pagamento_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    emprestimo_id bigint,
    cliente_id bigint,
    valor_pago numeric(10,2) NOT NULL,
    data_pagamento timestamp with time zone NOT NULL,
    metodo_pagamento text NOT NULL,
    referencia_pagamento text,
    CONSTRAINT pagamentos_metodo_pagamento_check CHECK (metodo_pagamento IN ('Numerario','Transferência Bancária',
        'M-Pesa','E-Mola','MKesh','Penhor','Outro')),
    CONSTRAINT pagamentos_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE,
    CONSTRAINT pagamentos_emprestimo_id_fkey FOREIGN KEY (emprestimo_id)
        REFERENCES public.emprestimos(emprestimo_id) ON DELETE CASCADE
);

-- PENALIZACOES
CREATE TABLE public.penalizacoes (
    penalizacao_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    emprestimo_id bigint NOT NULL,
    cliente_id bigint NOT NULL,
    tipo text NOT NULL,
    dias_atraso integer DEFAULT 0,
    valor numeric(10,2) NOT NULL,
    status text NOT NULL,
    data_aplicacao timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    observacoes text,
    CONSTRAINT penalizacoes_status_check CHECK (status IN ('pendente','simulado','aplicada','cancelada')),
    CONSTRAINT fk_cliente FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE,
    CONSTRAINT fk_emprestimo FOREIGN KEY (emprestimo_id)
        REFERENCES public.emprestimos(emprestimo_id) ON DELETE CASCADE
);

-- PENHOR
CREATE TABLE public.penhor (
    penhor_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id bigint,
    descricao_item text NOT NULL,
    valor_estimado numeric(10,2) NOT NULL,
    data_penhora timestamp with time zone NOT NULL,
    CONSTRAINT penhor_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE
);

-- TESTEMUNHAS
CREATE TABLE public.testemunhas (
    testemunha_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id bigint,
    nome text NOT NULL,
    telefone text NOT NULL UNIQUE,
    tipo_relacao text NOT NULL,
    CONSTRAINT testemunhas_tipo_relacao_check CHECK (tipo_relacao IN ('Parente','Amigo','Colega','Outro')),
    CONSTRAINT testemunhas_cliente_id_fkey FOREIGN KEY (cliente_id)
        REFERENCES public.clientes(cliente_id) ON DELETE CASCADE
);
