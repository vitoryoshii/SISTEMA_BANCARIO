from utils.utils import valida_cpf, log_transacao
from datetime import datetime
from typing import Optional
from models.database import DatabaseManager
from decimal import Decimal
import textwrap

class ContaService:
    def __init__(self):
        self.conta_atual: Optional[dict] = None

    @log_transacao
    def autenticar_cliente(self) -> bool:
        cpf = input("\nDigite seu CPF (somente números): ").strip()
        
        if not valida_cpf(cpf):
            print("\n@@@CPF inválido! @@@")

        with DatabaseManager() as db:
            contas = db.fetch_all("""
                SELECT numero_conta, agencia, saldo 
                FROM contas 
                WHERE cpf = ?
            """, (cpf,))
            
            if not contas:
                print("\n@@@ Nenhuma conta encontrada! @@@")
                return False
            
            print("\n================ SUAS CONTAS ================")
            for i, conta in enumerate(contas, 1):
                print(f"{i} - Ag: {conta['agencia']} C/C: {conta['numero_conta']} | Saldo: R$ {conta['saldo']:.2f}")
            
            try:
                opcao = int(input("\nSelecione a conta: ")) - 1
                if opcao < 0 or opcao >= len(contas):
                    raise ValueError
                
                self.conta_atual = contas[opcao]
                print(f"\n========== CONTA {self.conta_atual['agencia']}.{self.conta_atual['numero_conta']} SELECIONADA ==========")
                return True
            except (ValueError):
                print("\n@@@ Seleção inválida! @@@")
                return False

    def trocar_conta(self) -> bool:
        if not self.conta_atual:
            print("\n@@@ Nenhuma conta selecionada atualmente! @@@")
            return self.autenticar_cliente()
        
        cpf = input("\nDigite seu CPF para autenticar novamente: ").strip()

        if not valida_cpf(cpf):
            print("\n@@@ CFP inválido! @@@")
            return False
        
        try:
            with DatabaseManager() as db:
                conta_atual_valida = db.fetch_one("""
                SELECT 1 
                FROM contas
                WHERE numero_conta = ? AND agencia = ? AND cpf = ? 
                """, (self.conta_atual['numero_conta'], self.conta_atual['agencia'], cpf))
        
            if not conta_atual_valida:
                print("\n@@@ CPF não corresponde à conta atual! @@@")
                return False
            
            with DatabaseManager() as db:
                contas = db.fetch_all(
                    "SELECT numero_conta, agencia, saldo FROM contas WHERE cpf = ?",
                    (cpf,)
                )
            
            if len(contas) <= 1:
                print("\n@@@ Você não possui outras contas! @@@")
                return False
            
            print("\n================ SUAS CONTAS ================")
            for i, conta in enumerate(contas, 1):
                print(f"{i} - Ag: {conta['agencia']} | C/C: {conta['numero_conta']} | Saldo: R$ {conta['saldo']:.2f}")
            
            try:
                opcao = int(input("\nSelecione o número da nova conta: ")) - 1
                if opcao < 0 or opcao >= len(contas):
                    raise ValueError
                    
                if (contas[opcao]['numero_conta'] == self.conta_atual['numero_conta'] and 
                    contas[opcao]['agencia'] == self.conta_atual['agencia']):
                    print("\n@@@ Esta já é a conta selecionada! @@@")
                    return False
                    
                self.conta_atual = contas[opcao]
                print(f"\n========= Conta alterada para {self.conta_atual['agencia']}.{self.conta_atual['numero_conta']} =========")
                return True
                    
            except ValueError:
                print("\n@@@ Opção inválida! @@@")
                return False
        except Exception as e:
            print(f"\n@@@ Erro ao trocar conta: {str(e)} @@@")
            return False

    def limpar_conta(self) -> None:
        if self.conta_atual:
            print(f"\n=== Sessão encerrada para conta {self.conta_atual['agencia']}.{self.conta_atual['numero_conta']} ===")
        self.conta_atual = None

    @log_transacao
    def depositar(self) -> bool:
        print(f"\nSaldo atual: R$ {self.conta_atual['saldo']:.2f}")

        if not self.conta_atual:
            print("\n@@@ Nenhuma conta selecionada! @@@")
            return False
        
        try:
            valor_str = input("\nValor do deposito: ").replace(',', '.')
            valor = Decimal(valor_str)
            
            if valor <= 0:
                print("\n@@@ Valor deve ser positivo! @@@")
                return False
            
            with DatabaseManager() as db:
                conta_info = db.fetch_one("""
                    SELECT limite_transacoes FROM contas
                    WHERE numero_conta = ? AND agencia = ?
                """, (self.conta_atual['numero_conta'], self.conta_atual['agencia']))

                if not conta_info:
                    print("\n@@@ Conta não encontrada! @@@")
                    return False
                
                transacoes_hoje = db.fetch_one("""
                    SELECT COUNT(*) as total
                    FROM transacoes
                    WHERE conta_numero = ? AND agencia = ?
                    AND tipo = 'DEPOSITO'
                    AND date(data) = date('now')
                """, (self.conta_atual['numero_conta'], self.conta_atual['agencia']))

                if transacoes_hoje['total'] >= conta_info['limite_transacoes']:
                    print(f"\n@@@ Limite de {conta_info['limite_transacoes']} depósitos diários atingido! @@@")
                    return False

                db.executar_query("""
                    UPDATE contas 
                    SET saldo = saldo + ? 
                    WHERE numero_conta = ? AND agencia = ?
                """, (str(valor), self.conta_atual['numero_conta'], self.conta_atual['agencia']))
                
                db.executar_query("""
                    INSERT INTO transacoes (conta_numero, agencia, tipo, valor, data)
                    VALUES (?, ?, 'DEPOSITO', ?, ?)
                """, (self.conta_atual['numero_conta'], self.conta_atual['agencia'], str(valor), datetime.now().strftime('%d/%m/%Y - %H:%M:%S')))
            
            self.conta_atual['saldo'] = Decimal(str(self.conta_atual['saldo'])) + valor
            print(f"\n=== Depósito de R$ {valor:.2f} realizado! ===")
            return True
        
        except Exception as e:
            print(f"\n@@@ Erro no depósito: {str(e)} @@@")
            return False

    @log_transacao
    def sacar(self) -> bool:
        print(f"\nLimite por saque: R$ 1000.00")
        print(f"Saldo disponível: R$ {self.conta_atual['saldo']:.2f}")

        if not self.conta_atual:
            print("\n@@@ Nenhuma conta selecionada! @@@")
            return False
        
        try:
            valor_str = input("\nValor do saque: ").replace(',', '.')
            valor = Decimal(valor_str)
            if valor <= 0:
                print("\n@@@ Valor deve ser positivo! @@@")
                return False
        
            with DatabaseManager() as db:
                conta_info = db.fetch_one("""
                    SELECT saldo, limite_saque, limite_transacoes FROM contas 
                    WHERE numero_conta = ? AND agencia = ?
                """, (self.conta_atual['numero_conta'], self.conta_atual['agencia']))

                if not conta_info:
                    print("\n@@@ Conta não encontrada! @@@")
                    return False
                
                if valor > conta_info['saldo']:
                    print("\n@@@ Saldo insulficiente! @@@")
                    return False
                
                if valor > conta_info['limite_saque']:
                    print(f"\n@@@ Valor excede o limite de saque de R$ {conta_info['limite_saque']:.2f}! @@@")
                    return False
                
                transacoes_hoje = db.fetch_one("""
                    SELECT COUNT(*) as total
                    FROM transacoes
                    WHERE conta_numero = ? AND agencia = ?
                    AND tipo = 'SAQUE'
                    AND date(data) = date('now')
                """, (self.conta_atual['numero_conta'], self.conta_atual['agencia']))

                if transacoes_hoje['total'] >= conta_info['limite_transacoes']:
                    print(f"\n@@@ Limite de {conta_info['limite_transacoes']} saques diários atingido! @@@")
                    return False

                with db.connection:
                    db.executar_query("""
                        UPDATE contas 
                        SET saldo = saldo - ? 
                        WHERE numero_conta = ? AND agencia = ?
                    """, (str(valor), self.conta_atual['numero_conta'], self.conta_atual['agencia']))
                    
                    db.executar_query("""
                        INSERT INTO transacoes (conta_numero, agencia, tipo, valor, data)
                        VALUES (?, ?, 'SAQUE', ?, ?)
                    """, (self.conta_atual['numero_conta'], self.conta_atual['agencia'], str(valor), datetime.now().strftime('%d/%m/%Y - %H:%M:%S')))

            self.conta_atual['saldo'] = Decimal(str(self.conta_atual['saldo'])) - valor
            print(f"\n=== Saque de R$ {valor:.2f} realizado com sucesso! ===")
            print(f"\nNovo saldo: R$ {self.conta_atual['saldo']:.2f}")
            return True
        
        except Exception as e:
            print(f"\n@@@ Erro no saque: {e} @@@")
            return False

    @log_transacao
    def extrato(self) -> None:
        """Exibe extrato da conta selecionada"""
        if not self.conta_atual:
            print("\n@@@ Nenhuma conta selecionada! @@@")
            return 

        with DatabaseManager() as db:
            transacoes = db.fetch_all("""
                SELECT tipo, valor, data
                FROM transacoes
                WHERE conta_numero = ? AND agencia = ?
                ORDER BY data DESC
                LIMIT 15
            """, (self.conta_atual['numero_conta'], self.conta_atual['agencia']))

            saldo = db.fetch_one(
                "SELECT saldo FROM contas WHERE numero_conta = ? AND agencia = ?",
                (self.conta_atual['numero_conta'], self.conta_atual['agencia'])
            ) or {'saldo': 0}

        print(f"\n=========== EXTRATO - CONTA {self.conta_atual['agencia']}.{self.conta_atual['numero_conta']} ===========")
        
        if not transacoes:
            print("Nenhuma transação recente")
        else:
            print("\nData/Hora             | Operação | Valor")
            print("-" * 46)
            for t in transacoes:
                print(f"{t['data']} | {t['tipo']:8} | R$ {t['valor']:>9.2f}")
        
        print("\n" + "=" * 46)
        print(f"\nSALDO ATUAL: R$ {saldo['saldo']:.2f}")
        print("=" * 46)

