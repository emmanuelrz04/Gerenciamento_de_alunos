# Sistema de Controle de Presença Escolar - Espaço Saber

**Status do Projeto:** Em Produção | **Última Atualização:** Maio/2026

---

## O Problema

Uma professora de reforço escolar perdia em média 15 minutos de cada aula realizando chamada manual e registrando faltas em planilhas desconectadas. O cálculo de frequência era feito manualmente, não havia registro histórico confiável e o controle de faltas consecutivas era impreciso.

Tempo total perdido por ano: aproximadamente 48 horas apenas com tarefas administrativas.

## A Solução

Sistema web que reduz o tempo de registro de presença para menos de 2 minutos diários, com relatórios automáticos e alertas inteligentes.

**Tecnologias utilizadas:**
- Python 3.14
- Flask 3.x
- SQLite com SQLAlchemy
- Jinja2 Templates
- Bootstrap 5
- Chart.js
- Bcrypt
---

## Principais Funcionalidades

### Para o Professor

- Painel centralizado com lista de alunos e status do dia atual
- Registro de presença com 3 opções: Presente, Falta e Falta com Atestado
- Botões de ação em massa (Todos Presentes / Todos Falta)
- Alerta automático para alunos com 3 ou mais faltas consecutivas

### Relatórios e Estatísticas

- Cálculo automático de percentual de presença por aluno
- Relatório individual com gráfico de pizza (Chart.js)
- Calendário interativo de presenças por mês
- Relatório de faltas pronto para impressão (PDF via navegador)

### Segurança

- Hash de senhas com bcrypt
- Proteção CSRF em todos os formulários
- Proteção contra SQL Injection (SQLAlchemy)
- Proteção contra XSS (Jinja2 autoescape)

---

## Arquitetura

O projeto segue o padrão Model-View-Controller com estrutura modular:

`Controllers:` Gerenciam as rotas HTTP e a lógica de requisição
`Models:` Mapeamento das entidades Aluno e Presenca
`Templates:` Renderização das páginas com Jinja2
`Static:` Arquivos CSS e JavaScript

### Diagrama de Fluxo de Dados

Usuário requisita página → Controller processa → Service aplica regras → Repository consulta banco → View renderiza resposta HTML

---

## Benefícios Entregues

| Métrica | Antes | Depois |
|---------|-------|--------|
| Tempo de chamada | 15 minutos | 2 minutos |
| Economia diária | - | 13 minutos |
| Economia mensal | - | 4 horas |
| Economia anual | - | 48 horas |

**Diferenciais competitivos:**

-  Zero dependência de internet (funciona localmente)
-  Banco de dados leve (SQLite) com backup facilitado
-  Interface intuitiva projetada para uso diário
-  Relatórios profissionais gerados em segundos

---
# Screenshots

## Interface do Sistema

Abaixo estão as principais telas e funcionalidades do sistema:

### 1. Index do sistema
Página inicial do site

![Tela de Login](https://github.com/emmanuelrz04/Gerenciamento_de_alunos/blob/main/Screenshots/SC1.png?raw=true)

### 2. Sistema de loguin
Acesso seguro com matrícula e senha.
![Tela de Login](https://github.com/emmanuelrz04/Gerenciamento_de_alunos/blob/main/Screenshots/SC2.png?raw=true)

### 3. Gerenciamento de faltas ao longo do mês
![Tela de Login](https://github.com/emmanuelrz04/Gerenciamento_de_alunos/blob/main/Screenshots/SC3.png?raw=true)

### 4. Lista de Alunos (Demais imagens)
- Registro de presença (Presente, Falta, Atestado)
- Relatório individual com gráfico
- Calendário de presenças
- Relatório de faltas para impressão
![Tela de Login](https://github.com/emmanuelrz04/Gerenciamento_de_alunos/blob/main/Screenshots/SC4.png?raw=true)

---

## Como Executar o Projeto

### Pré-requisitos
- Python 3.8 ou superior instalado
- Git (opcional, para clonar)

### Passos para rodar localmente

`git clone https://github.com/emmanuelrz04/Gerenciamento_de_alunos.git`

`cd Gerenciamento_de_alunos`

`python -m venv venv`

`venv\Scripts\activate` no Windows ou `source venv/bin/activate` no Linux/Mac

`pip install -r requirements.txt`

`python run.py`

Acesse `http://localhost:5000` no navegador

### Credenciais de Acesso
| Campo | Valor |
|-------|-------|
| Matrícula | PROF001 |
| Senha | admin123 |

---

## Estrutura do Projeto

`app/`
  `controllers/` - Rotas da aplicação
  `models/` - Classes do banco de dados
  `templates/` - Páginas HTML
  `static/` - CSS e JavaScript
`instance/` - Banco de dados SQLite
`migrations/` - Controle de versão do schema
`run.py` - Ponto de entrada da aplicação
`config.py` - Configurações e variáveis de ambiente
`requirements.txt` - Dependências do projeto

---

## Melhorias Futuras

- Exportar relatórios em formato Excel
- Dashboard com gráficos da turma completa
- Envio de notificações por e-mail para responsáveis
- Versão mobile (PWA)
- API REST para integração com outros sistemas

---

## Autor

**Emmanuel Ricardo**  
GitHub: [emmanuelrz04](https://github.com/emmanuelrz04)

---

## Licença

Este projeto está sob a licença MIT. Consulte o arquivo LICENSE para mais informações.

---

*Sistema desenvolvido para otimizar a rotina de professores de reforço escolar, com foco em usabilidade e eficiência.*
