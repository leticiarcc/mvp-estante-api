# Título: Estante Virtual

Backend da aplicação **Estante Virtual**, desenvolvido para a disciplina *Desenvolvimento Full Stack Básico*. Esta API é responsável por toda a regra de negócio e persistência dos livros cadastrados pelo usuário, oferecendo rotas para **cadastro, listagem, edição, remoção** e **estatísticas** de leitura (livros por status e por mês de conclusão).

A documentação interativa da API é gerada automaticamente via **Swagger (OpenAPI)**.

---

## Tecnologias utilizadas

- **Python**
- **Flask** — framework web
- **flask-openapi3** — geração automática de documentação Swagger
- **SQLAlchemy** — ORM para manipulação do banco de dados
- **SQLite** — banco de dados
- **Pydantic** — validação e tipagem de dados das requisições
- **Flask-CORS** — liberação de requisições de origens externas (necessário para o frontend funcionar mesmo aberto diretamente como arquivo local)

---

## Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

- [Python](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/) (geralmente já vem junto com o Python)
- Um editor de código de sua preferência (ex: VS Code)
- *(Opcional)* Uma extensão ou software para visualizar o banco SQLite gerado (ex: extensão **SQLite Viewer** no VS Code, ou o **DB Browser for SQLite**)

---

## Instalação e configuração do ambiente

### 1. Clone o repositório ou realize o download do arquivo zip no repositório.

### 2. Crie um ambiente virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> Quando o ambiente virtual estiver ativo, o terminal exibirá `(venv)` no início da linha.

### 3. Instale as dependências

Com o ambiente virtual ativado, instale todas as bibliotecas necessárias listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Dependências do projeto:**

| Biblioteca | Versão |
|---|---|
| Flask | 3.0.3 |
| Flask-Cors | 4.0.1 |
| flask-openapi3[swagger] | 3.1.2 |
| pydantic | 2.7.1 |
| SQLAlchemy | 2.0.30 |
| SQLAlchemy-Utils | 0.41.2 |

### 4. Banco de dados

O banco de dados **SQLite** é criado automaticamente na primeira execução da aplicação — não é necessário nenhum passo manual de criação de tabelas.

---

## Como executar o projeto

Com o ambiente virtual ativado e as dependências instaladas, inicie o servidor Flask com o comando:

```bash
flask run --host 0.0.0.0 --port 5000
```
O servidor rodará em: http://localhost:5000
```
---

## Documentação da API (Swagger)

Após iniciar o servidor, acesse a documentação da API em:

```
http://localhost:5000/openapi

```

Nela é possível visualizar todas as rotas disponíveis, os métodos HTTP, os parâmetros esperados, os formatos de requisição/resposta e os possíveis códigos de status, além de poder testar cada rota diretamente pelo navegador.

### Resumo das rotas da estante: 

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Redireciona para a documentação Swagger |
| `POST` | `/cadastrarlivro` | Cadastra um novo livro na estante |
| `GET` | `/listarlivros` | Lista todos os livros cadastrados |
| `PATCH` | `/atualizarlivro?id={id}` | Atualiza parcialmente um livro existente |
| `DELETE` | `/deletarlivro?id={id}` | Remove um livro da estante |
| `GET` | `/estatisticas/livros-por-status` | Retorna a quantidade de livros por status de leitura |
| `GET` | `/estatisticas/livros-concluidos-por-mes` | Retorna a quantidade de livros concluídos, agrupados por mês |

---

```
## Estrutura do projeto

├── model/
│   ├── __init__.py     # Inicialização do pacote e configuração da sessão/engine
│   ├── base.py        # Configuração base do SQLAlchemy (Base declarativa)
│   └── livro.py       # Definição da tabela/modelo Livro
├── schemas/
│   ├── __init__.py     # Inicialização do pacote de schemas
│   ├── error.py       # Schema padrão de retorno de erros
│   └── livro.py       # Schemas de validação e serialização do Livro (Pydantic)
├── app.py            # Rotas da API e regras de negócio
├── requirements.txt      # Dependências do projeto
└── README.md           # Este arquivo

```
```
---
