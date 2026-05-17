import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

class Config:
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Configuração do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de sessão
    SESSION_COOKIE_SECURE = False  # Mude para True em produção (HTTPS)
    SESSION_COOKIE_HTTPONLY = True  # Impede acesso ao cookie via JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protege contra CSRF
    
    # Configurações de segurança
    WTF_CSRF_ENABLED = True  # Ativa proteção CSRF
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-dev-key'