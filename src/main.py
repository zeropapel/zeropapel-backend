from flask import Flask, request, jsonify
import os
from flask_cors import CORS

app = Flask(__name__)

# Configuração do CORS (Opção B: Recomendado para Produção)
# Habilita CORS para todas as rotas que começam com /api/
# e permite requisições apenas da origem https://www.zeropapel.com.br
CORS(app, resources={r"/api/*": {
    "origins": "https://www.zeropapel.com.br",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Inclua OPTIONS explicitamente
    "allow_headers": ["Authorization", "Content-Type", "X-Requested-With"]
}} )

# --- Início da seção de Middleware de Autenticação (se aplicável) ---
# Se você tiver um middleware de autenticação que verifica tokens JWT ou sessões,
# ele provavelmente está em uma função decorada com @app.before_request.
# É CRUCIAL que este middleware permita que as requisições OPTIONS passem sem verificação.

# Exemplo de como seu middleware DEVE ser ajustado:
# @app.before_request
# def verify_authentication():
#     # Se a requisição for OPTIONS, retorne imediatamente para permitir que o Flask-CORS a processe
#     if request.method == "OPTIONS":
#         return

#     # --- Sua lógica de verificação de autenticação real começa aqui ---
#     # Exemplo com Flask-JWT-Extended (adapte para sua implementação):
#     # from flask_jwt_extended import verify_jwt_in_request
#     # from flask_jwt_extended.exceptions import NoAuthorizationError

#     # # Exclua rotas de login/registro da verificação de autenticação
#     # # if request.endpoint not in ["login", "register"]:
#     # #     try:
#     # #         verify_jwt_in_request()
#     # #     except NoAuthorizationError:
#     # #         return jsonify({"msg": "Missing Authorization Header"}), 401
#     # #     except Exception as e:
#     # #         return jsonify({"msg": str(e)}), 401
#     # # --- Fim da sua lógica de verificação de autenticação ---
# pass # Remova esta linha se você descomentar o código acima

# --- Fim da seção de Middleware de Autenticação ---

@app.route("/")
def hello_world():
    return "Hello, Render! Application is running."

# --- Suas rotas de autenticação (register, login) devem ser descomentadas e implementadas aqui ---
# Exemplo (adapte conforme seu código real):
# @app.route("/api/auth/register", methods=["POST"])
# def register():
#     # Lógica para registrar um novo usuário
#     # Exemplo: data = request.get_json()
#     # if not data or not data.get("username") or not data.get("password"):
#     #     return jsonify({"msg": "Missing username or password"}), 400
#     # # ... salvar usuário no banco de dados ...
#     # return jsonify({"message": "User registered successfully"}), 201

# @app.route("/api/auth/login", methods=["POST"])
# def login():
#     # Lógica para autenticar o usuário e gerar um token JWT
#     # Exemplo: data = request.get_json()
#     # username = data.get("username")
#     # password = data.get("password")
#     # # ... verificar credenciais no banco de dados ...
#     # if username == "test" and password == "password": # Exemplo simples
#     # #     # from flask_jwt_extended import create_access_token
#     # #     # access_token = create_access_token(identity=username)
#     # #     # return jsonify(access_token=access_token), 200
#     # else:
#     # #     return jsonify({"msg": "Bad username or password"}), 401

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
