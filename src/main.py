from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_migrate import Migrate, init, migrate, upgrade
from datetime import datetime

# --- Configuração da aplicação (Flask) e Banco de Dados ---
app = Flask(__name__)

# Configurações do ambiente e do banco de dados
if not os.environ.get("DATABASE_URL"):
    raise RuntimeError("A variável de ambiente DATABASE_URL precisa estar configurada!")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Inicialização do Flask-Migrate
migrate = Migrate(app, db)

# Configuração do JWT
if not os.environ.get("JWT_SECRET_KEY"):
    raise RuntimeError("A variável de ambiente JWT_SECRET_KEY precisa estar configurada!")
app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]

jwt = JWTManager(app)

# Configuração do Cross-Origin Resource Sharing (CORS)
CORS(app, resources={r"/api/*": {
    "origins": ["https://www.zeropapel.com.br", "https://zeropapel.com.br"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Authorization", "Content-Type", "X-Requested-With"]
}})

# --- Inicialização das migrações ---
with app.app_context():
    try:
        print("Verificando migrações do banco de dados...")
        
        # Verifica se o diretório de migrações existe
        from os.path import exists
        if not exists("migrations"):
            print("Diretório `migrations/` não encontrado. Inicializando...")
            init()

        # Gera os arquivos de migração, se necessário
        print("Criando migração...")
        migrate(message="Criação inicial do banco de dados")

        # Aplica as migrações no banco
        print("Aplicando migrações...")
        upgrade()
        print("Migrações aplicadas com sucesso!")
    except Exception as e:
        print(f"Erro ao aplicar migrações: {str(e)}")


# --- Definição do Modelo de Usuário ---
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    oauth_id = db.Column(db.String(255), unique=True, nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    free_documents_signed = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def can_sign_document(self):
        """Verifica se o usuário pode assinar mais documentos (fremium logic)"""
        if self.is_admin:
            return True
        return self.free_documents_signed < 5

    def increment_signed_documents(self):
        """Incrementa a contagem de documentos assinados"""
        self.free_documents_signed += 1
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'email_verified': self.email_verified,
            'free_documents_signed': self.free_documents_signed,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<User {self.email}>'


# --- Middleware de Autenticação ---
@app.before_request
def verify_authentication():
    if request.method == "OPTIONS":
        return

    # Ignorar verificação de autenticação para algumas rotas
    if request.endpoint not in ["login", "register", "hello_world"]:
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()  # Verifica o token JWT
        except Exception as e:
            return jsonify({"msg": f"Token inválido ou ausente: {str(e)}"}), 401


# --- Rotas ---
@app.route('/')
def hello_world():
    return 'Hello, Render! Application is running.'


@app.route("/api/auth/register", methods=["POST"])
def register():
    """Rota para registrar um novo usuário"""
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "Dados JSON são obrigatórios"}), 400
    
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email e senha são obrigatórios"}), 400

    if "@" not in email or len(password) < 6:
        return jsonify({"msg": "Email inválido ou senha muito curta"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Usuário já existe"}), 409

    try:
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        print(f"Usuário registrado com sucesso: {email}")
        return jsonify({"user": new_user.to_dict(), "msg": "Usuário registrado com sucesso"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar usuário: {e}")
        return jsonify({"msg": f"Erro ao registrar usuário: {e}"}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Rota para autenticar usuário"""
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "Dados JSON são obrigatórios"}), 400
    
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"msg": "Email ou senha incorretos"}), 401

    access_token = create_access_token(identity=user.email)
    print(f"Login bem-sucedido para: {email}")
    
    return jsonify({
        "message": "Login realizado com sucesso",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Retorna o usuário autenticado"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404

    return jsonify({"user": user.to_dict()}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Iniciando servidor na porta {port}")
    app.run(host='0.0.0.0', port=port)
