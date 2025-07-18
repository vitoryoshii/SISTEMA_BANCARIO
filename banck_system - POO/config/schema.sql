CREATE TABLE IF NOT EXISTS clientes (
    cpf TEXT NOT NULL PRIMARY KEY,
    nome TEXT NOT NULL,
    data_nascimento TEXT,
    endereco TEXT,
    tipo TEXT CHECK (tipo IN ('FISICA', 'JURIDICA')) NOT NULL
);

CREATE TABLE IF NOT EXISTS contas (
    numero_conta INTEGER NOT NULL,
    agencia TEXT NOT NULL DEFAULT '0001',
    cpf TEXT NOT NULL,
    saldo REAL NOT NULL DEFAULT 0.0,
    limite_saque REAL NOT NULL DEFAULT 1000.0,
    limite_transacoes INTEGER NOT NULL DEFAULT 10,
    PRIMARY KEY (numero_conta, agencia),
    FOREIGN KEY (cpf) REFERENCES clientes(cpf)
);

CREATE TABLE IF NOT EXISTS transacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conta_numero INTEGER NOT NULL,
    agencia TEXT NOT NULL DEFAULT '0001',
    tipo TEXT NOT NULL,
    valor REAL NOT NULL,
    data TEXT NOT NULL,
    FOREIGN KEY (conta_numero, agencia) REFERENCES contas(numero_conta, agencia)
);
