# Arquivos de Configuração para Deploy no Render.com

Este documento contém os arquivos de configuração necessários para fazer o deploy da plataforma ZeroPapel no Render.com.

## 1. Arquivo `render.yaml` (na raiz do projeto backend)

Crie este arquivo na pasta `signature_platform_backend/render.yaml`:

```yaml
services:
  - type: web
    name: zeropapel-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python src/main.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 10000
databases:
  - name: zeropapel-db
    databaseName: zeropapel
    user: zeropapel_user
```

## 2. Atualização do arquivo `src/main.py`

Substitua a parte final do arquivo `src/main.py` por:

```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

## 3. Atualização do arquivo `src/config.py`

Adicione estas linhas no arquivo de configuração para suportar PostgreSQL:

```python
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Render.com fornece PostgreSQL, não MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/signature_platform'
    
    # Fix para PostgreSQL no Render
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
```

## 4. Atualização do arquivo `requirements.txt`

Adicione estas dependências ao arquivo `requirements.txt`:

```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-JWT-Extended==4.5.2
Flask-CORS==4.0.0
Flask-Migrate==4.0.5
python-dotenv==1.0.0
bcrypt==4.0.1
Werkzeug==2.3.7
psycopg2-binary==2.9.7
gunicorn==21.2.0
```

## 5. Arquivo `.env.example` atualizado

```env
# Database (PostgreSQL no Render)
DATABASE_URL=postgresql://username:password@hostname:port/database

# Security
SECRET_KEY=sua-chave-secreta-super-forte
JWT_SECRET_KEY=sua-chave-jwt-secreta

# Upload settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Email (SendGrid)
SENDGRID_API_KEY=sua-api-key-sendgrid
FROM_EMAIL=noreply@zeropapel.com.br

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=seu-account-sid
TWILIO_AUTH_TOKEN=seu-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+5511999999999

# OAuth2 (Google)
GOOGLE_CLIENT_ID=seu-google-client-id
GOOGLE_CLIENT_SECRET=seu-google-client-secret

# Domain
DOMAIN_NAME=zeropapel.com.br
BASE_URL=https://zeropapel.com.br

# CORS
CORS_ORIGINS=https://zeropapel.com.br,https://www.zeropapel.com.br

# Production
FLASK_ENV=production
PORT=10000
```

## 6. Arquivo `Procfile` (alternativo)

Se preferir usar Procfile em vez de render.yaml:

```
web: gunicorn --bind 0.0.0.0:$PORT src.main:app
```

## 7. Atualização do frontend `src/lib/api.js`

```javascript
// Configuração da API para produção
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://zeropapel-backend.onrender.com/api'
  : 'http://localhost:5000/api';

// Resto do código permanece igual...
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## 8. Arquivo `.htaccess` para o Hostinger

Crie este arquivo na pasta `public_html` do Hostinger:

```apache
RewriteEngine On
RewriteBase /

# Handle SPA routes
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]

# Security headers
Header always set X-Frame-Options DENY
Header always set X-Content-Type-Options nosniff
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"

# CORS headers (se necessário)
Header always set Access-Control-Allow-Origin "https://zeropapel-backend.onrender.com"
Header always set Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
Header always set Access-Control-Allow-Headers "Content-Type, Authorization"

# Cache static assets
<FilesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 month"
    Header append Cache-Control "public, immutable"
</FilesMatch>

# Compress files
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>
```

## 9. Script de build para o frontend

Crie um arquivo `build.sh` na pasta do frontend:

```bash
#!/bin/bash
echo "Building ZeroPapel Frontend for Production..."

# Install dependencies
npm install

# Build for production
npm run build

echo "Build completed! Files are in the 'dist' folder."
echo "Upload the contents of 'dist' folder to your Hostinger public_html directory."
```

## 10. Variáveis de ambiente para o Render

Configure estas variáveis no dashboard do Render:

```
SECRET_KEY=sua_chave_secreta_super_forte_aqui
JWT_SECRET_KEY=sua_chave_jwt_secreta_aqui
DOMAIN_NAME=zeropapel.com.br
BASE_URL=https://zeropapel.com.br
UPLOAD_FOLDER=uploads
CORS_ORIGINS=https://zeropapel.com.br,https://www.zeropapel.com.br
FLASK_ENV=production
```

---

**Instruções de uso:**

1. Copie estes arquivos para os locais indicados
2. Atualize as URLs e chaves conforme necessário
3. Faça o deploy seguindo o manual principal
4. Teste todas as funcionalidades

*Configurações preparadas por: Manus AI*

