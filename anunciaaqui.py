from flask_bcrypt import Bcrypt
from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html', titulo="Menu Principal")

@app.route("/cadastro/usuario")
def usuario():
    return render_template('usuario.html', titulo="Cadastro de Usuário")

@app.route("/cadastro/anuncio")
def anuncio():
    return render_template('anuncio.html' , titulo="Cadastro de Anúncio")

@app.route("/anuncios/pergunta")
def pergunta():
    return render_template('pergunta.html', titulo="Perguntas Frequentes")

@app.route("/anuncios/compra")
def compra():
    print("anuncio comprado")
    return render_template('compra.html', titulo="Compras")

@app.route("/anuncios/favoritos")
def favoritos():
    print("favorito inserido")
    return render_template('favoritos.html' , titulo="Favoritos")

@app.route("/relatorios/vendas")
def relVendas():
    return render_template('relVendas.html' , titulo="Relatório de Vendas")

@app.route("/relatorios/compras")
def relCompras():
    return render_template('relCompras.html' , titulo="Relatório de Compras")