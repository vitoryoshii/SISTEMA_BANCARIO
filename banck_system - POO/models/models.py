from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional

class Cliente:
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas: List['Conta'] = []

    def realizar_transacao(self, conta: 'Conta', transacao: 'Transacao') -> bool:
        return transacao.registrar(conta)

    def adicionar_conta(self, conta: 'Conta') -> None:
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome: str, cpf: str, data_nascimento: str, endereco: str):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

    def __str__(self):
        return f"{self.nome} (CPF: {self.cpf})"

class Conta:
    def __init__(self, numero_conta: int, cliente: PessoaFisica):
        self._saldo = Decimal('0')
        self._agencia = "0001"
        self._numero_conta = numero_conta
        self._cliente = cliente
        self._historico = Historico()
    
    @property
    def saldo(self) -> Decimal:
        return self._saldo
    
    @property
    def agencia(self) -> str:
        return self._agencia
    
    @property
    def numero_conta(self) -> int:
        return self._numero_conta
    
    @property
    def cliente(self) -> PessoaFisica:
        return self._cliente
    
    @property
    def historico(self) -> 'Historico':
        return self._historico
        
class ContaCorrente(Conta):
    def __init__(self, numero_conta: int, cliente: PessoaFisica, limite: Decimal = Decimal('1000'), limite_transacoes: int = 10): #teste sem limite e limite_transacoes definido por padrão
        super().__init__(numero_conta, cliente)
        self._limite = limite
        self._limite_transacoes = limite_transacoes

    def _verificar_limite_transacoes(self):
        hoje = datetime.now().strftime("%d-%m-%Y")
        transacoes_hoje = [
            t for t in self.historico.transacoes
            if t["data"].startswith(hoje)
        ]
        return len(transacoes_hoje) >= self._limite_transacoes

    def sacar(self, valor: Decimal) -> bool:
        if self._verificar_limite_transacoes():
            print(f"\n@@@ Operação falhou! Limite de {self._limite_transacoes} transações diárias atingido. @@@")
            return False

        if valor > self._limite:
            print("\n@@@ Operação falhou! O valor excede o limite de R$ {self._limite:.2f} por saque. @@@")
            return False
        
        return super().sacar(valor)
    
    def depositar(self, valor: Decimal) -> bool:
        if self._verificar_limite_transacoes():
            print(f"\n@@@ Operação falhou! Limite de {self._limite_transacoes} transações diárias atingido. @@@")
            return False
        
        return super().depositar(valor)

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
        self._transacoes: List[Dict] = []

    @property
    def transacoes(self) -> List[Dict]:
        return self._transacoes
    
    def adicionar_transacao(self, transacao: 'Transacao') -> None:
        self.transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
        )

    def gerar_relatorio(self, tipo_transacao=None):
        for transacao in self.transacoes:
            if tipo_transacao is None or transacao["tipo"].lower() == tipo_transacao.lower():
                yield transacao

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self) -> Decimal:
        pass

    @abstractmethod
    def registrar(self, conta: Conta) -> bool:
        pass

class Saque(Transacao):
    def __init__(self, valor: Decimal):
        self._valor = valor
    
    @property
    def valor(self) -> Decimal:
        return self._valor
    
    def registrar(self, conta: Conta) -> bool:
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

        return sucesso_transacao    
    
class Deposito(Transacao):
    def __init__(self, valor: Decimal):
        self._valor = valor
    
    @property
    def valor(self) -> Decimal:
        return self._valor
    
    def registrar(self, conta: Conta) -> bool:
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

        return sucesso_transacao
