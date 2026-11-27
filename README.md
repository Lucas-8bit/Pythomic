# Pythomic 2.0

Rede social estilo Instagram feita em **Python puro** (ReactPy + Flask), agora
**modular**, com **design moderno mobile-only** e **muitas animações**.

Esta versão refatora o `pythomic.py` original (um único arquivo monolítico de
~2.300 linhas) em vários módulos por responsabilidade, mantendo **100% da
funcionalidade** original: criptografia de campos sensíveis, hash de senha
PBKDF2, rate limiting, uploads validados por magic bytes, feed, curtir,
seguir, views, perfis, troca de foto/senha e tema claro/escuro persistente.

> A interface é **mobile-only**: foi pensada para a tela do telefone. Abra no
> celular ou use a emulação mobile das DevTools do navegador.

---

## ✨ O que mudou nesta versão

### Design moderno + animações
- **Glassmorphism** no cabeçalho e nos modais (`backdrop-filter:
  saturate(180%) blur(20px)`), além de cards.
- **Sombras em camadas** e cantos mais arredondados.
- **Gradientes animados** no logo, no botão primário (com varredura shimmer) e
  no anel do avatar (gira no estilo stories).
- **Entrada escalonada dos cards** do feed (stagger animation, 1.º–8.º card).
- **Top sheet**: modais descem do topo (de cima para baixo), com cantos
  arredondados embaixo — coerente com os botões de ação do cabeçalho.
- **Pop do coração** reforçado ao curtir, com brilho (`drop-shadow`) e
  **rajada de 4 partículas em cruz**.
- **Ripple** nos botões e feedback de toque (scale) em todos os interativos.
- **Shake** nas mensagens de erro, **float** no ícone de feed vazio.
- **Skeleton shimmer** disponível (classe `.py-skeleton`).
- **Transições suaves** de tema com `cubic-bezier(0.4, 0, 0.2, 1)`.
- **Acessibilidade**: `@media (prefers-reduced-motion: reduce)` desativa
  animações e transições.

### Mobile-only adaptativo
- A **barra lateral de desktop foi removida** (`display: none`) — todos os
  botões de ação (criar post, atualizar, tema e menu) ficam no **cabeçalho**,
  sem barra inferior.
- **Celular (retrato)**: coluna única, cards centralizados, tipografia fluida
  com `clamp()`.
- **≤ 480 px (telefone)**: elementos um pouco maiores (avatar, botões de toque
  ≥44 px e textos) para ficar mais confortável — sem afetar tablets.
- **≥ 600 px**: área principal mais larga (640 px), cards mais largos.
- **Feed sempre em coluna única** (mobile-only): não há mais grid de 2 colunas
  em telas maiores.
- **≥ 1.024 px**: continua mobile — apenas centralizado/largo (760 px), sem
  layout de desktop.
- Suporte a **safe-area-inset** (iPhone com notch) no cabeçalho e nos modais.
- **Meta `viewport`** injetada no `<head>` pelo `run.py`
  (`width=device-width, initial-scale=1, viewport-fit=cover`) — sem ela, o
  navegador do celular renderiza a página a ~980 px e a interface fica minúscula.
- `theme-color` dinâmica (`#5b5bf6` no claro, `#05060c` no escuro) e metas
  `apple-mobile-web-app-capable` / `mobile-web-app-capable` para uso como PWA.

### Contas: verificação de email, recuperação e exclusão
- **Bot de email** (`pythomic/mailer.py`): valida se o email é real, gera o
  código de verificação e a nova senha de recuperação, e envia tudo por SMTP.
- **Verificação de email no cadastro**: o email é confirmado com um código de
  6 dígitos antes da conta ser criada — só emails reais entram no banco.
- **Recuperação de senha**: "Esqueci minha senha" gera uma nova senha aleatória
  e envia por email; depois é só entrar normalmente (igual ao login de sempre).
- **Excluir conta** nas Configurações, com **duas confirmações** e aviso de
  que é **irreversível** (é preciso digitar EXCLUIR).

