# Manual de Instalacao do Pacote Standalone - OficinaPro

## 1. Objetivo

Este manual orienta a instalacao do pacote `OficinaPro_Standalone_Installer.zip`, que executa o sistema OficinaPro em um unico computador Windows usando Docker Desktop.

O pacote inclui:

- Aplicacao web OficinaPro.
- Banco MySQL em container.
- Executavel `OficinaPro.exe`.
- Scripts de instalacao, inicio, parada, status, teste, backup e restauracao.

## 2. Requisitos

Antes de instalar, confirme:

- Windows 10 ou superior.
- Docker Desktop instalado.
- Docker Desktop aberto e com o mecanismo Linux ativo.
- Porta `5000` livre para o sistema web.
- Porta `3307` livre para o MySQL do pacote.
- Permissao para executar arquivos `.exe`, `.cmd` e scripts PowerShell.

Nao e necessario instalar Python nem MySQL diretamente no Windows.

## 3. Arquivo de instalacao

Arquivo principal para distribuicao:

```text
OficinaPro_Standalone_Installer.zip
```

Pasta criada apos extrair:

```text
standalone_installer
```

## 4. Instalacao recomendada

1. Copie `OficinaPro_Standalone_Installer.zip` para o computador onde o sistema sera usado.
2. Extraia o arquivo ZIP.
3. Abra a pasta `standalone_installer`.
4. Confirme que o Docker Desktop esta aberto.
5. Execute:

```text
OficinaPro.exe
```

O executavel ira:

1. Verificar Docker e Docker Compose.
2. Criar o arquivo `.env`, se ele ainda nao existir.
3. Construir a imagem da aplicacao.
4. Iniciar os containers do app e do MySQL.
5. Aguardar a tela de login responder.
6. Abrir o navegador em `http://127.0.0.1:5000`.

## 5. Primeiro acesso

Endereco local:

```text
http://127.0.0.1:5000
```

Credenciais iniciais:

```text
Usuario: admin
Senha: admin123
```

Recomendacao: altere a senha inicial antes de usar o sistema em producao.

## 6. Instalacao por script

Se preferir usar o instalador por script, execute:

```text
Instalar_OficinaPro.cmd
```

Ou, pelo PowerShell:

```powershell
powershell.exe -ExecutionPolicy Bypass -File install.ps1
```

## 7. Iniciar o sistema depois da primeira instalacao

Opcao recomendada:

```text
OficinaPro.exe
```

Opcao por script:

```text
Iniciar_OficinaPro.cmd
```

Ou:

```powershell
powershell.exe -ExecutionPolicy Bypass -File start.ps1
```

## 8. Parar o sistema

Para parar os containers preservando os dados:

```text
Parar_OficinaPro.cmd
```

Ou:

```powershell
powershell.exe -ExecutionPolicy Bypass -File stop.ps1
```

## 9. Verificar status

Para consultar containers e logs:

```text
Status_OficinaPro.cmd
```

Ou:

```powershell
powershell.exe -ExecutionPolicy Bypass -File status.ps1
```

## 10. Testar a instalacao

Com o Docker Desktop aberto e o sistema iniciado:

```text
Testar_OficinaPro.cmd
```

Ou:

```powershell
powershell.exe -ExecutionPolicy Bypass -File test_installation.ps1
```

Resultado esperado:

- Container do app em execucao.
- Container do MySQL em execucao.
- Tela de login respondendo.
- Tabelas principais criadas no banco.

## 11. Configuracoes

O arquivo `.env` controla as portas e credenciais do pacote.

Variaveis principais:

```text
APP_HOST_PORT=5000
MYSQL_HOST_PORT=3307
MYSQL_ROOT_PASSWORD=root123
MYSQL_DATABASE=oficina_pro
MYSQL_USER=oficinapro
MYSQL_PASSWORD=oficinapro123
```

Para mudar a porta do sistema web, altere `APP_HOST_PORT`.

Para mudar a porta externa do MySQL, altere `MYSQL_HOST_PORT`.

Apos alterar o `.env`, reinicie o sistema.

## 12. Backup

Para gerar backup do banco:

```powershell
powershell.exe -ExecutionPolicy Bypass -File backup.ps1
```

Os backups sao gravados na pasta:

```text
backups
```

## 13. Restaurar backup

Para restaurar um backup:

```powershell
powershell.exe -ExecutionPolicy Bypass -File restore.ps1 -BackupFile backups\oficina_pro_YYYYMMDD_HHMMSS.sql
```

Antes de restaurar, confirme que o arquivo escolhido e o backup correto.

## 14. Desinstalar

Para remover os containers preservando os dados:

```powershell
powershell.exe -ExecutionPolicy Bypass -File uninstall.ps1
```

Para remover containers e apagar tambem os dados:

```powershell
powershell.exe -ExecutionPolicy Bypass -File uninstall.ps1 -RemoveData
```

Use `-RemoveData` somente quando tiver certeza de que os dados podem ser apagados.

## 15. Problemas comuns

### Docker nao encontrado

Verifique se o Docker Desktop esta instalado e aberto.

### Erro dockerDesktopLinuxEngine

O Docker Desktop esta fechado ou o mecanismo Linux nao iniciou. Abra o Docker Desktop e aguarde ele ficar pronto.

### Porta 5000 ocupada

Altere `APP_HOST_PORT` no arquivo `.env`, por exemplo:

```text
APP_HOST_PORT=5001
```

Depois acesse:

```text
http://127.0.0.1:5001
```

### Porta 3307 ocupada

Altere `MYSQL_HOST_PORT` no arquivo `.env`, por exemplo:

```text
MYSQL_HOST_PORT=3310
```

### Login nao funciona

Confirme se esta usando:

```text
admin / admin123
```

Se a senha ja foi alterada, use a senha nova cadastrada pelo administrador.

### Sistema nao abre no navegador

Acesse manualmente:

```text
http://127.0.0.1:5000
```

Se a porta foi alterada, use a porta configurada em `APP_HOST_PORT`.
