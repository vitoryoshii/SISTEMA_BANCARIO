from abc import ABC, abstractproperty, abstractclassmethod
from .utils import data_hora

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        self.indice_conta = 0

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.cpf}')>"

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
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero_conta}', '{self.usuario.nome}')>"

    def __str__(self):
        return f'''
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero_conta}
            Titular:\t{self.usuario.nome}
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
                "data": data_hora()
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self.transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

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
