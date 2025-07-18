from typing import Optional, Dict, Any
from .database import DatabaseManager

class Sessao:
    def __init__(self):
        self._conta_atual: Optional[Dict[str, Any]] = None
        self._cpf_usuario_atual: Optional[Dict[str, Any]] = None

    @property
    def conta_atual(self) -> Optional[Dict[str, Any]]:
        return self._conta_atual
    
    @property
    def cpf_usuario_atual(self) -> Optional[Dict[str, Any]]:
        return self._cpf_usuario_atual
    
    def autenticar(self, cpf: str) -> bool:
        with DatabaseManager as db:
            usuario = db.fetch_one("SELECT * FROM clientes WHERE cpf = ?", (cpf,))
            if not usuario:
                return False
            
            self._cpf_usuario_atual = dict(usuario)
            
    def selecionar_conta(self, cpf):

        with DatabaseManager() as db:
            contas = db.fetch_all("""
                SELECT numero_conta, agencia, saldo 
                FROM contas 
                WHERE cpf = ?
            """, (cpf,))

            if not contas:
                print("\n@@@ Nenhuma conta encontrada para este CPF! @@@")
                return False
            
            print("\n=== SUAS CONTAS ===")
            for i, conta in enumerate(contas, 1):
                print(f"{i} - Ag: {conta['agencia']} | C/C: {conta['numero_conta']} | Saldo: R$ {conta['saldo']:.2f}")

            try:
                opcao = int(input("Selecione o número da conta: ")) - 1
                self.conta_selecionada = contas[opcao]
                self.cpf_usuario = cpf
                return True
            except (ValueError, IndexError):
                print("\n@@@ Conta Inválida! Tente novamente. @@@")
                return False

    def limpar_sesao(self) -> None:
        self._conta_atual = None
        self._cpf_usuario_atual = None    
