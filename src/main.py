from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

app = Flask(__name__)

# --- Configuração do Banco de Dados (Flask-SQLAlchemy) ---
# Certifique-se de que DATABASE_URL esteja configurada no Render.com
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "mysql+pymysql://user:password@host:port/dbname")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --- Configuração do JWT (Flask-JWT-Extended) ---
# Certifique-se de que JWT_SECRET_KEY esteja configurada no Render.com
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "sua_chave_secreta_aqui") # MUDE PARA UMA CHAVE FORTE E SEGURA!
jwt = JWTManager(app)

# --- Configuração do CORS ---
CORS(app, resources={r"/api/*": {
    "origins": "https://www.zeropapel.com.br",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Authorization", "Content-Type", "X-Requested-With"]
}} )

# --- Definição do Modelo de Usuário (simplificado para o main.py) ---
# Idealmente, este modelo estaria em src/models/user.py e seria importado.
# Estou incluindo-o aqui para que o main.py seja autocontido para este exemplo.
# Certifique-se de que a tabela \'users\' seja criada no seu banco de dados.
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
        """Check if user can sign more documents (freemium logic)"""
        if self.is_admin:
            return True
        # Assumindo um limite de 5 documentos gratuitos
        return self.free_documents_signed < 5

    def increment_signed_documents(self):
        """Increment the count of signed documents"""
        self.free_documents_signed += 1
        db.session.commit()

    def to_dict(self):
        return {
            \'id\': self.id,
            \'email\': self.email,
            \'email_verified\': self.email_verified,
            \'free_documents_signed\': self.free_documents_signed,
            \'is_admin\': self.is_admin,
            \'created_at\': self.created_at.isoformat() if self.created_at else None,
            \'updated_at\': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f\'\\<User {self.email}>\'

# --- Middleware de Autenticação ---
# Protege rotas que exigem autenticação, mas permite requisições OPTIONS.
@app.before_request
def verify_authentication():
    # Permite que as requisições OPTIONS passem sem verificação de token
    if request.method == "OPTIONS":
        return

    # Exclua rotas de login/registro da verificação de autenticação
    # Adapte \'login\' e \'register\' para os nomes de endpoint reais das suas funções
    # Se você usa Blueprints, o endpoint pode ser \'blueprint_name.function_name\'
    if request.endpoint not in ["login", "register", "hello_world"]:
        try:
            # Verifica se há um token JWT válido na requisição
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({"msg": f"Token inválido ou ausente: {str(e)}"}), 401

# --- Rotas ---
@app.route(\'/\')
def hello_world():
    return \'Hello, Render! Application is running.\'

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Registra um novo usuário"""
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "Dados JSON são obrigatórios"}), 400
    
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email e senha são obrigatórios"}), 400

    # Validação básica de email
    if "@" not in email or "." not in email:
        return jsonify({"msg": "Email inválido"}), 400

    # Validação básica de senha
    if len(password) < 6:
        return jsonify({"msg": "A senha deve ter pelo menos 6 caracteres"}), 400

    # Verifica se o usuário já existe
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Usuário com este email já existe"}), 409

    # Cria novo usuário
    new_user = User(email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Log da ação para depuração
        print(f"Usuário registrado com sucesso: {email}")
        
        return jsonify({
            "message": "Usuário registrado com sucesso",
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao registrar usuário: {str(e)}")
        return jsonify({"msg": f"Erro ao registrar usuário: {str(e)}"}), 500

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Autentica um usuário e retorna um token JWT"""
    data = request.get_json()
    
    if not data:
        return jsonify({"msg": "Dados JSON são obrigatórios"}), 400
    
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email e senha são obrigatórios"}), 400

    # Busca o usuário no banco de dados
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        # Gera token JWT
        access_token = create_access_token(identity=user.email)
        
        # Log da ação para depuração
        print(f"Login bem-sucedido para: {email}")
        
        return jsonify({
            "message": "Login realizado com sucesso",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200
    else:
        # Log da tentativa de login falhada para depuração
        print(f"Tentativa de login falhada para: {email}")
        return jsonify({"msg": "Email ou senha incorretos"}), 401

# Exemplo de rota protegida (requer JWT)
@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    """Rota de exemplo que requer autenticação JWT"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404
    
    return jsonify({
        "logged_in_as": current_user_email,
        "message": "Você acessou uma rota protegida!",
        "user": user.to_dict()
    }), 200

# Rota para obter informações do usuário atual
@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    """Retorna informações do usuário autenticado"""
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    
    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404
    
    return jsonify({"user": user.to_dict()}), 200

# Handler de erro para JWT
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token expirado"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"msg": "Token inválido"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"msg": "Token de autorização é obrigatório"}), 401


if __name__ == \'__main__\':
    # Inicializa o banco de dados se não existir (apenas para desenvolvimento/primeira execução)
    # Em produção, use migrações (Alembic) ou um processo separado para criar o DB.
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado")
    
    port = int(os.environ.get(\'PORT\', 5000))
    print(f"Iniciando servidor na porta {port}")
    app.run(host=\'0.0.0.0\', port=port)
