# Compatibilidade de Tecnologias com Hostinger

## Backend

### Node.js

O Hostinger oferece suporte a aplicações Node.js em seus planos de VPS e, em certa medida, em planos de hospedagem compartilhada com cPanel. O cPanel possui uma integração para aplicações Node.js, o que simplifica o processo de deploy. No entanto, algumas fontes indicam que o Node.js pode exigir acesso root para instalação de bibliotecas e módulos, o que é mais comum em ambientes VPS. Para hospedagem compartilhada, a compatibilidade pode depender da versão do cPanel e da configuração específica do Hostinger. É importante verificar se o plano de hospedagem compartilhada do usuário permite a execução de aplicações Node.js via cPanel.

### Python

O Hostinger oferece suporte robusto a aplicações Python em diversas de suas soluções de hospedagem, incluindo a capacidade de executar scripts Python via cron jobs e a instalação de aplicações Python WSGI via cPanel. Isso torna o Python uma opção viável para o backend da plataforma de assinatura.

## Frontend

### React.js

A implantação de aplicações React.js no Hostinger é possível, especialmente para aplicações que geram arquivos estáticos (builds). No entanto, para funcionalidades que dependem de Server-Side Rendering (SSR), como as oferecidas pelo Next.js, pode haver limitações em planos de hospedagem compartilhada, exigindo configurações específicas ou um ambiente VPS. Aplicações React puramente client-side são mais fáceis de implantar.

### Next.js

O Next.js, por sua natureza de SSR, apresenta mais desafios para implantação em hospedagem compartilhada com cPanel. Embora seja possível, muitos usuários relatam a necessidade de um ambiente VPS para ter controle total sobre o servidor e as configurações necessárias para o SSR. A implantação de Next.js em cPanel pode exigir configurações manuais complexas e pode não ser ideal para todos os cenários de hospedagem compartilhada.

## Banco de Dados

### PostgreSQL

O Hostinger não oferece suporte nativo a PostgreSQL em seus planos de hospedagem compartilhada ou em nuvem. Para utilizar PostgreSQL, o usuário precisaria de um plano VPS, o que implicaria em uma migração manual e gerenciamento do próprio servidor de banco de dados. Isso vai contra a especificação de usar o Hostinger existente e cPanel.

### MySQL

O MySQL é o sistema de gerenciamento de banco de dados padrão e totalmente suportado pelo Hostinger em todos os seus planos, incluindo hospedagem compartilhada com cPanel. É a opção mais compatível e recomendada para este projeto, dado o ambiente de hospedagem especificado.

## Conclusão Preliminar sobre Tecnologias

Com base na pesquisa de compatibilidade com o Hostinger e cPanel, as seguintes escolhas tecnológicas são as mais adequadas para o projeto:

*   **Backend:** Python (com Flask ou Django) é a opção mais segura e compatível para hospedagem compartilhada no Hostinger. Node.js é uma alternativa, mas pode apresentar mais desafios de configuração em cPanel compartilhado.
*   **Frontend:** React.js (com build estático) é a opção mais viável para o frontend, pois pode ser facilmente implantado em hospedagem compartilhada. Next.js é mais complexo e pode exigir um VPS.
*   **Banco de Dados:** MySQL é a escolha obrigatória, dada a falta de suporte nativo a PostgreSQL em planos de hospedagem compartilhada do Hostinger.

Esta análise preliminar será a base para a arquitetura detalhada da plataforma.



# Arquitetura Detalhada da Plataforma de Assinatura Digital e Eletrônica

Com base na análise de compatibilidade com o ambiente Hostinger e cPanel, a arquitetura da plataforma será definida para otimizar a performance, segurança e facilidade de implantação.

## 1. Escolha das Tecnologias

### Backend: Python com Flask

**Justificativa:** A pesquisa demonstrou que o Python é amplamente suportado no Hostinger, com recursos para execução de scripts e aplicações WSGI via cPanel. O Flask é um microframework Python leve e flexível, ideal para construir APIs RESTful, que serão o coração da comunicação entre o frontend e o backend. Sua simplicidade e modularidade facilitam o desenvolvimento e a manutenção, além de ser mais fácil de implantar em ambientes de hospedagem compartilhada em comparação com frameworks mais robustos como o Django, que pode exigir mais recursos e configurações específicas.

