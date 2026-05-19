# Instalacao do OficinaPro em 192.168.15.21

## Objetivo

Este pacote foi configurado para instalar o OficinaPro no computador servidor com IP:

```text
192.168.15.21
```

O sistema ficara acessivel na rede interna em:

```text
http://192.168.15.21:5000
```

## Requisitos no servidor

- Windows 10 ou superior.
- Docker Desktop instalado.
- Docker Desktop aberto e com o mecanismo Linux ativo.
- O computador deve estar usando o IP `192.168.15.21`.
- Porta `5000` liberada no firewall para acesso dos computadores da rede.
- Porta `3307` livre para acesso local ao MySQL do container, se necessario.

## Instalacao

1. Copie esta pasta para o computador `192.168.15.21`.
2. Abra o Docker Desktop e aguarde ele ficar pronto.
3. Execute como administrador, se precisar liberar a porta no firewall:

```text
Liberar_Firewall_OficinaPro.cmd
```

4. Execute:

```text
OficinaPro.exe
```

O executavel ira construir e iniciar os containers do app e do MySQL.

## Primeiro acesso

No proprio servidor:

```text
http://192.168.15.21:5000
```

Em outros computadores da rede:

```text
http://192.168.15.21:5000
```

Credenciais iniciais:

```text
Usuario: admin
Senha: admin123
```

## Validacao

Depois de iniciar, execute:

```powershell
powershell.exe -ExecutionPolicy Bypass -File test_installation.ps1
```

O teste valida containers, tela de login e tabelas principais do banco.

## Firewall do Windows

Se outros computadores nao conseguirem acessar, libere a porta `5000` no firewall do servidor.

Opcao pronta do pacote:

```text
Liberar_Firewall_OficinaPro.cmd
```

Comando manual no PowerShell como administrador:

```powershell
New-NetFirewallRule -DisplayName "OficinaPro Web 5000" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## Configuracao aplicada

Arquivo `.env`:

```text
APP_PUBLIC_HOST=192.168.15.21
APP_HOST_PORT=5000
MYSQL_HOST_PORT=3307
```

Se o IP do servidor mudar, altere `APP_PUBLIC_HOST` no arquivo `.env`.
