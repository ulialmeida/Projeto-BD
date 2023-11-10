from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, INTEGER
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user


# Cria uma instância da aplicação Flask, inicializando aplicação web
app = Flask(__name__)
app.secret_key = "bancodedadosdecompostos123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/almei/PycharmProjects/banco_compostos/compounds.db'
db = SQLAlchemy(app)

# Inicializar o Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Definição dos modelos SQLAlchemy para as tabelas do banco de dados
class Compound(db.Model):
    __tablename__ = 'tbl_compound' 
    compound_id = db.Column(db.Integer, primary_key=True)
    compound = db.Column(db.String(255))
    molecular_formula = db.Column(db.String(255))
    molecular_mass = db.Column(db.Float)
    
class Matrix(db.Model):
    __tablename__ = 'tbl_matrixes'
    matrixes_id = db.Column(db.Integer, primary_key=True)
    organism = db.Column(db.String(255))
    plant_tissue = db.Column(db.String(255))

class Name(db.Model):
    __tablename__ = 'tbl_name'
    name_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    
class Identification(db.Model):
    __tablename__ = 'tbl_identification'
    compound_id = db.Column(db.Integer, ForeignKey('tbl_compound.compound_id'), primary_key=True)
    matrix_id = db.Column(db.Integer, ForeignKey('tbl_matrixes.matrixes_id'), primary_key=True)
    name_id = db.Column(db.Integer, ForeignKey('tbl_name.name_id'), primary_key=True)

# Definição da classe User para autenticação
class User(UserMixin, db.Model):
    __tablename__ = 'tbl_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))

# Rotas para exibição e interação com os dados
@app.route('/')
def entrada():
    return render_template('entrada.html')

@app.route('/compound')
def index():
    compounds = Compound.query.all()
    return render_template('index.html', compounds=compounds)

@app.route('/matrixes')
def matrixes():
    matrixes = Matrix.query.all()
    if len(matrixes) == 0:
        return 'A tabela `tbl_matrixes` está vazia.'
    else:
        return render_template('matrixes.html', matrixes=matrixes)
    
@app.route('/name')
def name():
    names = Name.query.all()
    if len(names) == 0:
        return 'A tabela `tbl_name` está vazia.'
    else:
        return render_template('name.html', names=names)

@app.route('/identification')
def identification():
    identifications = Identification.query.all()
    if len(identifications) == 0:
        return 'A tabela `tbl_identification` está vazia.'
    else:
        return render_template('identification.html', identifications=identifications)

@app.route('/view_compound/<int:compound_id>')
def view_compound(compound_id):
    # Recupera o composto com base no ID
    compound = Compound.query.get(compound_id)

    if not compound:
        return 'Composto não encontrado.'

    # Recupera as identificações relacionadas a este composto
    identifications = Identification.query.filter_by(compound_id=compound_id).all()

    # Recupera informações relacionadas às matrizes e nomes usando os IDs das identificações
    matrix_info = []
    name_info = []

    for identification in identifications:
        matrix = Matrix.query.get(identification.matrix_id)
        name = Name.query.get(identification.name_id)

        if matrix:
            matrix_info.append(matrix)
        if name:
            name_info.append(name)

    return render_template('view_compound.html', compound=compound, matrix_info=matrix_info, name_info=name_info)

@app.route('/view_author_compounds/<int:author_id>')
def view_author_compounds(author_id):
    # Recupera o autor com base no ID
    author = Name.query.get(author_id)

    if not author:
        return 'Autor não encontrado.'

    # Recupera as identificações relacionadas a este autor
    identifications = Identification.query.filter_by(name_id=author_id).all()

    # Recupera informações relacionadas aos compostos usando os IDs das identificações
    compounds_info = []

    for identification in identifications:
        compound = Compound.query.get(identification.compound_id)
        if compound:
            compounds_info.append(compound)

    return render_template('view_author_compounds.html', author=author, compounds_info=compounds_info)

