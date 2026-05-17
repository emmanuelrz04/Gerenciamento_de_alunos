from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Aluno, Presenca
from datetime import date, datetime

# Cria um blueprint para rotas de alunos
bp = Blueprint('aluno', __name__, url_prefix='/alunos')

def calcular_estatisticas_aluno(aluno_id):
    """Calcula percentual de presença e faltas consecutivas"""
    from app.models import Presenca
    
    presencas = Presenca.query.filter_by(aluno_id=aluno_id).order_by(Presenca.data.desc()).all()
    total = len(presencas)
    presentes = sum(1 for p in presencas if p.presente)
    percentual = (presentes / total * 100) if total > 0 else 0
    
    # Calcular faltas consecutivas (das mais recentes para as mais antigas)
    faltas_consecutivas = 0
    for p in presencas:
        if not p.presente and not p.justificativa:
            faltas_consecutivas += 1
        else:
            break
    
    return percentual, total, faltas_consecutivas

def calcular_faltas_consecutivas(aluno_id):
    """Calcula apenas faltas consecutivas"""
    from app.models import Presenca
    
    presencas = Presenca.query.filter_by(aluno_id=aluno_id).order_by(Presenca.data.desc()).all()
    faltas = 0
    for p in presencas:
        if not p.presente and not p.justificativa:
            faltas += 1
        else:
            break
    return faltas

def calcular_estatisticas_aluno(aluno_id):
    """Calcula percentual de presença e faltas consecutivas"""
    from app.models import Presenca
    from datetime import date, timedelta
    
    presencas = Presenca.query.filter_by(aluno_id=aluno_id).order_by(Presenca.data.desc()).all()
    total = len(presencas)
    presentes = sum(1 for p in presencas if p.presente)
    percentual = (presentes / total * 100) if total > 0 else 0
    
    # Calcular faltas consecutivas
    faltas_consecutivas = 0
    for p in presencas:
        if not p.presente and not p.justificativa:
            faltas_consecutivas += 1
        else:
            break
    
    return percentual, total, faltas_consecutivas

def calcular_faltas_consecutivas(aluno_id):
    """Calcula apenas faltas consecutivas"""
    from app.models import Presenca
    
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
    # Mostra apenas alunos com tipo 'aluno' (não admin)
    alunos = Aluno.query.filter_by(tipo='aluno').order_by(Aluno.nome).all()
    hoje = date.today()
    
    # Busca presenças de hoje para cada aluno
    presencas_hoje = {}
    for aluno in alunos:
        presenca = Presenca.query.filter_by(aluno_id=aluno.id, data=hoje).first()
        if presenca:
            presencas_hoje[aluno.id] = presenca
        else:
            presencas_hoje[aluno.id] = None
    
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
    
    # Busca se já existe registro para hoje
    registro = Presenca.query.filter_by(aluno_id=id, data=hoje).first()
    
    # Define o status baseado no parâmetro
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
        # Atualiza registro existente
        registro.presente = presente
        registro.justificativa = justificativa
        flash(f'{mensagem} (registro atualizado)', 'success')
    else:
        # Cria novo registro
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
    """Cadastra um novo aluno"""
    
    if request.method == 'POST':
        # Obtém dados do formulário
        nome = request.form.get('nome')
        email = request.form.get('email')
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')
        
        # Validações
        if not all([nome, email, matricula, senha]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('alunos/cadastrar.html')
        
        # Verifica se matrícula já existe
        if Aluno.query.filter_by(matricula=matricula).first():
            flash('Matrícula já cadastrada.', 'danger')
            return render_template('alunos/cadastrar.html')
        
        # Verifica se email já existe
        if Aluno.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'danger')
            return render_template('alunos/cadastrar.html')
        
        # Cria novo aluno
        novo_aluno = Aluno(
            nome=nome,
            email=email,
            matricula=matricula,
            senha=senha
        )
        
        try:
            db.session.add(novo_aluno)
            db.session.commit()
            flash(f'Aluno {nome} cadastrado com sucesso!', 'success')
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
        # Obtém dados do formulário
        nome = request.form.get('nome')
        email = request.form.get('email')
        matricula = request.form.get('matricula')
        
        # Validações
        if not all([nome, email, matricula]):
            flash('Nome, e-mail e matrícula são obrigatórios.', 'danger')
            return render_template('alunos/editar.html', aluno=aluno)
        
        # Verifica se nova matrícula já existe (e não é a mesma)
        if matricula != aluno.matricula:
            if Aluno.query.filter_by(matricula=matricula).first():
                flash('Matrícula já cadastrada por outro aluno.', 'danger')
                return render_template('alunos/editar.html', aluno=aluno)
        
        # Verifica se novo email já existe (e não é o mesmo)
        if email != aluno.email:
            if Aluno.query.filter_by(email=email).first():
                flash('E-mail já cadastrado por outro aluno.', 'danger')
                return render_template('alunos/editar.html', aluno=aluno)
        
        # Atualiza dados
        aluno.nome = nome
        aluno.email = email
        aluno.matricula = matricula
        
        # Se uma nova senha foi fornecida, atualiza
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
    
    # Busca presenças ordenadas por data (mais recentes primeiro)
    presencas = Presenca.query.filter_by(aluno_id=id)\
        .order_by(Presenca.data.desc()).all()
    
    # Calcula estatísticas
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

# Registrar funções auxiliares para os templates
from flask import current_app

@bp.app_context_processor
def utility_processor():
    return {
        'calcular_estatisticas_aluno': calcular_estatisticas_aluno,
        'calcular_faltas_consecutivas': calcular_faltas_consecutivas
    }