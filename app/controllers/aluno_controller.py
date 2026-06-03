from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Aluno, Presenca
from datetime import date, datetime

bp = Blueprint('aluno', __name__, url_prefix='/alunos')

def calcular_estatisticas_aluno(aluno_id):
    """Calcula percentual de presença e faltas consecutivas"""
    presencas = Presenca.query.filter_by(aluno_id=aluno_id).order_by(Presenca.data.desc()).all()
    total = len(presencas)
    presentes = sum(1 for p in presencas if p.presente)
    percentual = (presentes / total * 100) if total > 0 else 0
    
    faltas_consecutivas = 0
    for p in presencas:
        if not p.presente and not p.justificativa:
            faltas_consecutivas += 1
        else:
            break
    
    return percentual, total, faltas_consecutivas

def calcular_faltas_consecutivas(aluno_id):
    """Calcula apenas faltas consecutivas"""
    presencas = Presenca.query.filter_by(aluno_id=aluno_id).order_by(Presenca.data.desc()).all()
    faltas = 0
    for p in presencas:
        if not p.presente and not p.justificativa:
            faltas += 1
        else:
            break
    return faltas

@bp.route('/')
@login_required
def listar_alunos():
    """Lista todos os alunos (exceto administradores)"""
    alunos = Aluno.query.filter_by(tipo='aluno').order_by(Aluno.nome).all()
    hoje = date.today()
    
    presencas_hoje = {}
    for aluno in alunos:
        presenca = Presenca.query.filter_by(aluno_id=aluno.id, data=hoje).first()
        presencas_hoje[aluno.id] = presenca if presenca else None
    
    return render_template('alunos/listar.html', 
                         alunos=alunos, 
                         hoje=hoje,
                         presencas_hoje=presencas_hoje)

@bp.route('/presenca-rapida/<int:id>/<string:status>', methods=['POST'])
@login_required
def presenca_rapida(id, status):
    """Registra presença rápida: presente, falta, ou presente com atestado"""
    
    aluno = Aluno.query.get_or_404(id)
    hoje = date.today()
    registro = Presenca.query.filter_by(aluno_id=id, data=hoje).first()
    
    if status == 'presente':
        presente = True
        justificativa = None
        mensagem = f'Presença registrada para {aluno.nome}'
    elif status == 'falta':
        presente = False
        justificativa = None
        mensagem = f'Falta registrada para {aluno.nome}'
    elif status == 'atestado':
        presente = False
        justificativa = 'Falta justificada com atestado médico'
        mensagem = f'Falta com atestado registrada para {aluno.nome}'
    else:
        flash('Status inválido.', 'danger')
        return redirect(url_for('aluno.listar_alunos'))
    
    if registro:
        registro.presente = presente
        registro.justificativa = justificativa
        flash(f'{mensagem} (registro atualizado)', 'success')
    else:
        novo_registro = Presenca(
            aluno_id=id,
            data=hoje,
            presente=presente,
            justificativa=justificativa
        )
        db.session.add(novo_registro)
        flash(mensagem, 'success')
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar: {str(e)}', 'danger')
    
    return redirect(url_for('aluno.listar_alunos'))

