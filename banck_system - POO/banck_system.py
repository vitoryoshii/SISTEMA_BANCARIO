import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
from recursosEX import validarCPF, data_hora_atual

# Modelando POO

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class Pessoa_fisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero_conta, cpf):
        self._saldo = 0
        self._agencia = "0001"
        self._numero_conta = numero_conta
        self._usuario = cpf
        self._historico = Historico()

    @classmethod
    def criar_conta(cls, numero_conta, usuario):
        return cls(numero_conta, usuario)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def numero_conta(self):
        return self._numero_conta
    
    @property
    def usuario(self):
        return self._usuario
    
    @property
    def historico(self):
        return self._historico

    def sacar(self, valor_saque):
        saldo = self.saldo
        excedeu_saldo = valor_saque > saldo

        if excedeu_saldo: 
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
        elif valor_saque > 0:
            self._saldo -= valor_saque
            print("\n=== Saque realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
        
        return False

    def depositar(self, valor_deposito):
        if valor_deposito > 0:
            self._saldo += valor_deposito
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
        return True

class ContaCorrente(Conta):
    def __init__(self, numero_conta, usuario, limite=500, limite_saque=3):
        super().__init__(numero_conta, usuario)
        self._limite = limite
        self._limite_saque = limite_saque

    def sacar(self, valor_saque):
        numero_saque = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
       )
        
        excedeu_limite = valor_saque > self._limite
        excedeu_saques = numero_saque >= self._limite_saque

        if excedeu_limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
        elif excedeu_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
        else:
            return super().sacar(valor_saque)
        
        return False
    
    def __str__(self):
        return f'''
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero_conta}
            Titular:\t{self.cliente.nome}
        '''

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self.transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M")
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, numero_conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, numero_conta):
        sucesso_transacao = numero_conta.sacar(self.valor)

        if sucesso_transacao:
            numero_conta.historico.adicionar_transacao(self)
    
class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, numero_conta):
        sucesso_transacao = numero_conta.depositar(self.valor)

        if sucesso_transacao:
            numero_conta.historico.adicionar_transacao(self)

def menu():
    horario_atual = datetime.now().strftime("%d-%m-%Y %H:%M")
    
    menu = f'''
    ==== {data_hora_atual()} ====
    ========== MENU ==========

    [0]\tDEPOSITAR
    [1]\tSACAR
    [2]\tEXTRATO
    [3]\tNOVA CONTA
    [4]\tLISTAR CONTAS
    [5]\tNOVO USUARIO
    [6]\tLISTAR USUÁRIOS
    [7]\tSAIR

    =========================
    '''
    return int(input(textwrap.dedent(menu)))

def filtro_usuarios(cpf, usuarios):
    usuario_filtrado = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuario_filtrado[0] if usuario_filtrado else None

def recuperar_conta_usuario(usuario):
    if not usuario.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return
    
    return usuario.contas[0]

def depositar(usuarios):
    cpf = input("Digite o CPF do usuário: ")
    usuario = filtro_usuarios(cpf, usuarios)

    if not usuario:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    valor_deposito = float(input("Digite o valor do depósito: "))
    transacao = Deposito(valor_deposito)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    usuario.realizar_transacao(conta, transacao)

def sacar(usuarios):
    cpf = input("Digite o CPF do usuário: ")
    usuario = filtro_usuarios(cpf, usuarios)

    if not usuario:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    valor_saque = float(input("Digite o valor do saque: "))
    transacao = Saque(valor_saque)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    usuario.realizar_transacao(conta, transacao)

def exibir_extrato(usuarios):
    cpf = input("Digite o CPF do usuário: ")
    usuario = filtro_usuarios(cpf, usuarios)

    if not usuario:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f} - {transacao['data']}"
        
        print(extrato)
        print(f"\nSALDO: R$ {conta.saldo:.2f}")
        print("\n=========================================")

def criar_usuario(usuarios):
    print("=== CADASTRO DE USUÁRIO ===")
    print("=== CPF: 000.000.000-00 ===")
    cpf = input("Digite o CPF (apenas números ou com pontuação): ")

    if not validarCPF(cpf):
        print("\n@@@ CPF inválido! Tente novamente. @@@")
        return

    usuario = filtro_usuarios(cpf, usuarios)
    if usuario: 
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return
    
    nome = input("Digite seu nome completo: ")
    data_nascimento = input("Digite sua data de nascimento (dd-mm-aaaa): ")
    endereco = input("Digite seu endereço (Logradouro, número - bairro - cidade/UF): ")

    cliente = Pessoa_fisica(nome=nome, data_nascimento=data_nascimento, endereco=endereco, cpf=cpf)
    usuarios.append(cliente)

    print("=== Usuário criado com sucesso! ===")

def criar_conta(numero_conta, usuarios, contas):
    cpf = input("Digite o CPF do usuário: ")
    usuario = filtro_usuarios(cpf, usuarios)

    if not usuario:
        print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")
        return
    
    conta = ContaCorrente.criar_conta(usuario=usuario, numero_conta=numero_conta)
    contas.append(conta)
    usuario.adicionar_conta(conta)

    print("=== Conta criada com sucesso! ===")

def listar_contas(usuarios):
    for usuario in usuarios:
        for conta in usuario.contas:
            print("=" * 50)
            print(f"Nome: {usuario.nome} | Conta: {conta.numero_conta} | Saldo: R$ {conta.saldo:.2f}")

def listar_usuarios(usuarios):
    if not usuarios:
        print("\n@@@ Não há usuários cadastrados. @@@")
        return
    
    print("\n============== LISTA DE USUÁRIOS ==============")
    for usuario in usuarios:
        print(f"Nome: {usuario.nome}")
        print(f"CPF: {usuario.cpf}")
        print(f"Data de Nascimento: {usuario.data_nascimento}")
        print(f"Endereço: {usuario.endereco}")
        print("=" * 50)

def main():
    usuarios = []   
    contas = []

    while True:
        opcao = menu()

        if opcao == 0: # DEPOSITAR
            print("DEPOSITO")
            depositar(usuarios)
        elif opcao == 1: # SACAR    
            print("SACAR")
            sacar(usuarios)
        elif opcao == 2: # Extrato          
            print("EXTRATO")
            exibir_extrato(usuarios)
        elif opcao == 3: # NOVA CONTA
            print("CRIAR CONTA")
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, usuarios, contas)
        elif opcao == 4: # LISTAR CONTAS
            print("LISTAS DE CONTAS")
            listar_contas(usuarios)
        elif opcao == 5: # NOVO USUARIO
            print("CADASTRO DE USUÁRIO")
            criar_usuario(usuarios)
        elif opcao == 6: # LISTAR USUÁRIOS
            print("LISTAR USUÁRIOS")
            listar_usuarios(usuarios)
        elif opcao == 7: # Sair
            break
        else: # Opção inválida
            print("\n@@@ Operação falhou! Digite uma opção válida. @@@")

main() # Chama a função main
