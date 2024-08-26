from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
from flask_login import current_user, LoginManager, login_user, logout_user, login_required, UserMixin
from flask_login import UserMixin


app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:JPontes062730@localhost:3306/anunciaaqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://juliapontes:JPontes062730@juliapontes.mysql.pythonanywhere-services.com:3306/juliapontes$anunciaaqui'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = '123456'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"
    id = db.Column('usuario_id', db.Integer, primary_key=True)
    nome = db.Column('usuario_nome', db.String(256), nullable=False)
    email = db.Column('usuario_email', db.String(256), unique=True, nullable=False)
    senha = db.Column('usuario_senha', db.String(256), nullable=False)
    tipousuario = db.Column('usuario_tipo', db.String(50), nullable=False)

    def __init__(self, nome, email, senha, tipousuario):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipousuario = tipousuario

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anuncio_id', db.Integer, primary_key=True)
    titulo = db.Column('anuncio_titulo', db.String(256))
    descricao = db.Column('anuncio_descricao', db.String(256))
    preco = db.Column('anuncio_preco', db.Float)
    categoria_id = db.Column('categoria_id', db.Integer, db.ForeignKey("categoria.categoria_id"))
    usuario_id = db.Column('usuario_id', db.Integer, db.ForeignKey("usuario.usuario_id"))

    def __init__(self, titulo, descricao, preco, categoria_id, usuario_id):
        self.titulo = titulo
        self.descricao = descricao
        self.preco = preco
        self.categoria_id = categoria_id
        self.usuario_id = usuario_id

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('categoria_id', db.Integer, primary_key=True)
    nome = db.Column('categoria_nome', db.String(256))

    def __init__(self, nome):
        self.nome = nome

class Pergunta(db.Model):
    __tablename__ = "pergunta"
    id = db.Column('pergunta_id', db.Integer, primary_key=True)
    texto = db.Column('pergunta_texto', db.String(256))
    data_pergunta = db.Column('pergunta_data', db.Date)
    anuncio_id = db.Column('anuncio_id', db.Integer, db.ForeignKey("anuncio.anuncio_id"))
    usuario_id = db.Column('usuario_id', db.Integer, db.ForeignKey("usuario.usuario_id"))

    def __init__(self, texto, anuncio_id, usuario_id):
        self.texto = texto
        self.data_pergunta = datetime.now()
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

class Compra(db.Model):
    __tablename__ = "compra"
    id = db.Column('compra_id', db.Integer, primary_key=True)
    data_compra = db.Column('compra_data', db.Date)
    preco = db.Column('compra_preco', db.Float)
    anuncio_id = db.Column('anuncio_id', db.Integer, db.ForeignKey("anuncio.anuncio_id"))
    usuario_id = db.Column('usuario_id', db.Integer, db.ForeignKey("usuario.usuario_id"))

    def __init__(self, preco, anuncio_id, usuario_id):
        self.data_compra = datetime.now()
        self.preco = preco
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

class Lista_Favoritos(db.Model):
    __tablename__ = "listafavoritos"
    id = db.Column('lista_favoritos_id', db.Integer, primary_key=True)
    nome = db.Column('nome_lista_favoritos', db.String(256))
    usuario_id = db.Column('usuario_id', db.Integer, db.ForeignKey("usuario.usuario_id"))

    def __init__(self, nome, usuario_id):
        self.nome = nome
        self.usuario_id = usuario_id

