# OficinaPro Linux - 192.168.15.21

Pacote Linux para instalar o OficinaPro no servidor:

```text
192.168.15.21
```

## Requisitos

- Linux com Docker instalado.
- Docker Compose plugin instalado.
- Usuario com permissao para executar Docker.
- Porta `5000` liberada no firewall do servidor.

## Instalar

```bash
chmod +x *.sh
./install.sh
```

## Acessar

```text
http://192.168.15.21:5000
```

Login inicial:

```text
admin / admin123
```

## Testar

```bash
./test_installation.sh
```

## Parar

```bash
./stop.sh
```

## Iniciar novamente

```bash
./start.sh
```

## Status e logs

```bash
./status.sh
```

## Backup

```bash
./backup.sh
```

## Restaurar backup

```bash
./restore.sh backups/arquivo.sql
```