@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def cadastrar_aluno():
    """Cadastra um novo aluno - apenas nome é necessário. Email e senha são gerados automaticamente."""
    
    def gerar_matricula():
        from datetime import datetime
        ano = datetime.now().year
        ultimo_aluno = Aluno.query.order_by(Aluno.id.desc()).first()
        if ultimo_aluno and ultimo_aluno.matricula:
            try:
                sequencial = int(ultimo_aluno.matricula[-4:]) + 1
            except (ValueError, IndexError):
                sequencial = 1
        else:
            sequencial = 1
        return f"{ano}{sequencial:04d}"
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        
        if not nome:
            flash('Nome é obrigatório.', 'danger')
            return render_template('alunos/cadastrar.html')
        
        # Gera tudo automaticamente
        matricula = gerar_matricula()
        email = f"{nome.lower().replace(' ', '')}@aluno.com"
        senha = "123456"
        
        # Verifica se matrícula já existe (segurança)
        if Aluno.query.filter_by(matricula=matricula).first():
            flash('Erro ao gerar matrícula. Tente novamente.', 'danger')
            return render_template('alunos/cadastrar.html')
        
        novo_aluno = Aluno(
            nome=nome,
            email=email,
            matricula=matricula,
            senha=senha
        )
        novo_aluno.tipo = 'aluno'
        
        try:
            db.session.add(novo_aluno)
            db.session.commit()
            flash(f'Aluno {nome} cadastrado com sucesso! Matrícula: {matricula}', 'success')
            return redirect(url_for('aluno.listar_alunos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
    
    return render_template('alunos/cadastrar.html')

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_aluno(id):
    """Edita os dados de um aluno"""
    
    aluno = Aluno.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        matricula = request.form.get('matricula')
        
        if not all([nome, email, matricula]):
            flash('Nome, e-mail e matrícula são obrigatórios.', 'danger')
            return render_template('alunos/editar.html', aluno=aluno)
        
        if matricula != aluno.matricula:
            if Aluno.query.filter_by(matricula=matricula).first():
                flash('Matrícula já cadastrada por outro aluno.', 'danger')
                return render_template('alunos/editar.html', aluno=aluno)
        
        if email != aluno.email:
            if Aluno.query.filter_by(email=email).first():
                flash('E-mail já cadastrado por outro aluno.', 'danger')
                return render_template('alunos/editar.html', aluno=aluno)
        
        aluno.nome = nome
        aluno.email = email
        aluno.matricula = matricula
        
        nova_senha = request.form.get('nova_senha')
        if nova_senha:
            if len(nova_senha) < 6:
                flash('A nova senha deve ter pelo menos 6 caracteres.', 'danger')
                return render_template('alunos/editar.html', aluno=aluno)
            aluno.senha = nova_senha
            flash('Senha atualizada com sucesso!', 'success')
        
        try:
            db.session.commit()
            flash(f'Dados de {aluno.nome} atualizados com sucesso!', 'success')
            return redirect(url_for('aluno.listar_alunos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {str(e)}', 'danger')
    
    return render_template('alunos/editar.html', aluno=aluno)

@bp.route('/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_aluno(id):
    """Exclui um aluno e todas as suas presenças"""
    
    aluno = Aluno.query.get_or_404(id)
    nome_aluno = aluno.nome
    
    try:
        db.session.delete(aluno)
        db.session.commit()
        flash(f'Aluno {nome_aluno} excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir: {str(e)}', 'danger')
    
    return redirect(url_for('aluno.listar_alunos'))

@bp.route('/<int:id>/historico')
@login_required
def historico_aluno(id):
    """Visualiza o histórico de presenças de um aluno"""
    
    aluno = Aluno.query.get_or_404(id)
    presencas = Presenca.query.filter_by(aluno_id=id).order_by(Presenca.data.desc()).all()
    
    total_aulas = len(presencas)
    presencas_count = sum(1 for p in presencas if p.presente)
    faltas_count = total_aulas - presencas_count
    faltas_justificadas = sum(1 for p in presencas if not p.presente and p.justificativa)
    percentual = (presencas_count / total_aulas * 100) if total_aulas > 0 else 0
    
    return render_template('alunos/historico.html', 
                         aluno=aluno, 
                         presencas=presencas,
                         total_aulas=total_aulas,
                         presencas_count=presencas_count,
                         faltas_count=faltas_count,
                         faltas_justificadas=faltas_justificadas,
                         percentual=percentual)

# Funções auxiliares para os templates
@bp.app_context_processor
def utility_processor():
    return {
        'calcular_estatisticas_aluno': calcular_estatisticas_aluno,
        'calcular_faltas_consecutivas': calcular_faltas_consecutivas
    }