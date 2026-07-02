from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime
from model import Session, Livro
from schemas import *
from flask_cors import CORS

info = Info(title="API Estante Virtual", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

home_tag = Tag(
    name="Documentação", description="Documentações: Swagger, Redoc ou RapiDoc"
)
livro_tag = Tag(
    name="Estante de Livros",
    description="Adição, visualização, edição, remoção e visualização de estatísticas dos livros cadastrados na estante virtual.",
)


@app.get("/", tags=[home_tag])
def home():
    """Redireciona para a documentação da API (Swagger)."""
    return redirect("/openapi")


@app.post(
    "/cadastrarlivro",
    tags=[livro_tag],
    summary="Cadastra um novo livro",
    responses={"200": LivroViewSchema, "409": ErrorSchema, "400": ErrorSchema},
)
def add_livro(body: LivroCadastroSchema):
    """Cadastra um novo livro na estante.

    Regras de negócio:
        - O título do livro deve ser único na estante (tentativa de duplicado retorna 409).
        - Se status = 'Estou lendo', recomenda-se informar 'data_inicio' e 'pagina_atual', além de: 'titulo', 'autor', 'genero', 'status' e 'qtde_paginas' (Estrutura base para o livro).
        - Se status = 'Concluído', recomenda-se informar 'data_fim' e 'nota' (de 1 a 5 estrelas), além de: 'titulo', 'autor', 'genero', 'status' e 'qtde_paginas' (Estrutura base para o livro).
        - Se status = 'Quero ler', recomenda-se informar apenas: 'titulo', 'autor', 'genero', 'status' e 'qtde_paginas'.


    Retorna o livro cadastrado, incluindo o ID gerado pelo banco de dados.
    """
    livro = Livro(
        titulo=body.titulo,
        autor=body.autor,
        genero=body.genero,
        qtde_paginas=body.qtde_paginas,
        status=body.status,
        data_inicio=body.data_inicio,
        pagina_atual=body.pagina_atual,
        data_fim=body.data_fim,
        anotacoes=body.anotacoes,
        nota=body.nota,
    )

    try:
        session = Session()
        session.add(livro)
        session.commit()
        return apresenta_livro(livro), 200

    except IntegrityError as e:
        error_msg = "Livro com o mesmo nome já cadastrado na estante :/"
        return {"message": error_msg}, 409
    except Exception as e:
        error_msg = "Não foi possível salvar o novo livro :/"
        return {"message": error_msg}, 400


@app.get(
    "/listarlivros",
    tags=[livro_tag],
    summary="Lista todos os livros cadastrados",
    responses={"200": ListagemLivrosSchema},
)
def get_livros():
    """Retorna a listagem de todos os livros cadastrados na estante.
    Caso não exista nenhum livro cadastrado, retorna uma lista vazia
    com status 200 (não é considerado um erro).
    """
    session = Session()
    livros = session.query(Livro).all()

    if not livros:
        return {"livros": []}, 200
    else:
        return apresenta_livros(livros), 200


@app.patch(
    "/atualizarlivro",
    tags=[livro_tag],
    summary="Atualiza um livro existente",
    responses={"200": LivroViewSchema, "404": ErrorSchema, "400": ErrorSchema},
)
def edit_livro(query: LivroBuscaSchema, body: LivroEdicaoSchema):
    """Atualiza parcialmente o registro de um livro a partir do ID.
    Apenas os campos enviados no corpo da requisição são atualizados
    """
    session = Session()
    """ Busca o registro do livro direto do banco """
    livro = session.query(Livro).filter(Livro.id == query.id).first()

    if not livro:
        return {"message": "Livro não encontrado"}, 404

    try:
        dados = body.model_dump()
        for campo, valor in dados.items():
            if valor in [None, "", "string"]:
                continue

            if campo in ["qtde_paginas", "nota"] and valor == 0:
                continue

            setattr(livro, campo, valor)

        session.add(livro)
        session.commit()
        session.refresh(livro)
        return apresenta_livro(livro), 200

    except Exception as e:
        session.rollback()
        return {"message": "Erro ao atualizar"}, 400


@app.delete(
    "/deletarlivro",
    tags=[livro_tag],
    summary="Remove um livro da estante",
    responses={"200": LivroDeletaSchema, "404": ErrorSchema},
)
def del_livro(query: LivroBuscaSchema):
    """Remove o registro de um livro a partir do ID."""
    livro_id = query.id
    session = Session()
    count = session.query(Livro).filter(Livro.id == livro_id).delete()
    session.commit()

    if count:
        return {
            "message": "Livro removido com sucesso da estante!",
            "id": livro_id,
        }, 200
    else:
        error_msg = "Livro não encontrado na estante :/"
        return {"message": error_msg}, 404


@app.get(
    "/estatisticas/livros-por-status",
    tags=[livro_tag],
    summary="Retorna a quantidade de livros por status",
    responses={"200": EstatisticasSchema},
)
def get_estatisticas_status():
    """Retorna a quantidade de livros cadastrados em cada status de leitura.
    Os rótulos retornados seguem sempre a mesma ordem fixa:
    ['Concluído', 'Estou lendo', 'Quero ler']. Quando não há nenhum
    livro cadastrado, os valores são retornados como 0 (não há erro 404,
    pois a ausência de dados é um cenário válido).
    """

    session = Session()
    concluidos = session.query(Livro).filter(Livro.status == "Concluído").count()
    lendo = session.query(Livro).filter(Livro.status == "Estou lendo").count()
    quero_ler = session.query(Livro).filter(Livro.status == "Quero ler").count()
    return {
        "labels": ["Concluído", "Estou lendo", "Quero ler"],
        "values": [concluidos, lendo, quero_ler],
    }, 200


@app.get(
    "/estatisticas/livros-concluidos-por-mes",
    tags=[livro_tag],
    summary="Retorna a quantidade de livros concluídos por mês",
    responses={"200": EstatisticasSchema},
)
def livros_por_mes():
    """Retorna a quantidade de livros concluídos, agrupados por mês de conclusão.
    Apenas livros com 'data_fim' preenchida são considerados. Os meses são
    retornados no formato 'YYYY-MM', ordenados cronologicamente. Quando não
    há nenhum livro concluído, ambas as listas são retornadas vazias com
    status 200 (não é considerado um erro).
    """
    session = Session()
    livros = session.query(Livro).filter(Livro.data_fim != None).all()
    contagem = {}

    for livro in livros:
        if livro.data_fim:
            mes = livro.data_fim.strftime("%Y-%m")

            if mes in contagem:
                contagem[mes] += 1
            else:
                contagem[mes] = 1

    """ Ordena por mês 
    """
    meses_ordenados = sorted(contagem.keys())

    labels = []
    values = []
    for mes in meses_ordenados:
        labels.append(mes)
        values.append(contagem[mes])
    return {"labels": labels, "values": values}, 200
