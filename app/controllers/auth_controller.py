from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Aluno
from werkzeug.security import check_password_hash

# Cria um blueprint para organizar as rotas de autenticação
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para login do usuário"""
    
    # Se o usuário já está logado, redireciona para a página inicial
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Obtém os dados do formulário
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')
        
        # Validação básica
        if not matricula or not senha:
            flash('Por favor, preencha matrícula e senha.', 'danger')
            return render_template('auth/login.html')
        
        # Busca o aluno pela matrícula
        aluno = Aluno.query.filter_by(matricula=matricula).first()
        
        # Verifica se o aluno existe e a senha está correta
        if aluno and aluno.verificar_senha(senha):
            # Realiza o login
            login_user(aluno)
            flash(f'Bem-vindo, {aluno.nome}!', 'success')
            
            # Redireciona para a página que o usuário tentou acessar ou página inicial
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Matrícula ou senha inválidos.', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Rota para logout do usuário"""
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('index'))

@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Rota para registro de novos usuários"""
    
    # Se o usuário já está logado, redireciona
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Obtém dados do formulário
        nome = request.form.get('nome')
        email = request.form.get('email')
        matricula = request.form.get('matricula')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        
        # Validações
        if not all([nome, email, matricula, senha]):
            flash('Todos os campos são obrigatórios.', 'danger')
            return render_template('auth/registro.html')
        
        if senha != confirmar_senha:
            flash('As senhas não conferem.', 'danger')
            return render_template('auth/registro.html')
        
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('auth/registro.html')
        
        # Verifica se matrícula já existe
        if Aluno.query.filter_by(matricula=matricula).first():
            flash('Matrícula já cadastrada.', 'danger')
            return render_template('auth/registro.html')
        
        # Verifica se email já existe
        if Aluno.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'danger')
            return render_template('auth/registro.html')
        
        # Cria novo aluno (o hash da senha é feito automaticamente pelo model)
        novo_aluno = Aluno(
            nome=nome,
            email=email,
            matricula=matricula,
            senha=senha
        )
        
        try:
            db.session.add(novo_aluno)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar: {str(e)}', 'danger')
            return render_template('auth/registro.html')
    
    return render_template('auth/registro.html')