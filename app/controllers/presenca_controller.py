from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required
from app import db
from app.models import Aluno, Presenca
from datetime import date, datetime
import json

bp = Blueprint('presenca', __name__, url_prefix='/presencas')

@bp.route('/visualizar')
@login_required
def visualizar_presencas():
    data_str = request.args.get('data')
    if data_str:
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida.', 'danger')
            data = date.today()
    else:
        data = date.today()
    
    alunos = Aluno.query.filter_by(tipo='aluno').order_by(Aluno.nome).all()
    presencas = {}
    for aluno in alunos:
        presenca = Presenca.query.filter_by(aluno_id=aluno.id, data=data).first()
        presencas[aluno.id] = presenca if presenca else None
    
    total_alunos = len(alunos)
    registrados = sum(1 for p in presencas.values() if p is not None)
    presentes = sum(1 for p in presencas.values() if p and p.presente)
    faltas = registrados - presentes
    faltas_justificadas = sum(1 for p in presencas.values() if p and not p.presente and p.justificativa)
    
    return render_template('presencas/visualizar.html',
                           alunos=alunos,
                           presencas=presencas,
                           data=data,
                           total_alunos=total_alunos,
                           registrados=registrados,
                           presentes=presentes,
                           faltas=faltas,
                           faltas_justificadas=faltas_justificadas)

@bp.route('/api/presencas')
@login_required
def api_presencas():
    aluno_id = request.args.get('aluno_id')
    ano = int(request.args.get('ano'))
    mes = int(request.args.get('mes'))
    
    query = Presenca.query.filter(
        db.extract('year', Presenca.data) == ano,
        db.extract('month', Presenca.data) == mes
    )
    if aluno_id != 'todos':
        query = query.filter(Presenca.aluno_id == int(aluno_id))
    
    presencas = query.all()
    resultado = {}
    for p in presencas:
        data_str = p.data.strftime('%Y-%m-%d')
        resultado[data_str] = {
            'presente': p.presente,
            'justificativa': p.justificativa,
            'data_registro': p.data_registro.strftime('%d/%m/%Y %H:%M') if p.data_registro else ''
        }
    
    return jsonify(resultado)

@bp.route('/calendario')
@login_required
def calendario():
    alunos = Aluno.query.filter_by(tipo='aluno').order_by(Aluno.nome).all()
    return render_template('presencas/calendario.html', alunos=alunos)

@bp.route('/relatorio_aluno/<int:aluno_id>')
@login_required
def relatorio_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    presencas = Presenca.query.filter_by(aluno_id=aluno_id).order_by(Presenca.data).all()
    
    total = len(presencas)
    presentes = sum(1 for p in presencas if p.presente)
    faltas = sum(1 for p in presencas if not p.presente and not p.justificativa)
    faltas_justificadas = sum(1 for p in presencas if not p.presente and p.justificativa)
    
    percentual_presenca = (presentes / total * 100) if total > 0 else 0
    percentual_faltas = (faltas / total * 100) if total > 0 else 0
    percentual_justificadas = (faltas_justificadas / total * 100) if total > 0 else 0
    
    # Últimos 12 meses para gráfico de linha
    hoje = date.today()
    ultimos_meses = []
    presencas_mensais = []
    for i in range(11, -1, -1):
        mes_calculo = hoje.month - i
        ano_calculo = hoje.year
        if mes_calculo <= 0:
            mes_calculo += 12
            ano_calculo -= 1
        data_inicio = date(ano_calculo, mes_calculo, 1)
        ultimos_meses.append(data_inicio.strftime('%b/%Y'))
        
        presencas_mes = [p for p in presencas if p.data.month == mes_calculo and p.data.year == ano_calculo]
        total_mes = len(presencas_mes)
        presentes_mes = sum(1 for p in presencas_mes if p.presente)
        percentual_mes = (presentes_mes / total_mes * 100) if total_mes > 0 else 0
        presencas_mensais.append(percentual_mes)
    
    return render_template('presencas/relatorio_aluno.html',
                           aluno=aluno,
                           total_aulas=total,
                           presentes=presentes,
                           faltas=faltas,
                           faltas_justificadas=faltas_justificadas,
                           percentual_presenca=percentual_presenca,
                           percentual_faltas=percentual_faltas,
                           percentual_justificadas=percentual_justificadas,
                           ultimos_meses=ultimos_meses,
                           presencas_mensais=presencas_mensais,
                           presencas=presencas)

@bp.route('/relatorios')
@login_required
def relatorios():
    alunos = Aluno.query.filter_by(tipo='aluno').order_by(Aluno.nome).all()
    return render_template('presencas/relatorios.html', alunos=alunos)

# ⬇️⬇️⬇️ NOVA ROTA DO RELATÓRIO PDF (HTML para impressão) ⬇️⬇️⬇️

@bp.route('/relatorio_faltas')
@login_required
def relatorio_faltas():
    """Gera um relatório HTML detalhado de faltas (pronto para imprimir como PDF)"""
    alunos = Aluno.query.filter_by(tipo='aluno').order_by(Aluno.nome).all()
    dados_alunos = []
    total_faltas_geral = 0
    total_justificadas_geral = 0
    total_aulas_geral = 0

    for aluno in alunos:
        presencas = Presenca.query.filter_by(aluno_id=aluno.id).all()
        total_aulas = len(presencas)
        faltas_nao_just = []
        faltas_just = []
        for p in presencas:
            if not p.presente:
                if p.justificativa:
                    faltas_just.append({'data': p.data, 'justificativa': p.justificativa})
                else:
                    faltas_nao_just.append({'data': p.data, 'justificativa': None})
        qtd_faltas = len(faltas_nao_just)
        qtd_justificadas = len(faltas_just)
        percentual_falta = (qtd_faltas / total_aulas * 100) if total_aulas > 0 else 0

        total_faltas_geral += qtd_faltas
        total_justificadas_geral += qtd_justificadas
        total_aulas_geral += total_aulas

        dados_alunos.append({
            'nome': aluno.nome,
            'matricula': aluno.matricula,
            'email': aluno.email,
            'total_aulas': total_aulas,
            'faltas': qtd_faltas,
            'faltas_justificadas': qtd_justificadas,
            'percentual_falta': percentual_falta,
            'lista_faltas': faltas_nao_just,
            'lista_justificadas': faltas_just
        })

    media_faltas_geral = (total_faltas_geral / total_aulas_geral * 100) if total_aulas_geral > 0 else 0

    return render_template(
        'presencas/relatorio_faltas.html',
        hoje=date.today(),
        alunos=dados_alunos,
        total_alunos=len(alunos),
        total_faltas_geral=total_faltas_geral,
        total_justificadas_geral=total_justificadas_geral,
        media_faltas_geral=media_faltas_geral
    )