### Código separado em sistemas
A aplicação foi dividida em pacotes independentes para melhor organização:

```
pythomic/                      # raiz do projeto
├── run.py                     # ponto de entrada: python run.py
├── requirements.txt
├── README.md
├── iniciar.sh                 # setup completo em 1 comando (venv + deps + .env + run)
├── .env.example               # modelo de configuração SMTP (copie para .env)
└── pythomic/                  # pacote Python
    ├── __init__.py
    ├── config.py              # caminhos, constantes, segredo mestre
    ├── security.py            # criptografia Fernet, PBKDF2, rate limiter
    ├── database.py            # schema SQLite + consultas + safe_user()
    ├── mailer.py              # bot de email: valida email, código, nova senha, SMTP
    ├── uploads.py             # validação de mídia (magic bytes, tamanho)
    ├── server.py              # app Flask + cabeçalhos de segurança
    └── ui/
        ├── __init__.py
        ├── styles.py          # CSS global (moderno, mobile-only, animado)
        ├── scripts.py         # JS injetado (tema, upload base64)
        ├── icons.py           # ícones SVG inline
        └── components/        # um arquivo por tela ReactPy
            ├── __init__.py
            ├── welcome.py     # tela de boas-vindas
            ├── auth.py        # login / cadastro c/ verificação de email / recuperação
            ├── post_card.py   # card de post
            ├── create_post.py # top sheet de criar post
            ├── menu.py        # top sheet do perfil próprio + excluir conta
            ├── profile.py     # top sheet do perfil de outro usuário
            ├── home.py        # feed + header (criar, atualizar, tema, menu)
            └── app.py         # raiz: roteamento, tema, CSS global
```

Cada arquivo tem uma única responsabilidade, facilitando localizar, testar e
modificar cada parte.

---

## 📱 Funcionalidades

- **Cadastro e login** por **nome de usuário** (não email) e senha (política:
  mínimo de 8 caracteres, pelo menos uma letra e um número) e botão de
  mostrar/ocultar a senha dentro do campo, no canto.
- **Verificação de email no cadastro**: o bot valida se o email é real (formato
  + domínio com registro MX — aceita gmail, hotmail, outlook e todos os outros
  provedores) e envia um **código de 6 dígitos**. Só depois de digitar o código
  a conta é criada com o email confirmado no banco.
- **Recuperação de senha por email**: na tela de login, "Esqueci minha senha"
  pede o email da conta; o bot gera uma **nova senha aleatória**, substitui no
  banco e envia por email. Depois é só entrar normalmente — o site funciona
  igual ao login de sempre. A senha pode ser trocada depois nas Configurações.
- **Excluir a própria conta** nas Configurações, com **duas confirmações** e
  aviso de que **não dá para recuperar** (é preciso digitar EXCLUIR). Apaga
  posts, fotos, curtidas, seguidores e o usuário.
- **Feed** de posts com foto e legenda, entrada escalonada dos cards e botão
  **Atualizar** no cabeçalho (ao lado do +).
- **Curtir** com animação de pop + partículas e contador de curtidas.
- **Visualizações** únicas por post (uma por usuário, registrada no feed).
- **Criar post** via top sheet (abre pelo botão **+** no cabeçalho), com upload
  de mídia e legenda (até 500 caracteres).
- **Perfis** próprio e de outros usuários, com estatísticas (posts, seguidores
  e seguindo) e anel de avatar girando.
- **Seguir / desseguir** usuários.
- **Excluir os próprios posts** (botão no card, com confirmação em 2 cliques) —
  apaga também o arquivo de mídia da pasta `uploads/`.
- **Trocar foto de perfil e senha**.
- **Menu** (top sheet) com logout, troca de tema e **exclusão de conta**.
- **Tema claro/escuro persistente** (salvo em `localStorage`), com transição
  suave entre os temas.

---

## Requisitos

- Python **3.10 ou superior** (recomendado).
- `pip`.
- Conexão com a internet na primeira instalação, para baixar as dependências.

Confira a instalação do Python:

```bash
python --version
python -m pip --version
```