@app.route('/view_matrix_compounds/<int:matrix_id>')
def view_matrix_compounds(matrix_id):
    # Recupera o organismo com base no ID
    matrix = Matrix.query.get(matrix_id)

    if not matrix:
        return 'Organismo não encontrado.'

    # Recupera as identificações relacionadas a este organismo
    identifications = Identification.query.filter_by(matrix_id=matrix_id).all()

    # Recupera informações relacionadas aos compostos usando os IDs das identificações
    compound_info = []

    for identification in identifications:
        compound = Compound.query.get(identification.compound_id)

        if compound:
            compound_info.append(compound)

    return render_template('view_matrix_compounds.html', matrix=matrix, compound_info=compound_info)

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

     # Verifica se as credenciais estão corretas
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            login_user(user)  # Autentica o usuário
            return redirect(url_for('entrada'))

    return render_template('login.html')   

#Adição de novas informações 
@app.route('/add_compound', methods=['POST'])
@login_required
def add_compound():
    compound = request.form['compound']
    molecular_formula = request.form['molecular_formula']
    molecular_mass = request.form['molecular_mass']
    
    new_compound = Compound(compound=compound, molecular_formula=molecular_formula, molecular_mass=molecular_mass)
    db.session.add(new_compound)
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/add_matrix', methods=['POST'])
@login_required
def add_matrix():
    organism = request.form['organism']
    plant_tissue = request.form['plant_tissue']
    
    new_matrix = Matrix(organism=organism, plant_tissue=plant_tissue)
    db.session.add(new_matrix)
    db.session.commit()
    
    return redirect(url_for('matrixes'))

@app.route('/add_name', methods=['POST'])
@login_required
def add_name():
    name = request.form['name']
    
    new_name = Name(name=name)
    db.session.add(new_name)
    db.session.commit()
    
    return redirect(url_for('name'))

@app.route('/add_identification', methods=['POST'])
@login_required
def add_identification():
    compound_id = request.form['compound_id']
    matrix_id = request.form['matrix_id']
    name_id = request.form['name_id']
    
    new_identification = Identification(compound_id=compound_id, matrix_id=matrix_id, name_id=name_id)
    db.session.add(new_identification)
    db.session.commit()
    
    return redirect(url_for('identification'))

@app.route('/delete_compound', methods=['POST'])
@login_required
def delete_compound():
    compound_id = request.form['compound_id']

    # Verifica se o composto com o compound_id fornecido existe no banco de dados
    compound = Compound.query.get(compound_id)
    
    if not compound:
        return 'Composto não encontrado.'  # Redireciona para uma página de erro
    
    # Exclui composto do bd
    db.session.delete(compound)
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/delete_matrix', methods=['POST'])
@login_required
def delete_matrix():
    matrix_id = request.form['matrix_id']

    # Verifica se o composto com o compound_id fornecido existe no banco de dados
    matrix = Matrix.query.get(matrix_id)
    
    if not matrix:
        return 'Composto não encontrado.'  # Redireciona para uma página de erro
    
    # Exclui composto do bd
    db.session.delete(matrix)
    db.session.commit()

    return redirect(url_for('matrixes'))

@app.route('/delete_name', methods=['POST'])
@login_required
def delete_name():
    name_id = request.form['name_id']

    # Verifica se o composto com o compound_id fornecido existe no banco de dados
    name = Name.query.get(name_id)
    
    if not name:
        return 'Composto não encontrado.'  # Redireciona para uma página de erro
    
    # Exclui composto do bd
    db.session.delete(name)
    db.session.commit()

    return redirect(url_for('name'))

@login_manager.user_loader
def load_user(user_id):
    # Esta função é usada para carregar o usuário com base no ID do usuário
    return User.query.get(int(user_id))

# Inicialize o LoginManager com o seu aplicativo
login_manager.init_app(app)

#Flask seja iniciado somente quando o script Python for executado como um programa principal
if __name__ == '__main__':
    app.run(debug=True)
