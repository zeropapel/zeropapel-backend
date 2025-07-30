# Manual de Implantação da Plataforma ZeroPapel - Hostinger Web/Cloud + PaaS

Olá! Este manual foi atualizado especificamente para sua situação: hospedagem Hostinger Web/Cloud que não suporta aplicações Python diretamente. Vamos usar uma abordagem híbrida onde o **backend (Flask)** será hospedado em um serviço PaaS (Platform as a Service) e o **frontend (React)** será hospedado no seu Hostinger como site estático.

## Vantagens desta abordagem:

*   ✅ **Compatível com sua hospedagem atual** (Hostinger Web/Cloud)
*   ✅ **Sem custos adicionais** para começar (usaremos planos gratuitos do PaaS)
*   ✅ **Escalabilidade** - o PaaS cuida da infraestrutura do backend
*   ✅ **Facilidade de manutenção** - atualizações automáticas e backups
*   ✅ **Performance otimizada** - cada parte da aplicação roda no ambiente ideal

---

## Parte 1: Implantando o Backend no Render.com (PaaS)

O Render.com é um serviço PaaS moderno e fácil de usar, com plano gratuito que é perfeito para começar.

### Passo 1.1: Criando conta no Render.com

1.  **Acesse o site:** Vá para [https://render.com](https://render.com)
2.  **Crie sua conta:** Clique em "Get Started" e crie uma conta usando seu e-mail ou conecte com GitHub
3.  **Confirme seu e-mail:** Verifique sua caixa de entrada e confirme o e-mail

### Passo 1.2: Preparando o código para o Render

Antes de fazer o deploy, precisamos fazer alguns ajustes no código do backend:

1.  **Baixe os arquivos:** Certifique-se de ter a pasta `signature_platform_backend` no seu computador
2.  **Crie um arquivo `render.yaml`** na raiz da pasta `signature_platform_backend`:

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
      - key: DATABASE_URL
        fromDatabase:
          name: zeropapel-db
          property: connectionString
```

3.  **Atualize o arquivo `src/main.py`** para rodar na porta correta do Render:

```python
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Passo 1.3: Criando o banco de dados no Render

1.  **No dashboard do Render:** Clique em "New +" e selecione "PostgreSQL"
2.  **Configure o banco:**
   *   **Name:** `zeropapel-db`
   *   **Database:** `zeropapel`
   *   **User:** `zeropapel_user`
   *   **Region:** Escolha a mais próxima do Brasil (ex: Ohio)
3.  **Clique em "Create Database"**
4.  **Anote as informações de conexão** que aparecerão (você precisará delas depois)

### Passo 1.4: Fazendo deploy do backend

1.  **No dashboard do Render:** Clique em "New +" e selecione "Web Service"
2.  **Conecte seu repositório:**
   *   Se você tem GitHub: conecte o repositório onde está o código
   *   Se não tem GitHub: use a opção "Deploy from Git repository" e cole a URL do repositório
   *   **Alternativa:** Use a opção "Upload files" para enviar a pasta `signature_platform_backend`

3.  **Configure o serviço:**
   *   **Name:** `zeropapel-backend`
   *   **Environment:** `Python 3`
   *   **Build Command:** `pip install -r requirements.txt`
   *   **Start Command:** `python src/main.py`

4.  **Configure as variáveis de ambiente:**
   Clique em "Advanced" e adicione estas variáveis:
   
   *   `SECRET_KEY`: `sua_chave_secreta_super_forte_aqui`
   *   `JWT_SECRET_KEY`: `sua_chave_jwt_secreta_aqui`
   *   `DATABASE_URL`: (será preenchida automaticamente pelo banco PostgreSQL)
   *   `DOMAIN_NAME`: `zeropapel.com.br`
   *   `BASE_URL`: `https://zeropapel.com.br`
   *   `UPLOAD_FOLDER`: `uploads`

5.  **Clique em "Create Web Service"**

6.  **Aguarde o deploy:** O Render vai instalar as dependências e iniciar sua aplicação. Isso pode levar alguns minutos.

7.  **Anote a URL do backend:** Após o deploy, você receberá uma URL como `https://zeropapel-backend.onrender.com`. **Anote esta URL!**

### Passo 1.5: Testando o backend

1.  **Acesse a URL do backend** no navegador
2.  **Teste a API:** Adicione `/api/users` no final da URL (ex: `https://zeropapel-backend.onrender.com/api/users`)
3.  **Deve retornar:** `[]` (lista vazia, indicando que a API está funcionando)

---

## Parte 2: Preparando o Frontend para o Hostinger

Agora vamos preparar o frontend React para ser hospedado como site estático no Hostinger.

### Passo 2.1: Atualizando a configuração da API

1.  **Abra a pasta `signature_platform_frontend`** no seu computador
2.  **Edite o arquivo `src/lib/api.js`:**

```javascript
// Substitua a URL base pela URL do seu backend no Render
const API_BASE_URL = 'https://zeropapel-backend.onrender.com/api';

// Resto do código permanece igual...
```

3.  **Salve o arquivo**

### Passo 2.2: Compilando o frontend para produção

1.  **Abra o terminal/prompt de comando** na pasta `signature_platform_frontend`
2.  **Instale as dependências** (se ainda não fez):
   ```bash
   npm install
   ```
   ou
   ```bash
   pnpm install
   ```

3.  **Compile para produção:**
   ```bash
   npm run build
   ```
   ou
   ```bash
   pnpm run build
   ```

4.  **Verifique a pasta `dist`:** Após a compilação, você terá uma pasta `dist` com todos os arquivos estáticos (HTML, CSS, JS)

---

## Parte 3: Hospedando o Frontend no Hostinger

### Passo 3.1: Acessando o hPanel

1.  **Faça login no Hostinger** com suas credenciais
2.  **Acesse o hPanel** do domínio `zeropapel.com.br`

### Passo 3.2: Enviando os arquivos do frontend

1.  **No hPanel:** Vá em "Arquivos" → "Gerenciador de Arquivos"
2.  **Navegue até `public_html`:** Esta é a pasta raiz do seu site
3.  **Limpe a pasta (se necessário):** Se houver arquivos antigos, você pode removê-los
4.  **Envie os arquivos da pasta `dist`:**
   *   **Opção 1:** Compacte a pasta `dist` em um arquivo `.zip`, faça upload e extraia
   *   **Opção 2:** Selecione todos os arquivos dentro da pasta `dist` e faça upload diretamente

5.  **Estrutura final:** Sua pasta `public_html` deve conter:
   ```
   public_html/
   ├── index.html
   ├── assets/
   │   ├── index-[hash].css
   │   └── index-[hash].js
   └── outros arquivos estáticos...
   ```

### Passo 3.3: Configurando redirecionamentos (importante!)

Como é uma Single Page Application (SPA), precisamos configurar redirecionamentos:

1.  **Crie um arquivo `.htaccess`** na pasta `public_html` com o seguinte conteúdo:

```apache
RewriteEngine On
RewriteBase /

# Handle Angular and Vue.js routes
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]

# Security headers
Header always set X-Frame-Options DENY
Header always set X-Content-Type-Options nosniff
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"

# Cache static assets
<FilesMatch "\.(css|js|png|jpg|jpeg|gif|ico|svg)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 month"
</FilesMatch>
```

2.  **Salve o arquivo** no Gerenciador de Arquivos do Hostinger

---

## Parte 4: Configurações Finais e Testes

### Passo 4.1: Configurando CORS no backend

Para que o frontend no Hostinger se comunique com o backend no Render, precisamos configurar CORS:

1.  **No Render dashboard:** Vá para seu serviço `zeropapel-backend`
2.  **Adicione uma variável de ambiente:**
   *   **Key:** `CORS_ORIGINS`
   *   **Value:** `https://zeropapel.com.br,https://www.zeropapel.com.br`

3.  **O backend já está configurado** para usar esta variável (no código que desenvolvi)

### Passo 4.2: Testando a aplicação completa

1.  **Acesse seu site:** `https://zeropapel.com.br`
2.  **Verifique se carrega:** Você deve ver a tela de login da plataforma
3.  **Teste o registro:** Clique em "Criar conta" e tente registrar um usuário
4.  **Teste o login:** Após registrar, tente fazer login
5.  **Verifique o dashboard:** Se tudo estiver funcionando, você verá o dashboard da plataforma

### Passo 4.3: Monitoramento e logs

1.  **No Render:** Você pode ver os logs do backend em tempo real na aba "Logs"
2.  **No navegador:** Use F12 → Console para ver possíveis erros do frontend
3.  **Teste todas as funcionalidades** principais da plataforma

---

## Solução de Problemas Comuns

### Problema: "CORS Error" ou "Network Error"

**Solução:**
1.  Verifique se a URL da API no frontend está correta
2.  Confirme se a variável `CORS_ORIGINS` está configurada no Render
3.  Verifique se o backend está rodando (acesse a URL do Render diretamente)

### Problema: "Registration failed" ou "Database error"

**Solução:**
1.  Verifique os logs do backend no Render
2.  Confirme se o banco PostgreSQL está conectado corretamente
3.  Execute as migrações do banco (se necessário, via Render Shell)

### Problema: Página em branco ou erro 404

**Solução:**
1.  Verifique se o arquivo `.htaccess` foi criado corretamente
2.  Confirme se todos os arquivos da pasta `dist` foram enviados
3.  Verifique se o arquivo `index.html` está na raiz de `public_html`

### Problema: Backend "dormindo" (plano gratuito do Render)

**Solução:**
1.  O plano gratuito do Render "dorme" após 15 minutos de inatividade
2.  A primeira requisição após o "sono" pode demorar 30-60 segundos
3.  Para evitar isso, considere upgrade para plano pago ou use um serviço de "ping" para manter ativo

---

## Custos e Escalabilidade

### Custos Iniciais (Gratuito!)
*   **Render.com:** Plano gratuito (750 horas/mês)
*   **Hostinger:** Seu plano atual Web/Cloud
*   **Total:** R$ 0,00 adicionais

### Quando considerar upgrade:
*   **Render Pro ($7/mês):** Para eliminar o "sono" e ter melhor performance
*   **Banco de dados dedicado:** Se precisar de mais armazenamento
*   **CDN:** Para melhor performance global

---

## Próximos Passos

1.  **Teste todas as funcionalidades** da plataforma
2.  **Configure integrações** (SendGrid, Twilio, etc.) via variáveis de ambiente no Render
3.  **Monitore performance** e considere upgrades conforme necessário
4.  **Configure backups** automáticos do banco de dados
5.  **Implemente SSL** personalizado se desejar (já incluído no Render)

**Parabéns!** Sua plataforma ZeroPapel agora está rodando com uma arquitetura moderna e escalável, compatível com sua hospedagem Hostinger Web/Cloud!

---

*Desenvolvido por: Manus AI*  
*Data: 09 de Julho de 2025*  
*Versão: 2.0.0 (Atualizada para PaaS + Hostinger)*

