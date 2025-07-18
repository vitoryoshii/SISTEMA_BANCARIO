from models.database import DatabaseManager
from pathlib import Path

PASTA_RAIZ = Path(__file__).resolve().parent.parent

def criar_banco():
    with DatabaseManager() as db:
        with open(PASTA_RAIZ / 'config' / 'schema.sql', 'r') as f:
            schema = f.read()
        db.executar_querys(schema)
        print("Banco de dados inicializado com sucesso!")

if __name__ == "__main__":
    criar_banco()