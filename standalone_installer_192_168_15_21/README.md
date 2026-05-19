# OficinaPro Standalone Installer

Pacote standalone para rodar o OficinaPro em um unico computador com app web e MySQL.

## Requisito

- Windows com Docker Desktop instalado e em execucao.

O pacote inclui a aplicacao e a configuracao do MySQL em containers. Nao e necessario instalar Python ou MySQL diretamente no Windows.

## Arquitetura do pacote

- Frontend entregue: aplicacao web acessada pelo navegador.
- Execucao: API web local em Docker, acessivel em `http://127.0.0.1:5000`.
- Banco: MySQL 8 em container Docker.
- Protecao: build preparado para PyArmor, Nuitka e UPX quando essas ferramentas estiverem instaladas.

## Instalar

Opcao recomendada:

```text
OficinaPro.exe
```

Esse executavel inicia o app + MySQL pelo Docker Compose e abre o navegador automaticamente.

Fluxo executado pelo `OficinaPro.exe`:

1. Verifica Docker e Docker Compose.
2. Cria `.env` a partir de `.env.example`, quando necessario.
3. Executa `docker compose up -d --build`.
4. Aguarda a tela de login responder.
5. Abre o navegador em `http://127.0.0.1:5000`.

Opcao por script:

Clique duas vezes em:

```text
Instalar_OficinaPro.cmd
```

Ou execute no PowerShell:

```powershell
powershell.exe -ExecutionPolicy Bypass -File install.ps1
```

## Acessar

Depois da instalacao:

```text
http://127.0.0.1:5000
```

Login inicial:

```text
admin / admin123
```

## Portas

- App web: `5000`
- MySQL externo: `3307`
- MySQL interno no Docker: `3306`

Conexao externa ao MySQL:

```text
host: 127.0.0.1
porta: 3307
banco: oficina_pro
usuario: oficinapro
senha: oficinapro123
```

## Scripts

- `Instalar_OficinaPro.cmd`: instala, cria containers e inicia o sistema.
- `OficinaPro.exe`: executavel principal para iniciar o sistema e abrir o navegador.
- `build_secure_executable.ps1`: recria o executavel usando PyArmor + Nuitka quando disponiveis, UPX quando instalado e C#/.NET Framework como fallback.
- `Iniciar_OficinaPro.cmd`: inicia containers ja instalados.
- `Parar_OficinaPro.cmd`: para containers preservando dados.
- `Status_OficinaPro.cmd`: mostra status e logs.
- `Testar_OficinaPro.cmd`: executa teste rapido do app e do MySQL.
- `backup.ps1`: gera backup SQL em `backups`.
- `restore.ps1`: restaura backup SQL.
- `uninstall.ps1`: remove containers; com `-RemoveData`, apaga tambem o volume de dados.

## Manuais incluidos

- `MANUAL_INSTALACAO.md`: passo a passo para instalar, iniciar, parar, testar, fazer backup, restaurar e desinstalar o pacote.
- `MANUAL_USUARIO.md`: orientacao de uso das telas do sistema, cadastros, ordens, permissoes, graficos e boas praticas.

## Recriar executavel

Execute:

```powershell
powershell.exe -ExecutionPolicy Bypass -File build_secure_executable.ps1
```

Se PyArmor e Nuitka estiverem instalados, o script ofusca `launcher\OficinaProNuitkaLauncher.py` e compila o resultado. Se apenas Nuitka estiver instalado, compila o launcher Python diretamente. Se Nuitka nao estiver instalado, usa `launcher\OficinaProLauncher.cs`.

Para ativar a ofuscacao:

```powershell
pip install pyarmor nuitka
```

Para compactacao opcional, instale UPX e deixe `upx.exe` no PATH.

## Testar o pacote

Execute:

```powershell
powershell.exe -ExecutionPolicy Bypass -File test_installation.ps1
```

Resultado esperado:

- Containers do app e MySQL em execucao.
- App respondendo em `http://127.0.0.1:5000/login`.
- Login inicial disponivel com `admin / admin123`.

## Alterar configuracoes

Edite o arquivo `.env` apos a primeira instalacao, ou copie `.env.example` para `.env` antes de instalar.

Variaveis principais:

```text
APP_HOST_PORT=5000
MYSQL_HOST_PORT=3307
MYSQL_ROOT_PASSWORD=root123
MYSQL_DATABASE=oficina_pro
MYSQL_USER=oficinapro
MYSQL_PASSWORD=oficinapro123
```

## Backup

```powershell
powershell.exe -ExecutionPolicy Bypass -File backup.ps1
```

## Restaurar backup

```powershell
powershell.exe -ExecutionPolicy Bypass -File restore.ps1 -BackupFile backups\oficina_pro_YYYYMMDD_HHMMSS.sql
```

## Desinstalar

Preservando dados:

```powershell
powershell.exe -ExecutionPolicy Bypass -File uninstall.ps1
```

Apagando dados:

```powershell
powershell.exe -ExecutionPolicy Bypass -File uninstall.ps1 -RemoveData
```
