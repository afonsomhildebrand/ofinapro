# Documentacao Docker - OficinaPro

## 1. Objetivo

Este documento explica como executar o OficinaPro com Docker, usando um container para a aplicacao web e outro para o MySQL.

## 2. Arquivos Docker

- `Dockerfile`: cria a imagem da aplicacao Python.
- `docker-compose.yml`: orquestra os servicos `app` e `mysql`.
- `docker/entrypoint.sh`: aguarda o MySQL ficar disponivel, inicializa o banco e inicia o app.
- `.dockerignore`: evita enviar arquivos desnecessarios para o build.

## 3. Servicos

### app

Executa a aplicacao Flask com Gunicorn.

Porta publicada:

```text
5000:5000
```

Acesso:

```text
http://127.0.0.1:5000
```

### mysql

Executa MySQL 8.0 com dados persistidos em volume Docker.

Porta interna:

```text
3306
```

Porta externa padrao:

```text
3307
```

A porta externa foi definida como alternativa para evitar conflito com um MySQL local usando `3306`.

## 4. Variaveis principais

No `docker-compose.yml`, o app usa:

```text
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=oficinapro
MYSQL_PASSWORD=oficinapro123
MYSQL_DATABASE=oficina_pro
APP_PORT=5000
```

Para mudar a porta externa do MySQL, use no `.env`:

```text
MYSQL_HOST_PORT=3307
```

## 5. Subir o ambiente

Na pasta do projeto:

```bash
docker compose up -d --build
```

O primeiro build pode demorar porque baixa a imagem Python e instala dependencias.

## 6. Verificar status

```bash
docker compose ps
```

Resultado esperado:

```text
oficinapro_app     Up   0.0.0.0:5000->5000
oficinapro_mysql   Up   healthy   0.0.0.0:3307->3306
```

## 7. Acessar o sistema

Abra no navegador:

```text
http://127.0.0.1:5000
```

Credenciais iniciais:

```text
usuario: admin
senha: admin123
```

## 8. Conectar ao MySQL do container

De uma ferramenta externa no computador:

```text
host: 127.0.0.1
porta: 3307
banco: oficina_pro
usuario: oficinapro
senha: oficinapro123
```

Dentro da rede Docker, a aplicacao usa:

```text
host: mysql
porta: 3306
```

## 9. Logs

Logs do app:

```bash
docker compose logs -f app
```

Logs do MySQL:

```bash
docker compose logs -f mysql
```

## 10. Parar containers

```bash
docker compose down
```

Esse comando para os containers, mas preserva os dados no volume `mysql_data`.

## 11. Apagar banco e recriar do zero

Atencao: este comando apaga os dados do MySQL do projeto.

```bash
docker compose down -v
docker compose up -d --build
```

## 12. Backup simples

Gerar backup:

```bash
docker exec oficinapro_mysql mysqldump -uoficinapro -poficinapro123 oficina_pro > backup_oficina_pro.sql
```

Restaurar backup:

```bash
docker exec -i oficinapro_mysql mysql -uoficinapro -poficinapro123 oficina_pro < backup_oficina_pro.sql
```

## 13. Teste rapido

Depois de subir o ambiente:

```bash
docker compose ps
```

Verifique no navegador:

```text
http://127.0.0.1:5000/login
```

Verifique a tela de graficos:

```text
http://127.0.0.1:5000/graficos
```

Verifique o cadastro de usuarios:

```text
http://127.0.0.1:5000/usuarios
```

## 14. Problemas comuns

### Porta 5000 ocupada

Pare o processo local que esta usando a porta ou altere a publicacao do servico `app` no `docker-compose.yml`.

### Porta 3307 ocupada

Defina outra porta no `.env`:

```text
MYSQL_HOST_PORT=3310
```

Depois rode:

```bash
docker compose up -d
```

### MySQL demora para iniciar

O `healthcheck` do Compose aguarda o MySQL ficar saudavel antes de iniciar o app. Em maquinas mais lentas, isso pode levar alguns segundos.

### Login inicial nao funciona

Confirme se o container `app` executou a inicializacao:

```bash
docker compose logs app
```

Procure pela mensagem:

```text
Banco inicializado. Login: admin | Senha: admin123
```

## 15. Instalador standalone

O projeto tambem possui um pacote separado em:

```text
standalone_installer
```

Esse pacote contem uma copia do app, Docker Compose, scripts de instalacao, inicializacao, parada, status, backup, restauracao e teste.

Para distribuir para outro computador, use:

```text
OficinaPro_Standalone_Installer.zip
```

No computador de destino:

1. Instale e abra o Docker Desktop.
2. Extraia o ZIP.
3. Execute `OficinaPro.exe`.
4. Acesse `http://127.0.0.1:5000`.

### Executavel principal

Arquivo:

```text
standalone_installer\OficinaPro.exe
```

O executavel:

- Verifica se o Docker e o Docker Compose estao disponiveis.
- Cria `.env` a partir de `.env.example`, quando necessario.
- Executa `docker compose up -d --build` na pasta standalone.
- Aguarda a tela de login responder.
- Abre o navegador automaticamente.

Codigo-fonte do launcher:

```text
standalone_installer\launcher\OficinaProLauncher.cs
standalone_installer\launcher\OficinaProNuitkaLauncher.py
```

Script de build do executavel:

```text
standalone_installer\build_secure_executable.ps1
```

### Scripts auxiliares

- `Instalar_OficinaPro.cmd`: instala e inicia o ambiente.
- `build_secure_executable.ps1`: recria o executavel e aplica PyArmor, Nuitka e UPX quando disponiveis.
- `Iniciar_OficinaPro.cmd`: inicia containers ja criados.
- `Parar_OficinaPro.cmd`: para os containers preservando dados.
- `Status_OficinaPro.cmd`: mostra status e logs.
- `Testar_OficinaPro.cmd`: executa validacao rapida do pacote.
- `backup.ps1`: gera backup SQL.
- `restore.ps1`: restaura backup SQL.
- `uninstall.ps1`: remove containers e, opcionalmente, dados.

### Teste do pacote standalone

Na pasta `standalone_installer`, execute:

```bash
powershell.exe -ExecutionPolicy Bypass -File test_installation.ps1
```

Resultado esperado:

- Containers `oficinapro_standalone_app` e `oficinapro_standalone_mysql` em execucao.
- Aplicacao respondendo em `http://127.0.0.1:5000/login`.
- Login inicial disponivel com `admin` / `admin123`.