Em alguns sistemas Linux, o comando é `python3` em vez de `python`.

## Instalação e execução no Windows (CMD)

Abra o **Prompt de Comando (CMD)** e navegue até a pasta onde salvou ou clonou
o projeto. Por exemplo:

```bat
cd %USERPROFILE%\projetos\Pythomic
```

Se ainda não baixou o repositório, pode cloná-lo com Git:

```bat
git clone https://github.com/Letra-Arcania/Pythomic.git
cd Pythomic
```

Crie um ambiente virtual:

```bat
py -m venv .venv
```

Ative-o:

```bat
.venv\Scripts\activate
```

Atualize o `pip` e instale as dependências do projeto:

```bat
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

Inicie a aplicação:

```bat
py run.py
```

Abra o navegador em:

**http://localhost:5000**

Para parar o servidor, pressione `Ctrl+C` no terminal. Para sair do ambiente
virtual, execute `deactivate`.

> Se o comando `py` não existir, instale o Python pelo site oficial e marque a
> opção para adicioná-lo ao `PATH`. Depois tente usar `python` no lugar de `py`.

## Instalação e execução no Linux

Primeiro, clone o repositório ou entre na pasta que contém `run.py` e
`requirements.txt`:

```bash
git clone https://github.com/Letra-Arcania/Pythomic.git
cd Pythomic
```

### Debian / Ubuntu

Instale Python, `pip` e o suporte a ambientes virtuais:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

### Arch Linux / derivados

```bash
sudo pacman -Syu
sudo pacman -S --needed python python-pip git
```

### Fedora

```bash
sudo dnf install -y python3 python3-pip git
```

### Criar o ambiente virtual e instalar as bibliotecas

**Caminho rápido (Linux/macOS):** rode o script de setup, que cria o venv,
instala as dependências, prepara o `.env` e inicia o servidor numa tacada só:

```bash
chmod +x iniciar.sh
./iniciar.sh
```

**Caminho manual** — estando na pasta do projeto, execute em qualquer uma das
distribuições acima:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Inicie a aplicação:

```bash
python run.py
```

Caso ocorra algum erro no Flask por causa de uma versão muito nova do Python
(por exemplo, 3.14):

```bash
python -m pip install --upgrade Flask
```

Acesse **http://localhost:5000** no navegador. Para parar o servidor, pressione
`Ctrl+C`. Para sair do ambiente virtual, execute:

```bash
deactivate
```

> **Testar no celular (opcional):** o servidor escuta em `0.0.0.0:5000`, então
> é possível acessá-lo de outro dispositivo na **mesma rede local** (útil para
> testar a interface mobile em um telefone real) em
> `http://<ip-do-computador>:5000`. Ele **não** fica exposto na internet
> pública.

### Quais bibliotecas são instaladas?

As dependências estão listadas em `requirements.txt`:

- `reactpy` / `reactpy[flask]` — ReactPy e sua integração com Flask (interface
  reativa em Python).
- `flask` — servidor web.
- `cryptography` — fornece criptografia autenticada para campos sensíveis.

O `sqlite3`, além de módulos como `os`, `secrets` e `hashlib`, faz parte da
biblioteca padrão do Python e não precisa ser instalado com `pip`.

---

## Banco de dados, segredo e arquivos locais

Na primeira execução, a aplicação cria o banco `database.db` (na raiz do
projeto) e a pasta `uploads/` para os arquivos enviados. O banco usa SQLite em
**modo WAL**, com `foreign_keys=ON`, `busy_timeout=5000` e todas as consultas
**parametrizadas** (`?`). Tabelas:

| Tabela         | Conteúdo                                                    |
|----------------|------------------------------------------------------------|
| `users`        | Contas (hashes de busca, campos criptografados, senha)     |
| `posts`        | Publicações (texto criptografado, mídia)                   |
| `followers`    | Relações de seguimento (follower → following)              |
| `likes`        | Curtidas (usuário × post)                                  |
| `post_views`   | Visualizações únicas por post (uma por usuário)            |

