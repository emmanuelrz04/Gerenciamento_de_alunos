from app import db
from datetime import date, datetime

class Presenca(db.Model):
    """Modelo para registrar presença/falta dos alunos"""
    
    __tablename__ = 'presencas'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    presente = db.Column(db.Boolean, nullable=False, default=True)
    justificativa = db.Column(db.Text, nullable=True)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índices compostos para otimizar buscas
    __table_args__ = (
        db.UniqueConstraint('aluno_id', 'data', name='unique_presenca_dia'),
    )
    
    def __repr__(self):
        status = "Presente" if self.presente else "Falta"
        return f'<Presenca {self.aluno_id} - {self.data} - {status}>'