**Componentes Principais do Backend:**

*   **API RESTful:** Para gerenciar usuários, documentos, assinaturas e auditoria.
*   **Autenticação:** Implementação de autenticação baseada em JWT (JSON Web Tokens) para segurança das sessões, além de suporte a OAuth2 para login via Google.
*   **Gerenciamento de Documentos:** APIs para upload, conversão (DOCX para PDF), visualização e manipulação de documentos.
*   **Assinaturas:** Lógica para processar assinaturas eletrônicas (com registro de IP, timestamp, geolocalização) e placeholders para integração com APIs de certificação digital (ICP-Brasil).
*   **Auditoria e Logs:** Geração de hash SHA-256, timestamp (RFC 3161), trilha de auditoria detalhada e QR code para verificação.
*   **Integrações:** Módulos para integração com serviços de e-mail (SendGrid/SMTP), WhatsApp API (Twilio/Z-API) e APIs de certificado digital.

### Frontend: React.js

**Justificativa:** O React.js é uma biblioteca JavaScript robusta para construção de interfaces de usuário interativas. Sua capacidade de gerar builds estáticos (HTML, CSS, JavaScript) o torna altamente compatível com ambientes de hospedagem compartilhada como o Hostinger, onde esses arquivos podem ser facilmente implantados via cPanel ou FTP. A experiência do usuário será aprimorada com um editor de documentos drag-and-drop e um dashboard dinâmico.

**Componentes Principais do Frontend:**

*   **Dashboard do Usuário:** Interface para listar documentos, verificar status, baixar arquivos e gerenciar convites.
*   **Editor de Documentos:** Interface intuitiva para upload de PDFs (e conversão de DOCX), e arrastar e soltar campos de assinatura, data, nome completo e checkbox.
*   **Fluxo de Assinatura:** Interface para o processo de assinatura eletrônica e digital, com feedback visual e coleta de dados necessários.
*   **Painel Administrativo:** Interface para gerenciamento de usuários, estatísticas de uso e logs.
*   **Design Responsivo:** Garantia de que a plataforma seja totalmente funcional e visualmente agradável em dispositivos móveis e desktops.

### Banco de Dados: MySQL

**Justificativa:** O MySQL é a escolha padrão e totalmente suportada pelo Hostinger para hospedagem compartilhada. Ele oferece a confiabilidade e os recursos necessários para armazenar dados de usuários, documentos, logs de auditoria e configurações da plataforma. A configuração e o gerenciamento do MySQL são facilitados pelo cPanel.

**Estrutura de Dados (Exemplo):**

*   **Tabela `users`:** `id`, `email`, `password_hash`, `oauth_id`, `email_verified`, `created_at`, `updated_at`.
*   **Tabela `documents`:** `id`, `user_id`, `filename`, `original_path`, `signed_path`, `status`, `sha256_hash`, `created_at`, `updated_at`.
*   **Tabela `signature_requests`:** `id`, `document_id`, `signer_email`, `status`, `sent_at`, `signed_at`, `ip_address`, `geolocation`, `signature_type`.
*   **Tabela `audit_logs`:** `id`, `document_id`, `action`, `user_id`, `timestamp`, `ip_address`, `details`.
*   **Tabela `document_fields`:** `id`, `document_id`, `field_type`, `x_coord`, `y_coord`, `page_number`, `size`.

## 2. Segurança e Conformidade

*   **Criptografia:** Todos os dados em trânsito serão criptografados via HTTPS. Dados sensíveis em repouso (como hashes de senhas e documentos) serão armazenados de forma segura, utilizando técnicas de criptografia e hashing apropriadas.
*   **Prevenção de Ataques:** Implementação de medidas contra SQL Injection e XSS (Cross-Site Scripting).
*   **LGPD:** Design da plataforma com foco na conformidade com a LGPD, incluindo mecanismos para consentimento do usuário, direito ao esquecimento e proteção de dados pessoais.
*   **Logs de Auditoria:** Manutenção de logs de auditoria detalhados por no mínimo 5 anos, conforme exigido pela legislação.
*   **JWT:** Utilização de JSON Web Tokens para garantir a segurança das sessões de usuário.

## 3. Implantação no Hostinger