class Item_Lista_Favoritos(db.Model):
    __tablename__ = "itemlistafavoritos"
    id = db.Column('item_lista_favoritos_id', db.Integer, primary_key=True)
    anuncio_id = db.Column('anuncio_id', db.Integer, db.ForeignKey("anuncio.anuncio_id"))
    lista_favoritos_id = db.Column('lista_favoritos_id', db.Integer, db.ForeignKey("listafavoritos.lista_favoritos_id"))

    def __init__(self, anuncio_id, lista_favoritos_id):
        self.anuncio_id = anuncio_id
        self.lista_favoritos_id = lista_favoritos_id

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('paginanaoencontrada.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

@app.route("/")
def index():
    return render_template('index.html', titulo="Menu Principal")

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()

        user = Usuario.query.filter_by(email=email, senha=senha).first()

        if user:
            login_user(user)
            print(f"Usuário {user.nome} autenticado com sucesso.")
            return redirect(url_for('index'))
        else:
            print("Credenciais inválidas.")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/cadastro/usuario")
def usuario():
    usuarios = Usuario.query.all() 
    return render_template('usuario.html', titulo="Cadastro de Usuário", usuarios=usuarios)

@app.route("/usuario/criar", methods=['POST'])
def criar_usuario():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('password')  
    tipousuario = request.form.get('tipousuario')

    if not nome or not email or not senha or not tipousuario:
        return "Todos os campos são obrigatórios", 400

    senha_hash = hashlib.sha512(senha.encode("utf-8")).hexdigest()

    try:
        usuario = Usuario(nome=nome, email=email, senha=senha_hash, tipousuario=tipousuario)
        db.session.add(usuario)
        db.session.commit()
    except Exception as e:
        db.session.rollback()  
        print(f"Erro ao criar usuário: {e}")
        return "Erro ao criar usuário", 500

    return redirect(url_for('usuario'))

@app.route("/usuario/detalhar/<int:id>")
def detalhar_usuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route("/usuario/editar/<int:id>", methods=['GET', 'POST'])
def editar_usuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.senha = request.form.get('password')
        usuario.tipousuario = request.form.get('tipousuario')
        db.session.commit() 
        return redirect(url_for('usuario'))  
    return render_template('usuariocadastrado.html', usuario=usuario, titulo="Usuario")

@app.route("/usuario/deletar/<int:id>")
@login_required
def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
    return redirect(url_for('usuario')) 

@app.route("/cadastro/anuncio")
@login_required
def anuncio():
    anuncios = Anuncio.query.all()  
    usuarios = Usuario.query.all()  
    categorias = Categoria.query.all()  
    return render_template('anuncio.html', titulo="Cadastro de Anúncio", anuncios=anuncios, usuarios=usuarios, categorias=categorias, form_action='criar')

@app.route("/anuncio/criar", methods=['POST'])
@login_required
def criar_anuncio():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco')
        categoria_id = request.form.get('categoria_id')
        usuario_id = request.form.get('usuario_id')

        anuncio = Anuncio(titulo=titulo, descricao=descricao, preco=float(preco), categoria_id=int(categoria_id), usuario_id=int(usuario_id))
        db.session.add(anuncio)
        db.session.commit()

        return redirect(url_for('anuncio'))

@app.route("/anuncio/detalhar/<int:id>")
def detalhar_anuncio(id):
    anuncio = Anuncio.query.get(id)
    return anuncio.id

@app.route("/anuncio/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editar_anuncio(id):
    anuncio = Anuncio.query.get(id)
    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()
    if request.method == 'POST':
        anuncio.titulo = request.form.get('titulo')
        anuncio.descricao = request.form.get('descricao')
        anuncio.preco = float(request.form.get('preco'))
        anuncio.categoria_id = int(request.form.get('categoria_id'))
        anuncio.usuario_id = int(request.form.get('usuario_id'))
        db.session.commit()
        return redirect(url_for('anuncio'))
    return render_template('anunciocadastrado.html', titulo="Editar Anúncio", form_action='editar', anuncio=anuncio, categorias=categorias, usuarios=usuarios)


@app.route("/anuncio/deletar/<int:id>")
@login_required
def deletar_anuncio(id):
    anuncio = Anuncio.query.get(id)
    if anuncio:
        db.session.delete(anuncio)
        db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncios/pergunta")
@login_required
def pergunta():
    return render_template('pergunta.html', titulo="Perguntas Frequentes")

@app.route("/anuncios/compra")
@login_required
def compra():
    return render_template('compra.html', titulo="Compras")

@app.route("/anuncios/favoritos")
@login_required
def favoritos():
    return render_template('favoritos.html', titulo="Favoritos")

@app.route("/relatorios/vendas")
@login_required
def rel_vendas():
    return render_template('relVendas.html', titulo="Relatório de Vendas")

@app.route("/relatorios/compras")
@login_required
def rel_compras():
    return render_template('relCompras.html', titulo="Relatório de Compras")

if __name__ == 'anunciaaqui':
    with app.app_context():
        print("Criando todas as tabelas...")
        db.create_all()
        print("Tabelas criadas.")
    app.run(debug=True)
