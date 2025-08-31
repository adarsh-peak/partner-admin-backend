from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from src.configs.env import get_settings

settings = get_settings()


class Database:
    def __init__(self):
        self.DATABASE_URL = (
    "mssql+pyodbc://SA:reallyStrongPwd123@127.0.0.1:1433/SeqData"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&Encrypt=no"
    "&TrustServerCertificate=yes"
)


        self.engine = create_engine(
            self.DATABASE_URL,
            echo=True,
            future=True
        )

        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
        )

    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def call_procedure(self, procedure_name: str, params: dict = None):
        """
        Call a stored procedure with named parameters.

        :param procedure_name: Name of the stored procedure
        :param params: Dictionary of parameter_name: value
        :return: List of dictionaries, each representing a row
        """
        params = params or {}

        with self.get_session() as session:
            # Build placeholders for named parameters
            if params:
                placeholders = ", ".join([f":{k}" for k in params.keys()])
            else:
                placeholders = ""

            sql = text(f"EXEC {procedure_name} {placeholders}")
            result = session.execute(sql, params)
            
            # Convert each row to a dictionary keyed by column name
            rows = result.mappings().all()
            dict_rows = [dict(row) for row in rows]
            return dict_rows
        
    def execute_query(self, query: str, params: dict = None):
        """
        Execute a raw SQL query with optional parameters and return results as a list of dictionaries.

        :param query: The raw SQL query
        :param params: Dictionary of parameter_name: value
        :return: List of dictionaries, each representing a row
        """
        params = params or {}

        with self.get_session() as session:
            sql = text(query)
            result = session.execute(sql, params)
            # Convert result to list of dictionaries
            rows = result.mappings().all()
            dict_rows = [dict(row) for row in rows]
            return dict_rows

db_session = Database()
