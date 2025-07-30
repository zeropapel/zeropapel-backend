# Manual de Implantação da Plataforma ZeroPapel no Hostinger (hPanel)

Olá! Este manual foi feito para te guiar, passo a passo, na instalação da sua Plataforma de Assinatura Digital ZeroPapel no Hostinger, usando o painel de controle hPanel. Não se preocupe se você não tem muita experiência, vamos explicar tudo de forma bem simples!

## O que você vai precisar antes de começar:

*   Seus dados de acesso ao Hostinger (e-mail e senha).
*   Os arquivos da sua plataforma ZeroPapel (o código que eu te entreguei).

--- 

## Passo 1: Acessando o hPanel do Hostinger

O hPanel é o painel de controle onde você gerencia tudo sobre sua hospedagem. É por lá que vamos fazer a instalação.

1.  **Abra seu navegador** (Chrome, Firefox, Edge, etc.).
2.  **Acesse o site do Hostinger** e faça login com seu e-mail e senha.
3.  Após fazer login, você verá a tela principal do hPanel. Se tiver mais de um site, selecione o domínio `zeropapel.com.br`.

--- 

## Passo 2: Criando o Banco de Dados (onde os dados da plataforma serão guardados)

Sua plataforma precisa de um lugar para guardar informações como usuários, documentos e assinaturas. Esse lugar é o Banco de Dados MySQL.

1.  No menu lateral esquerdo do hPanel, procure por **"Bancos de Dados"** e clique em **"Gerenciamento de Bancos de Dados"**.

    *(Não consigo gerar imagens, mas procure por um ícone de banco de dados ou texto similar no menu lateral.)*

2.  Na tela de gerenciamento, você verá uma seção para **"Criar Novo Banco de Dados MySQL"**.

    *   **Nome do Banco de Dados:** Digite um nome fácil de lembrar, por exemplo: `zeropapel_db`. **Anote este nome!**
    *   **Nome de Usuário do Banco de Dados:** Crie um nome de usuário para acessar este banco, por exemplo: `zeropapel_user`. **Anote este nome!**
    *   **Senha do Banco de Dados:** Crie uma senha **bem forte** para este usuário. Use letras maiúsculas, minúsculas, números e símbolos. Exemplo: `MinhaSenhaF0rte!23`. **Anote esta senha em um lugar seguro!**

3.  Clique no botão **"Criar"**.

    *(Procure por um botão com o texto "Criar" ou "Create".)*

4.  Após criar, o Hostinger geralmente já associa o usuário ao banco de dados. Verifique na lista abaixo se o usuário (`zeropapel_user`) está conectado ao banco (`zeropapel_db`). Se não estiver, você precisará associá-los manualmente na seção de "Usuários MySQL".

**Informações IMPORTANTES para anotar (você vai precisar delas depois!):**

*   **Nome do Banco de Dados:** `zeropapel_db` (ou o nome que você escolheu)
*   **Nome de Usuário do Banco de Dados:** `zeropapel_user` (ou o nome que você escolheu)
*   **Senha do Banco de Dados:** `SUA_SENHA_FORTE_AQUI` (a senha que você criou)
*   **Host do Banco de Dados:** Na maioria dos casos, será `localhost`. Se o Hostinger indicar outro, anote-o.

--- 

## Passo 3: Criando o Aplicativo Python (Flask) no hPanel

Agora vamos dizer ao Hostinger que você quer rodar uma aplicação Python (Flask) no seu site.

1.  No menu lateral esquerdo do hPanel, procure por **"Avançado"** e clique em **"Configurar Aplicativo"** (ou "Configurações de PHP", dependendo da sua versão do hPanel).

    *(Procure por um ícone de engrenagem ou texto similar.)*

2.  Na tela de configuração, procure por uma opção para **"Adicionar Aplicativo"** ou **"Criar Aplicativo"**.

3.  Você precisará preencher algumas informações:

    *   **Domínio:** Selecione `zeropapel.com.br`.
    *   **Subdomínio:** Deixe em branco, a menos que você queira que a plataforma rode em um subdomínio (ex: `app.zeropapel.com.br`).
    *   **Pasta do Aplicativo:** Crie uma pasta para sua aplicação, por exemplo: `public_html/app_zeropapel`. **Anote este caminho!**
    *   **Versão do Python:** Selecione a versão mais recente disponível (ex: `Python 3.9` ou superior).
    *   **Arquivo de Entrada (Entry File):** Digite `src/main.py`. Este é o arquivo principal da sua aplicação Flask.
    *   **Variáveis de Ambiente:** Por enquanto, vamos pular esta parte. Voltaremos a ela no Passo 5.