#    @log_transacao
    #def exibir_extrato(Todos=False):
#        usuarios, _ = carregar_dados_database()
#        cpf = input("Digite o CPF do usuário: ")
#        usuario = filtro_usuarios(cpf, usuarios)

#        if not usuario:
#            print("\n@@@ Cliente não encontrado! @@@")
#            return
#        
#        conta = recuperar_conta_usuario(usuario)
#        if not conta:
#            return
        
#        print("\n================ EXTRATO ================")

        # Buscar transações no banco de dados
#        from .database import DatabaseManager
#        with DatabaseManager() as db:
#                transacoes = db.fetch_all("""
#                SELECT tipo, valor, data FROM transacoes 
#                WHERE numero_conta = ? AND agencia = ? ORDER BY data DESC
#                """, (conta.numero_conta, conta.agencia)
#                )
        
#        if not transacoes:
#            print("Não foram realizadas movimentações.")
#        else:
#            for t in transacoes:
#                print(f"\n{t['tipo']}:\n\tR$ {Decimal(t['valor']):.2f}\n\t{t['data']}")
        
#        print(f"\nSALDO: R$ {conta.saldo:.2f}")
#        print("\n=========================================")

class GerenteService:    
    @log_transacao
    def criar_usuario(self) -> bool:
        print("=========== CADASTRO DE USUÁRIO ===========")
        cpf = input("Digite o CPF (somente números): ").strip()

        if not valida_cpf(cpf):
            print("\n@@@ CPF inválido! @@@")
            return False
        
        with DatabaseManager() as db:
            if db.fetch_one("SELECT 1 FROM clientes WHERE cpf = ?", (cpf,)):
                print("\n@@@ Usuário já cadastrado! @@@")
                return False
        
        nome = input("Nome completo: ")
        if not nome:
            print("\n@@@ Nome é obrigatório! @@@")

        data_nascimento = input("Data de nascimento (DD-MM-AAAA): ").strip()
        endereco = input("Endereço (Logradouro, n° - bairro - cidade/UF): ").strip()

        try:
            with DatabaseManager() as db:
                db.executar_query("""
                    INSERT INTO clientes (cpf, nome, data_nascimento, endereco, tipo)
                    VALUES (?, ?, ?, ?, 'FISICA')
                """, (cpf, nome, data_nascimento, endereco))
                print("\n====== Usuário cadastrado com sucesso! ======")
                return True
        except Exception as e: 
            print(f"\n@@@ Erro ao cadastrar cliente: {str(e)} @@@")
            return False
        
    @log_transacao
    def criar_conta(self) -> bool:
        print("\n============ NOVA CONTA CORRENTE ===========")
        cpf = input("\nCPF do cliente: ").strip()

        if not valida_cpf(cpf):
            print("\n@@@ CPF inválido! @@@")
            return False

        with DatabaseManager() as db:
            cliente = db.fetch_one("SELECT nome FROM clientes WHERE cpf = ?", (cpf,))
            if not cliente:
                print("\n@@@ Cliente não encontrado! @@@")
                return False

            ultima_conta = db.fetch_one("SELECT MAX(numero_conta) as ultimo FROM contas") or {}
            nova_conta = (ultima_conta.get('ultimo') or 0) + 1

            try:
                db.executar_query("""
                    INSERT INTO contas (numero_conta, agencia, cpf, saldo, limite_saque, limite_transacoes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (nova_conta, '0001', cpf, 0.0, 1000.0, 10))

                print(f"\n=== Conta criada com sucesso! ===")
                print(f"Agência: 0001 | Conta: {nova_conta}")
                print(f"Titular: {cliente['nome']}")
                return True
            except Exception as e:
                print(f"\n@@@ Erro ao criar conta: {str(e)} @@@")
                return False

    @log_transacao
    def listar_contas(self) -> None:
        print("\n============ CONTAS CADASTRADAS ============")            
            
        with DatabaseManager() as db:
            query = db.fetch_all("""
            SELECT 
                    c.numero_conta as numero_conta,
                    c.agencia as agencia,
                    c.saldo as saldo,
                    cl.nome as nome,
                    cl.cpf as cpf
                FROM contas c
                JOIN clientes cl ON c.cpf = cl.cpf
                ORDER BY c.numero_conta
            """)
        
            if not query:
                print("\n@@@ Não há contas cadastradas. @@@")
                return

            for conta in query:
                print(textwrap.dedent(f"""
                    Titular: {conta['nome']}
                    CPF: {conta['cpf']}
                    Agência: {conta['agencia']}
                    Conta: {conta['numero_conta']}
                    Saldo: R$ {float(conta['saldo']):.2f}
                """))
                print("=" * 44)

    @log_transacao
    def listar_usuarios(self) -> None:
        print("\n=========== CLIENTES CADASTRADOS ===========")
        with DatabaseManager() as db:
            clientes = db.fetch_all("""
                SELECT cpf, nome, data_nascimento, endereco
                FROM clientes
                ORDER BY nome
            """)
        
        if not clientes:
            print("\n@@@ Nenhum cliente cadastrado @@@")

        for cliente in clientes:
            print(textwrap.dedent(f"""
                Nome: {cliente['nome']}
                CPF: {cliente['cpf']}
                Data de Nascimento: {cliente['data_nascimento']}
                Endereço: {cliente['endereco']}
            """))
            print("=" * 44)

    @log_transacao
    def visualizar_extrato(self) -> None:
        print("\n=== VISUALIZAR EXTRATO (QUALQUER CONTA) ===")

        cpf = input("Digite o CPF do cliente (somente números): ").strip()

        if not valida_cpf(cpf):
            print("\n@@@ CPF inválido! @@@")
            return
        
        try: 
            with DatabaseManager() as db:
                contas = db.fetch_all("""
                SELECT c.numero_conta, c.agencia, c.saldo, cl.nome 
                FROM contas c
                JOIN clientes cl ON c.cpf = cl.cpf
                WHERE cl.cpf = ?
                ORDER BY c.numero_conta
            """, (cpf,))
                
            if not contas:
                print("\n@@@ Nenhuma conta encontrada para este CPF! @@@")
                return
            
            print(f"\nContas disponíveis para {contas[0]['nome']}:")
            for i, conta in enumerate(contas, 1):
                print(f"{i} - Ag: {conta['agencia']} C/C: {conta['numero_conta']} | Saldo: R$ {float(conta['saldo']):.2f}")

            try:
                opcao = int(input("\nSelecionar a conta(número): ")) - 1
                conta_selecionada = contas[opcao]
            except (ValueError, IndentationError):
                print("\n@@@ Seleção inválida! @@@")
                return
            
            with DatabaseManager() as db:
                transacoes = db.fetch_all("""
                    SELECT tipo, valor, data 
                    FROM transacoes
                    WHERE conta_numero = ? AND agencia = ?
                    ORDER BY data DESC
                    LIMIT 15
                """, (conta_selecionada['numero_conta'], conta_selecionada['agencia']))

            print(f"\n========== EXTRATO - CONTA {conta_selecionada['agencia']}.{conta_selecionada['numero_conta']} ==========")
            print(textwrap.dedent(f"""
                \nTitular: {conta_selecionada['nome']}
                \nSaldo atual: R$ {float(conta_selecionada['saldo']):.2f}
                \nÚtimas transações:
                \n{"-" * 44}
            """))   

            if not transacoes:
                print("Nenhuma transação registrada")
            else:
                print("Data/Hora             | Operação | Valor")
                print("-" * 44)
                for t in transacoes:
                    print(f"{t['data']} | {t['tipo']:8} | R$ {float(t['valor']):>9.2f}")
            
            print("\n" + "=" * 44)
        
        except Exception as e:
            print(f"\n@@@ Erro ao visualizar extrato: {str(e)} @@@")