O **segredo mestre** é guardado em `.pythomic_secret` (permissão `0600`,
gerado com `secrets.token_urlsafe(32)`) caso a variável de ambiente
`PYTHOMIC_SECRET` não esteja definida.

**Guarde o segredo mestre com segurança.** Se perder ou substituir esse
segredo, os campos que foram criptografados com o segredo antigo ficam
**impossíveis de descriptografar**. Não compartilhe nem publique
`.pythomic_secret`, o banco de dados nem uploads privados.

Se `cryptography` não estiver disponível, o código tem um modo alternativo
baseado em **Base64** (com aviso de segurança impresso uma vez). **Base64 não é
criptografia**; instale as dependências do `requirements.txt` para usar o
recurso de criptografia previsto.

### Configuração por variáveis de ambiente

| Variável         | Efeito                                                                         |
|------------------|--------------------------------------------------------------------------------|
| `PYTHOMIC_SECRET`| Define o segredo mestre da criptografia (sobrepõe o arquivo `.pythomic_secret`). |
| `PYTHOMIC_DEBUG=1`| Liga o modo debug do Flask. **Apenas em desenvolvimento.**                    |
| `SMTP_HOST`      | Servidor SMTP do bot de email (ex.: `smtp.gmail.com`).                         |
| `SMTP_PORT`      | Porta (`587` p/ STARTTLS, `465` p/ SSL). Padrão: `587`.                        |
| `SMTP_USER`      | Login do remetente (ex.: `voce@gmail.com`).                                    |
| `SMTP_PASS`      | **Senha de app** do remetente (nunca a senha principal da conta).              |
| `SMTP_FROM`      | Remetente exibido (opcional; padrão = `SMTP_USER`).                            |
| `SMTP_SECURE`    | `starttls` (padrão) ou `ssl`.                                                  |

#### Bot de email (`pythomic/mailer.py`)

O `mailer.py` é o **bot** responsável por: (1) validar se o email é real
(`is_valid_email` — formato + registro MX do domínio), (2) gerar o **código de
verificação** do cadastro, (3) gerar a **nova senha** na recuperação e
(4) enviar tudo por **SMTP**. As credenciais vêm **só** das variáveis `SMTP_*`
acima — o Pythomic **não traz credenciais embutidas**.

**Sem** `SMTP_HOST`, o bot roda em **modo dev**: em vez de enviar, grava o
código/senha no log do servidor (stderr) e devolve o valor, para o fluxo de
cadastro e recuperação continuar testável sem um servidor de email. Em
produção, configure as variáveis `SMTP_*` com uma conta real (use **senha de
app**, nunca a senha principal — Gmail e outros provedores exigem isso).

Exemplo (Linux/macOS):

```bash
export PYTHOMIC_DEBUG=1
python run.py
```

