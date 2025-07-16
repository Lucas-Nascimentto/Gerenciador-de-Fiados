import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()  # carrega as variáveis do .env para o ambiente

def get_connection():
    conn_str = os.getenv("DATABASE_URL")
    return psycopg2.connect(conn_str, sslmode='require')