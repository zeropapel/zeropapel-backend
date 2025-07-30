from flask import Flask
import os
from flask_cors import CORS # Importe a extensão Flask-CORS

app = Flask(__name__ )

# Configuração do CORS (Opção B: Recomendado para Produção)
# Habilita CORS para todas as rotas que começam com /api/
# e permite requisições apenas da origem https://www.zeropapel.com.br
CORS(app, resources={r"/api/*": {"origins": "https://www.zeropapel.com.br"}} )

@app.route('/')
def hello_world():
    return 'Hello, Render! Application is running.'

# Certifique-se de que suas rotas de autenticação (register, login) estejam definidas aqui
# Exemplo (adapte conforme seu código real):
# @app.route("/api/auth/register", methods=["POST"])
# def register():
#     # ... seu código de registro ...
#     return {"message": "User registered successfully"}

# @app.route("/api/auth/login", methods=["POST"])
# def login():
#     # ... seu código de login ...
#     return {"message": "User logged in successfully"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