Com SMTP real:

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=voce@gmail.com
export SMTP_PASS=sua_senha_de_app
python run.py
```

---

## 🔐 Segurança

A camada de segurança é a mesma da v1, agora organizada em módulos.

- **Criptografia de campos** (nome, email e texto do post) com **Fernet**
  (AES-128-CBC + HMAC-SHA256), derivada de um segredo mestre. As chaves de
  campo e de busca são separadas por contexto (`pythomic-field-enc-v1` e
  `pythomic-lookup-hmac-v1`). Sem o pacote `cryptography`, o app roda em modo
  de contingência (base64) e avisa.
- **Senhas** com **PBKDF2-HMAC-SHA256, 600.000 iterações**, salt aleatório de
  16 bytes. Verificação em tempo constante (`hmac.compare_digest`).
- **Hashes de busca** (`name_hash` / `email_hash`) com HMAC-SHA256 — unicidade
  sem guardar o dado em texto puro.
- **Rate limiting** em memória (thread-safe): **login** — 5 tentativas por
  15 min por nome de usuário; **cadastro** — 30 por hora (global);
  **recuperação de senha** — 5 por hora por email.
- **Verificação de email** no cadastro: `is_valid_email()` checa formato +
  registro MX do domínio (rejeita domínios que não existem; aceita todos os
  provedores reais), e o código de 6 dígitos enviado por email é a prova
  definitiva de que o email existe/recebe mensagens. Código expira em 15 min;
  o cadastro fica pendente até a confirmação.
- **Recuperação de senha** gera uma senha aleatória forte (CSPRNG, 12
  caracteres) e a envia só para o email da conta — a senha antiga é
  substituída no banco.
- **Exclusão de conta** apaga usuário, posts, curtidas, seguidores e
  visualizações (cascade + limpeza manual das tabelas sem FK), além dos
  arquivos de mídia do disco; exige **duas confirmações** + digitar `EXCLUIR`
  (irreversível).
- **Uploads** validados por **magic bytes** (não pelo tipo declarado), com
  whitelist **JPEG, PNG, GIF, WEBP e MP4** (avatars aceitam só imagem). Limite
  de **10 MB** (12 MB como `MAX_CONTENT_LENGTH` no Flask). Arquivos salvos com
  nome aleatório (`uuid4`).
- **Cabeçalhos de segurança** em todas as respostas: `X-Content-Type-Options:
  nosniff`, `X-Frame-Options: DENY`,
  `Referrer-Policy: strict-origin-when-cross-origin`,
  `Permissions-Policy: camera=(), microphone=(), geolocation=()`.
- **Cookies de sessão** com `HTTPOnly` e `SameSite=Lax`.
- **`safe_user()`** (em `database.py`) garante que o hash da senha e os campos
  criptografados nunca chegam à interface.

> **Nota:** não há cabeçalho **Content-Security-Policy** (CSP) definido. Para
> uma implantação real, considere adicionar um CSP adequado antes de expor o
> aplicativo.

### Segredo mestre
A criptografia deriva de um segredo mestre, obtido por prioridade:

1. Variável de ambiente `PYTHOMIC_SECRET`;
2. Arquivo `.pythomic_secret` (permissão `0600`), criado na primeira execução.

Guarde esse segredo: sem ele, os dados já criptografados no banco **não** podem
ser descriptografados.

### Debug
`PYTHOMIC_DEBUG=1` liga o modo debug do Flask — **use apenas em
desenvolvimento** (o debugger interativo do Werkzeug permite execução remota
de código se exposto em produção).

---

## Solução de problemas

### `python` ou `python3` não encontrado
Instale Python seguindo as instruções da sua distribuição. No Windows, tente
`py --version`.

### `No module named ...`
Confirme que o ambiente virtual está ativado e instale as dependências
novamente:

```bash
python -m pip install -r requirements.txt
```

No Windows CMD, use `py -m pip install -r requirements.txt` se esse for o
comando Python disponível.

### `externally-managed-environment` no Linux
Não force a instalação de pacotes no Python do sistema. Crie e ative o ambiente
virtual conforme as instruções acima e instale as bibliotecas dentro dele.

### Não consigo abrir a página
Confirme que o servidor continua em execução e que o terminal não mostrou um
erro. Abra `http://localhost:5000` no mesmo computador. Como o servidor faz
bind em `0.0.0.0:5000`, ele também é acessível de outros dispositivos na mesma
rede local, mas não na internet pública.

### A interface aparece minúscula no celular
Isso indica que a meta `viewport` não está sendo aplicada. Certifique-se de
rodar o projeto pela entrada `run.py` (que injeta o `<head>` customizado), e
não por um servidor que sirva só o HTML sem o head do ReactPy.

---

## Segurança (uso)

- Use apenas para **desenvolvimento local** enquanto o projeto não tiver sido
  revisado e preparado para produção.
- **Não ative o modo de depuração** (`PYTHOMIC_DEBUG=1`) em um servidor público.
- **Não publique** `.pythomic_secret`, credenciais, banco de dados ou conteúdo
  de usuários.
- A proteção por senha e a criptografia de campos **não substituem** uma
  auditoria de segurança, testes e configuração adequada para implantação.

## Licença

Nenhuma licença foi especificada neste repositório até o momento. Consulte o
responsável pelo projeto antes de reutilizar ou redistribuir o código.