4.  Clique em **"Criar"** ou **"Salvar"**.

    *(Procure por um botão com o texto "Criar" ou "Salvar".)*

--- 

## Passo 4: Enviando os Arquivos da Plataforma para o Hostinger

Agora que o Hostinger sabe que você vai rodar uma aplicação Python, precisamos colocar os arquivos da sua plataforma lá dentro.

1.  No menu lateral esquerdo do hPanel, procure por **"Arquivos"** e clique em **"Gerenciador de Arquivos"**.

    *(Procure por um ícone de pasta ou texto similar.)*

2.  Dentro do Gerenciador de Arquivos, navegue até a pasta que você criou no Passo 3 (ex: `public_html/app_zeropapel`).

3.  **Envie os arquivos do backend:**
    *   Localize no seu computador a pasta `signature_platform_backend` que eu te entreguei.
    *   Dentro dela, você verá a pasta `src`. Você precisa enviar **todo o conteúdo** da pasta `signature_platform_backend` para dentro da pasta `app_zeropapel` no Hostinger.
    *   A forma mais fácil é **compactar** a pasta `signature_platform_backend` no seu computador (clique com o botão direito e escolha "Compactar" ou "Enviar para -> Pasta compactada"). Isso criará um arquivo `.zip`.
    *   No Gerenciador de Arquivos do Hostinger, clique no botão **"Upload"** (geralmente um ícone de nuvem com uma seta para cima) e selecione o arquivo `.zip` que você acabou de criar.
    *   Após o upload, clique com o botão direito no arquivo `.zip` no Hostinger e escolha a opção **"Extrair"** (ou "Unzip"). Extraia os arquivos para a pasta `app_zeropapel`.

    *(Procure pelos botões de upload e extração.)*

4.  **Verifique a estrutura:** Após extrair, a estrutura de pastas dentro de `app_zeropapel` deve ser parecida com esta:

    ```
    public_html/app_zeropapel/
    ├── src/
    │   ├── main.py
    │   ├── config.py
    │   ├── models/
    │   ├── routes/
    │   ├── utils/
    │   └── static/  (aqui estará o frontend)
    ├── venv/        (ambiente virtual do Python)
    ├── requirements.txt
    ├── .env.example
    └── ...outros arquivos do backend...
    ```

    **Importante:** Certifique-se de que o arquivo `main.py` esteja dentro da pasta `src` e que a pasta `src` esteja diretamente dentro de `app_zeropapel`.

--- 

## Passo 5: Configurando as Variáveis de Ambiente (informações secretas da plataforma)

As variáveis de ambiente são como "segredos" que sua aplicação precisa para funcionar, como a senha do banco de dados e chaves de segurança. Elas não ficam no código para sua segurança.

1.  Volte para a tela de **"Configurar Aplicativo"** (onde você criou o aplicativo Python no Passo 3).

2.  Role a página para baixo até encontrar a seção **"Variáveis de Ambiente"**.

3.  Você precisará adicionar as seguintes variáveis, uma por uma. Clique em "Adicionar Variável" para cada uma:

    *   **`DATABASE_URL`**: Esta é a informação mais importante para conectar ao seu banco de dados. Use o formato:
        `mysql+pymysql://NOME_USUARIO_BD:SENHA_BD@HOST_BD/NOME_BD`
        *   Substitua `NOME_USUARIO_BD`, `SENHA_BD`, `HOST_BD` e `NOME_BD` pelas informações que você anotou no **Passo 2**.
        *   Exemplo: `mysql+pymysql://zeropapel_user:MinhaSenhaF0rte!23@localhost/zeropapel_db`

    *   **`SECRET_KEY`**: Uma chave secreta para a segurança da sua aplicação. Crie uma sequência longa e aleatória de letras, números e símbolos. Exemplo: `minhachavesupersecreta123ABC!@#`

    *   **`JWT_SECRET_KEY`**: Uma chave secreta para os tokens de segurança. Você pode usar a mesma que `SECRET_KEY` ou criar uma nova.

    *   **`UPLOAD_FOLDER`**: O nome da pasta onde os documentos serão guardados. Digite `uploads`.

    *   **`DOMAIN_NAME`**: O domínio do seu site. Digite `zeropapel.com.br`.

    *   **`BASE_URL`**: A URL completa do seu site. Digite `https://zeropapel.com.br`.

    *   **Outras variáveis (se você for usar):** Se você planeja usar SendGrid (para e-mails), Twilio (para WhatsApp) ou integração com Google OAuth, adicione as variáveis correspondentes aqui, com as chaves que você obteve desses serviços:
        *   `SENDGRID_API_KEY`
        *   `FROM_EMAIL`
        *   `TWILIO_ACCOUNT_SID`
        *   `TWILIO_AUTH_TOKEN`
        *   `TWILIO_WHATSAPP_NUMBER`
        *   `GOOGLE_CLIENT_ID`
        *   `GOOGLE_CLIENT_SECRET`
        *   `ICP_BRASIL_API_KEY`
        *   `ICP_BRASIL_API_URL`
        *   `REDIS_URL` (se estiver usando Redis)