*   **Caminho de Implantação:** A plataforma será configurada para funcionar em um subdiretório (ex: `mydomain.com/signature`) para facilitar a integração com um site existente.
*   **cPanel/FTP:** O processo de implantação será detalhado para uso via cPanel ou FTP, incluindo a configuração do banco de dados MySQL e a criação do arquivo `.env`.
*   **SSL Gratuito:** Utilização do SSL gratuito (Let's Encrypt) fornecido pelo Hostinger para garantir a comunicação segura (HTTPS).

## 4. Funcionalidades Especiais

*   **PDF Assinado:** Cada PDF assinado incluirá o hash SHA-256, um rodapé com log de assinatura (IP, data, geolocalização, ID da assinatura) e um QR Code para verificação pública (`mydomain.com/verify?id=xxxx`).
*   **Modelo Freemium:** Implementação de lógica para permitir que usuários gratuitos assinem até 5 documentos por mês.

## 5. Testes

*   **Testes Unitários e de Integração:** Para garantir a funcionalidade e a robustez do código.
*   **Testes de Carga:** Simulação de 100 usuários concorrentes para avaliar o desempenho da plataforma.
*   **Testes de Responsividade:** Verificação da compatibilidade e usabilidade em diferentes dispositivos e tamanhos de tela.

Esta arquitetura detalhada servirá como um guia para as próximas fases de desenvolvimento, garantindo que todos os requisitos do usuário sejam atendidos de forma eficiente e segura.



# 6. Planejamento Técnico Abrangente

Este documento detalha o planejamento técnico para o desenvolvimento da plataforma de assinatura digital e eletrônica, abrangendo desde a estrutura de diretórios até as considerações de segurança e implantação.

## 6.1. Estrutura de Diretórios do Projeto

Para manter o código organizado e facilitar a implantação, a estrutura de diretórios será dividida em `backend` e `frontend`.

```
/signature_platform
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── models.py
│   │   ├── documents/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── models.py
│   │   ├── signatures/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── models.py
│   │   ├── audit/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── models.py
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── email_service.py
│   │   │   ├── whatsapp_service.py
│   │   │   └── icp_brasil_api.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── pdf_converter.py
│   │   │   ├── qr_generator.py
│   │   │   └── security.py
│   │   └── main.py  # Ponto de entrada da aplicação Flask
│   ├── config.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── wsgi.py  # Para implantação WSGI no cPanel
│   └── tests/
│       ├── test_auth.py
│       ├── test_documents.py
│       └── test_signatures.py
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   └── ... (outros assets estáticos)
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   │   ├── Login.js
│   │   │   │   └── Register.js
│   │   │   ├── Dashboard/
│   │   │   │   ├── DocumentList.js
│   │   │   │   └── DocumentCard.js
│   │   │   ├── DocumentEditor/
│   │   │   │   ├── EditorCanvas.js
│   │   │   │   └── FieldPalette.js
│   │   │   ├── Signature/
│   │   │   │   ├── SignModal.js
│   │   │   │   └── VerifyDocument.js
│   │   │   └── Admin/
│   │   │       ├── UserManagement.js
│   │   │       └── Stats.js
│   │   ├── services/
│   │   │   ├── auth.js
│   │   │   ├── documents.js
│   │   │   └── api.js
│   │   ├── styles/
│   │   │   ├── main.css
│   │   │   └── variables.css
│   │   └── utils/
│   │       ├── helpers.js
│   │       └── validators.js
│   ├── package.json
│   ├── .env.example
│   └── README.md
├── .gitignore
├── README.md
└── sql_schema.sql
```

## 6.2. Detalhamento do Backend (Python com Flask)

### Dependências (requirements.txt)

```
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-JWT-Extended
Flask-CORS
Werkzeug  # Para hashing de senhas
python-dotenv
psycopg2-binary  # Se PostgreSQL for usado, mas usaremos MySQL
PyMySQL  # Driver para MySQL
reportlab  # Para manipulação de PDF (conversão DOCX para PDF, adição de QR/rodapé)
qrcode  # Para geração de QR Code
requests  # Para chamadas a APIs externas (SendGrid, Twilio, ICP-Brasil)
python-magic  # Para detecção de tipo de arquivo
celery  # Para tarefas assíncronas (conversão de documentos, envio de emails/whatsapp)
redis  # Broker para Celery
```

### Estrutura da Aplicação Flask

*   **`app/__init__.py`**: Inicialização da aplicação Flask, configuração do SQLAlchemy, JWT, CORS.
*   **`app/auth/`**: Rotas e lógica para autenticação de usuários (registro, login, logout, redefinição de senha, verificação de e-mail, OAuth2).
*   **`app/documents/`**: Rotas e lógica para upload, gerenciamento, conversão e visualização de documentos.
*   **`app/signatures/`**: Rotas e lógica para criação e verificação de assinaturas (eletrônica e digital), registro de logs de auditoria.
*   **`app/audit/`**: Rotas e lógica para visualização e gerenciamento de logs de auditoria.
*   **`app/integrations/`**: Módulos para interagir com serviços externos (e-mail, WhatsApp, ICP-Brasil).
*   **`app/utils/`**: Funções utilitárias como conversão de PDF, geração de QR Code, funções de segurança (hashing, criptografia).
*   **`app/main.py`**: Ponto de entrada principal da aplicação, registro de blueprints.
*   **`config.py`**: Configurações da aplicação (chaves secretas, configurações de banco de dados, etc.).
*   **`wsgi.py`**: Arquivo de entrada para servidores WSGI (como o usado no cPanel).

### Autenticação

*   **Login/Registro:** Implementação de rotas para criação de conta e login com e-mail e senha. Hashing de senhas com `Werkzeug.security.generate_password_hash` e verificação com `check_password_hash`.
*   **JWT:** Geração de tokens de acesso e refresh para autenticação de API. Proteção de rotas com `@jwt_required`.
*   **OAuth2 (Google):** Integração com a API do Google para login simplificado. Armazenamento de `oauth_id` no banco de dados.
*   **Verificação de E-mail:** Envio de e-mail com token de verificação após o registro. Rota para confirmação do e-mail.
*   **Redefinição de Senha:** Geração de token único para redefinição de senha, envio por e-mail e rota para atualização da senha.

### Gerenciamento de Documentos

*   **Upload:** Recebimento de arquivos via API. Validação de tipo de arquivo. Armazenamento seguro em diretório configurável.
*   **Conversão DOCX para PDF:** Utilização de biblioteca como `python-docx` para ler DOCX e `reportlab` ou similar para gerar PDF. Alternativamente, pode-se usar um serviço externo ou uma ferramenta de linha de comando (se disponível no Hostinger) para conversão.
*   **Editor Drag-and-Drop:** O backend fornecerá as coordenadas e tipos de campos para o frontend. O frontend enviará essas informações para o backend para serem associadas ao documento.
*   **Preview:** O backend pode gerar miniaturas ou servir o PDF para visualização no frontend.

### Assinaturas

*   **Assinatura Eletrônica:**
    *   Registro de `user_id`, `document_id`, `timestamp`, `ip_address`, `geolocation` (obtida via IP ou frontend).
    *   Geração de hash SHA-256 do documento assinado.
    *   Inclusão de rodapé no PDF com dados da assinatura e QR Code.
*   **Assinatura Digital (ICP-Brasil):**
    *   **Placeholder para Integração:** O backend terá rotas e funções para interagir com APIs de provedores de certificado digital (Valid, Certisign, Soluti).
    *   O processo envolverá o envio do documento e dados do signatário para a API externa, que retornará o documento assinado digitalmente.
    *   Considerar a complexidade de manuseio de certificados A1/A3 (via browser ou aplicação desktop auxiliar).

### Auditoria e Logs

*   **Geração de Hash:** Cálculo do SHA-256 do documento final após todas as assinaturas.
*   **Timestamp (RFC 3161):** Integração com um serviço de carimbo de tempo confiável (TSA) para garantir a validade legal do timestamp.
*   **Trilha de Auditoria:** Registro detalhado de todas as ações relevantes (upload, visualização, assinatura, download) com `user_id`, `timestamp`, `ip_address`, `action_type`, `details`.
*   **QR Code:** Geração de QR Code que aponta para uma rota de verificação pública (`/verify?id=xxxx`).

### Integrações

*   **Serviço de E-mail (SendGrid/SMTP):** Configuração de envio de e-mails para verificação de conta, redefinição de senha, notificações de assinatura.
*   **WhatsApp API (Twilio/Z-API):** Integração para envio de lembretes de assinatura. Requer credenciais de API e configuração de webhooks.
*   **APIs de Certificado Digital (Valid, Soluti, Certisign):** Implementação de clientes para as APIs escolhidas. Necessário pesquisa aprofundada sobre a documentação de cada uma para definir a melhor abordagem.
*   **Validação CPF/CNPJ (Serpro API):** Opcional, mas pode ser integrado para validação de identidade dos signatários.

## 6.3. Detalhamento do Frontend (React.js)

### Dependências (package.json)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.23.1",
    "axios": "^1.6.8",
    "js-cookie": "^3.0.5",
    "pdfjs-dist": "^4.0.379",
    "react-pdf": "^7.7.1",
    "react-draggable": "^4.4.6",
    "react-resizable": "^3.0.5",
    "react-dropzone": "^14.2.3",
    "styled-components": "^6.1.11",
    "formik": "^2.4.6",
    "yup": "^1.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.2.0"
  }
}
```

### Estrutura da Aplicação React

*   **`public/`**: Contém o `index.html` e outros assets estáticos que serão servidos diretamente.
*   **`src/App.js`**: Componente principal que define as rotas da aplicação.
*   **`src/index.js`**: Ponto de entrada da aplicação React, renderiza o `App.js`.
*   **`src/components/`**: Componentes reutilizáveis e específicos de cada funcionalidade (autenticação, dashboard, editor, etc.).
*   **`src/services/`**: Módulos para interação com a API do backend (chamadas HTTP com `axios`).
*   **`src/styles/`**: Arquivos CSS para estilização global e de componentes.
*   **`src/utils/`**: Funções utilitárias para o frontend (validações, helpers).

### Dashboard do Usuário

*   Exibição de lista de documentos (upload, pendentes, assinados).
*   Funcionalidades de busca, filtro e paginação.
*   Opções para visualizar logs, baixar documentos, reenviar convites de assinatura.

### Editor de Documentos

*   **Upload:** Interface para arrastar e soltar arquivos PDF/DOCX. Validação de formato.
*   **Visualização de PDF:** Utilização de `react-pdf` para renderizar o documento PDF na tela.
*   **Colocação de Campos:** Componentes arrastáveis e redimensionáveis para campos de assinatura, data, nome completo, checkbox. As posições e tamanhos serão armazenados e enviados para o backend.
*   **Preview:** Visualização do documento com os campos antes do envio para assinatura.

### Fluxo de Assinatura

*   Interface para o signatário revisar o documento e aplicar a assinatura eletrônica (clique para assinar).
*   Coleta de IP e geolocalização via browser (com consentimento do usuário).
*   Integração com o backend para o processo de assinatura digital (ICP-Brasil), que pode envolver pop-ups ou redirecionamentos para o provedor de certificado.

### Painel Administrativo

*   Gerenciamento de usuários (criação, edição, exclusão, bloqueio).
*   Visualização de estatísticas de uso da plataforma (número de documentos, assinaturas).
*   Acesso a logs de sistema e performance.

## 6.4. Banco de Dados (MySQL)

### sql_schema.sql

```sql
-- Tabela de Usuários
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    oauth_id VARCHAR(255) UNIQUE,
    email_verified BOOLEAN DEFAULT FALSE,
    free_documents_signed INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de Documentos
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_path VARCHAR(255) NOT NULL,
    signed_path VARCHAR(255),
    status ENUM('uploaded', 'pending', 'signed', 'rejected') DEFAULT 'uploaded',
    sha256_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabela de Solicitações de Assinatura
