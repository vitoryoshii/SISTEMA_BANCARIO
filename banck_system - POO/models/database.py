import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = "bank_system.db"):
        self.db_path = Path(__file__).parent.parent / "data" / db_path
        self.connection: Optional[sqlite3.Connection] = None
        self._in_context = False
    
    def __enter__(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON")
            self._in_context = True
            return self
        except sqlite3.Error as e:
            raise RuntimeError(f"Falha ao conectar ao banco de dados: {str(e)}")
        
    def __exit__(self, exc_type, exc_value, exc_tb):
        self._in_context = False
        if self.connection:
            try:
                if exc_type is not None:
                    self.connection.rollback()
                self.connection.close()
            except sqlite3.Error as e:
                raise RuntimeError(f"Erro ao fechar conexão: {str(e)}")
            finally: 
                self.connection = None

    def _check_connection(self):
        if not self.connection or not self._in_context:
            raise RuntimeError("Conexão com o banco de dados não está disponível ou já foi fechada")

    def executar_query(self, query: str, parameters: tuple = None) -> sqlite3.Cursor:
        self._check_connection()

        try:
            cursor = self.connection.cursor()
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Erro ao executar query: {str(e)}")
    
    def executar_querys(self, querys: str):
        self._check_connection()

        try:
            cursor = self.connection.cursor()
            cursor.executescript(querys)
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Erro ao executar query: {str(e)}")

    def fetch_one(self, query: str, parameters: tuple = None) -> Optional[Dict[str, Any]]:
        self._check_connection()
        cursor = None
        try:
            cursor = self.executar_query(query, parameters)
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            if cursor is not None:
                cursor.close()
        
    def fetch_all(self, query: str, parameters: tuple = None) -> List[Dict[str, Any]]:
        self._check_connection()
        cursor = None
        try:
            cursor = self.executar_query(query, parameters)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            if cursor is not None:
                cursor.close()