4.  Após adicionar todas as variáveis, clique em **"Salvar"** ou **"Atualizar"**.

--- 

## Passo 6: Instalando as Dependências da Plataforma

Sua plataforma usa algumas "bibliotecas" extras para funcionar. Precisamos instalá-las no ambiente do Hostinger.

1.  Volte para a tela de **"Configurar Aplicativo"** (onde você está desde o Passo 3).

2.  Role a página para baixo até encontrar a seção **"Instalar Dependências"**.

3.  Clique no botão **"Instalar"** ou **"Executar Composer/Pip"**. O Hostinger vai ler o arquivo `requirements.txt` (que está na pasta da sua aplicação) e instalar tudo automaticamente.

    *   Este processo pode levar alguns minutos. Aguarde até que ele termine e mostre uma mensagem de sucesso.

--- 

## Passo 7: Executando as Migrações do Banco de Dados (criando as tabelas)

Mesmo com o banco de dados criado, ele ainda está vazio. Precisamos criar as "tabelas" onde os dados serão organizados. Isso é feito com um comando de migração.

1.  No menu lateral esquerdo do hPanel, procure por **"Avançado"** e clique em **"SSH"**.

    *(Procure por um ícone de terminal ou texto similar.)*

2.  Você verá as informações de acesso SSH. Clique em **"Acessar SSH"** para abrir um terminal no seu navegador (ou use um programa como PuTTY se preferir).

3.  No terminal SSH, você precisará navegar até a pasta da sua aplicação. Digite o seguinte comando e pressione Enter:

    ```bash
    cd public_html/app_zeropapel
    ```
    *(Lembre-se de usar o caminho da pasta que você escolheu no Passo 3)*

4.  Agora, vamos ativar o ambiente virtual do Python e executar o comando de migração. Digite os seguintes comandos, um por um, e pressione Enter após cada um:

    ```bash
    source venv/bin/activate
    flask db upgrade
    ```
    *   O comando `source venv/bin/activate` ativa o ambiente onde as bibliotecas da sua aplicação estão instaladas.
    *   O comando `flask db upgrade` vai criar as tabelas no seu banco de dados. Você deve ver mensagens indicando que as tabelas foram criadas.

5.  Após a migração, você pode sair do ambiente virtual digitando:

    ```bash
    deactivate
    ```

6.  Feche a janela do terminal SSH.

--- 

## Passo 8: Testando a Aplicação Instalada

Chegou a hora de ver sua plataforma funcionando!

1.  No seu navegador, digite o endereço do seu site: `https://zeropapel.com.br`.

2.  Você deve ver a tela de login/registro da Plataforma ZeroPapel.

3.  **Crie uma nova conta:** Como o banco de dados estava vazio, você precisará criar sua primeira conta de usuário. Clique em **"Criar conta"** e preencha seus dados (e-mail e senha).

    *   Se o registro for bem-sucedido, você será redirecionado para o dashboard da plataforma.

4.  **Faça login:** Após criar a conta, tente fazer login com o e-mail e senha que você acabou de cadastrar.

    *   Se o login for bem-sucedido, parabéns! Sua plataforma está instalada e funcionando!

--- 

## Solução de Problemas Comuns:

*   **"Internal Server Error" ou tela em branco:**
    *   Verifique se todas as variáveis de ambiente foram configuradas corretamente no Passo 5.
    *   Verifique se o `DATABASE_URL` está com o formato e as credenciais corretas.
    *   Confira se todos os arquivos foram enviados para a pasta correta no Passo 4 e se a estrutura está como esperado (`src/main.py`).
    *   Verifique os logs de erro do seu aplicativo no hPanel (geralmente em "Configurar Aplicativo" ou "Logs de Erro").

*   **"Registration failed" ou "Login failed" após criar a conta:**
    *   Isso geralmente indica um problema de conexão com o banco de dados ou que as tabelas não foram criadas. Refaça o **Passo 7** (execução das migrações) com atenção.
    *   Verifique novamente as credenciais do banco de dados no `DATABASE_URL` (Passo 5).

*   **Página não encontrada (404):**
    *   Verifique se o "Arquivo de Entrada" (`src/main.py`) está correto no Passo 3.
    *   Confira se a pasta do aplicativo está correta (`public_html/app_zeropapel`).

Se você seguir este manual e ainda tiver problemas, não hesite em me contatar novamente!