CREATE TABLE signature_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    signer_email VARCHAR(255) NOT NULL,
    status ENUM('pending', 'signed', 'rejected') DEFAULT 'pending',
    signature_type ENUM('electronic', 'digital') NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signed_at TIMESTAMP,
    ip_address VARCHAR(45),
    geolocation VARCHAR(255),
    biometric_data_placeholder TEXT, -- Placeholder para dados biométricos
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- Tabela de Campos de Documento (para o editor drag-and-drop)
CREATE TABLE document_fields (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    field_type ENUM('signature', 'date', 'full_name', 'checkbox') NOT NULL,
    page_number INT NOT NULL,
    x_coord DECIMAL(10, 2) NOT NULL,
    y_coord DECIMAL(10, 2) NOT NULL,
    width DECIMAL(10, 2),
    height DECIMAL(10, 2),
    FOREIGN KEY (document_id) REFERENCES documents(id)
);

-- Tabela de Logs de Auditoria
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT,
    user_id INT,
    action_type VARCHAR(255) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tabela de Configurações (para o modelo freemium, por exemplo)
CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value TEXT
);

-- Inserir configurações iniciais
INSERT INTO settings (setting_key, setting_value) VALUES ('free_documents_limit', '5');
```

## 6.5. Considerações de Segurança

*   **HTTPS:** A implantação será configurada para forçar o uso de HTTPS, utilizando o SSL gratuito do Hostinger.
*   **Criptografia de Dados Sensíveis:** Senhas serão armazenadas como hashes. Documentos e outros dados sensíveis em repouso serão protegidos por permissões de arquivo adequadas e, se necessário, criptografia adicional no nível do sistema de arquivos ou banco de dados.
*   **Validação de Entrada:** Todas as entradas do usuário serão rigorosamente validadas no frontend e no backend para prevenir ataques como SQL Injection e XSS.
*   **CORS:** Configuração de CORS no Flask para permitir requisições do frontend React.
*   **Proteção contra CSRF:** Implementação de tokens CSRF para proteger formulários.
*   **Gerenciamento de Sessão:** JWT para sessões stateless. Revogação de tokens em caso de logout ou comprometimento.
*   **LGPD:** Design da base de dados e fluxos de trabalho para garantir a conformidade com a LGPD, incluindo consentimento explícito para coleta de dados, direito ao acesso, retificação e exclusão de dados.

## 6.6. Plano de Implantação no Hostinger (cPanel/FTP)

Um guia detalhado será fornecido, mas os passos gerais incluirão:

1.  **Configuração do Banco de Dados MySQL:** Criação de banco de dados e usuário via cPanel.
2.  **Upload do Backend:** Upload dos arquivos do Flask para o diretório apropriado (ex: `signature_platform/backend`) via FTP ou Gerenciador de Arquivos do cPanel.
3.  **Configuração do Ambiente Python:** Criação de um ambiente virtual Python e instalação de dependências via SSH (se disponível) ou através de ferramentas do cPanel.
4.  **Configuração WSGI:** Configuração do arquivo `wsgi.py` e do aplicativo Python no cPanel para servir a aplicação Flask.
5.  **Upload do Frontend:** Build da aplicação React (`npm run build`) e upload dos arquivos estáticos gerados (geralmente na pasta `build` ou `dist`) para o subdiretório público do Hostinger (ex: `public_html/signature`).
6.  **Configuração de Redirecionamento:** Configuração de regras de `.htaccess` no subdiretório para garantir que todas as rotas do frontend sejam tratadas corretamente (especialmente para `react-router-dom`).
7.  **Configuração de Variáveis de Ambiente:** Criação do arquivo `.env` no backend com as credenciais do banco de dados e chaves secretas.
8.  **Configuração de SSL:** Ativação do SSL gratuito via cPanel.

## 6.7. Modelo Freemium

*   A tabela `users` terá um campo `free_documents_signed` para rastrear o uso.
*   Uma configuração `free_documents_limit` será armazenada na tabela `settings`.
*   O backend verificará o limite antes de permitir novas assinaturas para usuários gratuitos.
*   O frontend exibirá o status de uso para o usuário.

## 6.8. Testes

*   **Unitários:** Testes para funções individuais e métodos de classes no backend e componentes no frontend.
*   **Integração:** Testes para verificar a comunicação entre backend e frontend, e entre o backend e serviços externos.
*   **Carga:** Utilização de ferramentas como `Locust` ou `JMeter` para simular 100 usuários concorrentes e identificar gargalos.
*   **Responsividade:** Testes em diferentes navegadores e dispositivos usando ferramentas de desenvolvedor e emuladores.

Este planejamento técnico fornece uma base sólida para o desenvolvimento da plataforma, garantindo que todos os requisitos sejam abordados de forma sistemática e eficiente.

