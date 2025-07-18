from decimal import Decimal
from datetime import datetime
from .database import DatabaseManager
from .models import PessoaFisica, ContaCorrente, Deposito
import sqlite3

class Persistencia:
    @staticmethod
    def carregar_usuarios() -> list:
        with DatabaseManager() as db:
            usuarios = []
            for row in db.fetch_all("SELECT * FROM clientes WHERE tipo = 'FISICA'"):
                
                usuario = PessoaFisica(
                    nome=row['nome'],
                     cpf=row['cpf'],
                    data_nascimento=row['data_nascimento'],
                    endereco=row['endereco']
                )
                usuarios.append(usuario)

            return usuarios

    @staticmethod
    def salvar_usuario(usuario: PessoaFisica) -> bool:
        try:
            with DatabaseManager() as db:
                #por padrão, tipo 'FISICA' para Pessoa Física. Depois pode ser alterado para incluir Pessoa Jurídica.
                db.executar_query("""
                    INSERT INTO clientes (cpf, nome, data_nascimento, endereco, tipo)
                    VALUES (?, ?, ?, ?, 'FISICA') 
                    ON CONFLICT(cpf) DO UPDATE SET 
                    nome = excluded.nome,
                    data_nascimento = excluded.data_nascimento,
                    endereco = excluded.endereco
                """, (usuario.cpf, usuario.nome, usuario.data_nascimento, usuario.endereco))
            return True
        except Exception as e:
            print(f"Erro ao salvar usuário: {str(e)}")
            return False

    def carregar_contas() -> list:
        with DatabaseManager as db:
            contas = []
            usuarios = {u.cpf: u for u in Persistencia.carregar_usuarios()}

            for row in db.fetch_all("""
                SELECT c.*, c1.nome as cliente_nome
                FROM contas c
                JOIN clientes c1 ON c.cpf = c1.cpf
            """):
                usuario = usuarios.get(row['cpf'])
                if not usuario:
                    continue

                conta = ContaCorrente(
                    numero_conta=row['numero_conta'],
                    cliente=usuario,
                    limite=Decimal(str(row['limite_saque'])),
                    limite_transacoes=row['limite_transacoes']
                )
                conta._saldo = Decimal(str(row['saldo']))
                contas.append(conta)
                usuario.adicionar_conta(conta)

            return contas
    
    @staticmethod
    def salvar_conta(conta: ContaCorrente) -> bool:
        try:
            with DatabaseManager() as db:
                db.executar_query("""
                    INSERT INTO contas (numero_conta, agencia, cpf, saldo, limite_saque, limite_transacoes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(numero_conta, agencia) DO UPDATE SET 
                        saldo = excluded.saldo,
                        limite_saque = excluded.limite_saque,
                        limite_transacoes = excluded.limite_transacoes
                """, (conta.numero_conta, conta.agencia, conta.cliente.cpf, float(conta.saldo), float(conta._limite), conta._limite_transacoes))
                return True
        except Exception as e:
            print(f"Erro ao salvar conta: {str(e)}")
            return False

    @staticmethod
    def registrar_transacao_banco(conta: ContaCorrente, transacao) -> bool:
        try:
            with DatabaseManager() as db:
                db.executar_query("""
                    INSERT INTO transacoes 
                    (numero_conta, agencia, tipo, valor, data)
                    VALUES (?, ?, ?, ?, ?)
                """, (conta.numero_conta, conta.agencia, transacao.__class__.__name__, str(transacao.valor), datetime.now().strftime('%d/%m/%Y - %H:%M')))

                operador = '+' if isinstance(transacao, Deposito) else '-'
                db.executar_query(f"""
                    UPDATE contas
                    SET saldo = saldo {operador} ?
                    WHERE numero_conta = ? AND agencia = ?
                """, (str(transacao.valor), conta.numero_conta, conta.agencia))
            return True
        except sqlite3.Error as e:
            print(f"\n@@@ Erro ao registrar transação no banco: {str(e)} @@@")
            return False
        except Exception as e:
            print(f"\n@@@ Erro inesperado: {str(e)} @@@")
            return False