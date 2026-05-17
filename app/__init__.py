from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

# Inicializa extensões
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    # Cria a instância do Flask
    app = Flask(__name__)
    
    # Carrega configurações
    app.config.from_object(config_class)
    
    # Inicializa extensões com a aplicação
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configuração do Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    # IMPORTANTE: Importa os models para que o SQLAlchemy os conheça
    from app.models import Aluno, Presenca
    
    # Função do Flask-Login para carregar um usuário pelo ID
    @login_manager.user_loader
    def load_user(user_id):
        return Aluno.query.get(int(user_id))
    
    # Importa e registra os blueprints
    from app.controllers import aluno_controller, presenca_controller, auth_controller
    app.register_blueprint(aluno_controller.bp)
    app.register_blueprint(presenca_controller.bp)
    app.register_blueprint(auth_controller.bp)
    
    # Rota principal
    @app.route('/')
    def index():
        return render_template('index.html')
    

    # Adiciona a data atual para todos os templates
    @app.context_processor
    def inject_now():
        from datetime import date
        return {'hoje': date.today()}
    return app