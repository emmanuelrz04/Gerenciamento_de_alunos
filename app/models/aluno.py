from app import db
from flask_login import UserMixin
from datetime import datetime
import bcrypt

class Aluno(db.Model, UserMixin):
    """Modelo para representar um aluno no sistema"""
    
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    tipo = db.Column(db.String(20), nullable=False, default='aluno')
    
    # Relacionamento: um aluno tem muitos registros de presença
    presencas = db.relationship('Presenca', backref='aluno', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, nome, email, matricula, senha):
        self.nome = nome
        self.email = email
        self.matricula = matricula
        self.senha = senha
    
    @property
    def senha(self):
        raise AttributeError('Senha não é um atributo legível')
    
    @senha.setter
    def senha(self, senha_plana):
        self.senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verificar_senha(self, senha_plana):
        return bcrypt.checkpw(senha_plana.encode('utf-8'), self.senha_hash.encode('utf-8'))
    
    def __repr__(self):
        return f'<Aluno {self.nome} - {self.matricula}>'

