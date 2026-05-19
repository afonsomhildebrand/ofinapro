import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


APP_URL = os.environ.get("OFICINAPRO_URL", "http://127.0.0.1:5000")


def run(command, cwd, quiet=False):
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=False,
    )
    assert process.stdout is not None
    for line in process.stdout:
        if not quiet:
            print(line.rstrip())
    return process.wait()


def command_works(command, cwd):
    try:
        return run(command, cwd, quiet=True) == 0
    except OSError:
        return False


def wait_for_url(url, attempts=40):
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if 200 <= response.status < 500:
                    return True
        except urllib.error.URLError:
            time.sleep(3)
    return False


def read_env_value(env_file, key, fallback):
    if not env_file.exists():
        return fallback
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        line_key, value = line.split("=", 1)
        if line_key.strip().upper() == key.upper():
            value = value.strip().strip('"')
            return value or fallback
    return fallback


def main():
    base_dir = Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False) is False:
        base_dir = Path(__file__).resolve().parents[1]

    compose_file = base_dir / "docker-compose.yml"
    env_example = base_dir / ".env.example"
    env_file = base_dir / ".env"

    print("OficinaPro - Inicializador protegido")
    print("====================================")
    print()

    if not compose_file.exists():
        print("ERRO: docker-compose.yml nao encontrado na pasta do executavel.")
        input("Pressione ENTER para sair.")
        return 1

    if not env_file.exists() and env_example.exists():
        shutil.copyfile(env_example, env_file)
        print("Arquivo .env criado.")

    app_port = read_env_value(env_file, "APP_HOST_PORT", "5000")
    public_host = read_env_value(env_file, "APP_PUBLIC_HOST", "127.0.0.1")
    local_url = f"http://127.0.0.1:{app_port}"
    public_url = os.environ.get("OFICINAPRO_URL", f"http://{public_host}:{app_port}")

    if not command_works(["docker", "--version"], base_dir):
        print("ERRO: Docker nao foi encontrado.")
        print("Instale e abra o Docker Desktop antes de executar o OficinaPro.")
        input("Pressione ENTER para sair.")
        return 1

    if not command_works(["docker", "compose", "version"], base_dir):
        print("ERRO: Docker Compose nao foi encontrado.")
        input("Pressione ENTER para sair.")
        return 1

    print("Iniciando app e MySQL...")
    exit_code = run(["docker", "compose", "up", "-d", "--build"], base_dir)
    if exit_code != 0:
        print("ERRO: nao foi possivel iniciar os containers.")
        input("Pressione ENTER para sair.")
        return exit_code

    print("Aguardando aplicacao responder...")
    if not wait_for_url(f"{local_url}/login"):
        print("ERRO: aplicacao nao respondeu em tempo habil.")
        print("Use Status_OficinaPro.cmd para consultar os logs.")
        input("Pressione ENTER para sair.")
        return 1

    print("OficinaPro iniciado com sucesso.")
    print(f"Acesso local: {local_url}")
    print(f"Acesso na rede: {public_url}")
    print("Login inicial: admin / admin123")
    webbrowser.open(public_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
