import csv
from .models import Pessoa_fisica, ContaCorrente
from .utils import DADOS_PATH

def carregar_dados_separados(usuarios_arquivo="usuarios.csv", contas_arquivo="contas.csv"):
    usuarios = []
    contas = []
    usuarios_por_cpf = {}

    # Carregar usuários
    try:
        with open(DADOS_PATH / usuarios_arquivo, mode="r", newline='', encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                usuario = Pessoa_fisica(
                    nome=linha["nome"],
                    cpf=linha["cpf"],
                    data_nascimento=linha["data_nascimento"],
                    endereco=linha["endereco"]
                )
                usuarios.append(usuario)
                usuarios_por_cpf[usuario.cpf] = usuario
    except FileNotFoundError:
        print("Arquivo de usuários não encontrado. Continuando com lista vazia.")

    # Carregar contas e associar aos usuários
    try:
        with open(DADOS_PATH / contas_arquivo, mode="r", newline='', encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                cpf = linha["cpf"]
                usuario = usuarios_por_cpf.get(cpf)
                if usuario:
                    conta = ContaCorrente(
                        numero_conta=linha["numero_conta"],
                        usuario=usuario
                    )
                    contas.append(conta)
                    usuario.adicionar_conta(conta)
                else:
                    print(f"CPF {cpf} da conta {linha['numero_conta']} não encontrado entre os usuários.")
    except FileNotFoundError:
        print("Arquivo de contas não encontrado. Continuando com lista vazia.")

    return usuarios, contas

    
def salvar_usuarios_csv(usuarios, nome_arquivo="usuarios.csv"):
    colunas = ["cpf", "nome", "endereco", "data_nascimento"]

    try:
        with open(DADOS_PATH / nome_arquivo, mode="w", newline='', encoding="utf-8") as arquivo_csv:
            escritor = csv.DictWriter(arquivo_csv, fieldnames=colunas)
            escritor.writeheader()
            for usuario in usuarios:
                escritor.writerow({
                    "cpf": usuario.cpf,
                    "nome": usuario.nome,
                    "endereco": usuario.endereco,
                    "data_nascimento": usuario.data_nascimento
                })
        print(f"Usuários salvos em {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar usuários: {e}")

def salvar_contas_csv(contas, nome_arquivo="contas.csv"):
    colunas = ["agencia", "numero_conta", "cpf"]

    try:
        with open(DADOS_PATH / nome_arquivo, mode="w", newline='', encoding="utf-8") as arquivo_csv:
            escritor = csv.DictWriter(arquivo_csv, fieldnames=colunas)
            escritor.writeheader()
            for conta in contas:
                escritor.writerow({
                    "agencia": conta.agencia,
                    "numero_conta": conta.numero_conta,
                    "cpf": conta.usuario.cpf
                })
        print(f"Contas salvas em {nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar contas: {e}")