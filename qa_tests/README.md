# QA Tests - OficinaPro

Este diretorio contem uma suite separada de testes unitarios, testes de implementacao e testes de execucao para o app e para o Docker.

## Arquivos

- `unit_app_tests.py`: testes unitarios de funcoes, calculos e modelos principais.
- `implementation_app_tests.py`: testes funcionais/de implementacao usando Flask test client e banco SQLite em memoria.
- `run_all_app_tests.py`: executa os testes Python acima.
- `docker_execution_tests.ps1`: valida build, containers, HTTP do app, login, pagina de graficos e banco MySQL no Docker.
- `local_execution_tests.ps1`: valida o app local ja em execucao em `http://127.0.0.1:5000`.
- `..\standalone_installer\test_installation.ps1`: valida o pacote standalone e o ambiente iniciado pelo `OficinaPro.exe`.

## Executar testes Python

Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe qa_tests\run_all_app_tests.py
```

Ao finalizar, gera um relatorio detalhado em:

```text
qa_tests/reports/python_app_tests_DATA_HORA.md
```

## Executar testes Docker

Na raiz do projeto:

```powershell
powershell.exe -ExecutionPolicy Bypass -File qa_tests\docker_execution_tests.ps1
```

Ao finalizar, gera um relatorio detalhado em:

```text
qa_tests/reports/docker_execution_tests_DATA_HORA.md
```

## Executar teste de app local

Com o app local ja iniciado:

```powershell
powershell.exe -ExecutionPolicy Bypass -File qa_tests\local_execution_tests.ps1
```

Ao finalizar, gera um relatorio detalhado em:

```text
qa_tests/reports/local_execution_tests_DATA_HORA.md
```

## Executar teste do pacote standalone

Com Docker Desktop em execucao e o pacote standalone disponivel:

```powershell
powershell.exe -ExecutionPolicy Bypass -File standalone_installer\test_installation.ps1
```

Esse teste valida containers, HTTP da aplicacao e disponibilidade do login no pacote standalone.

## Relatorios

Todos os relatorios ficam em `qa_tests/reports`.

Cada relatorio contem:

- Status geral.
- Inicio e fim da execucao.
- Duracao.
- Etapas executadas.
- Evidencias principais.
- Falhas ou erros, quando houver.

## Cobertura atual

Testes Python:

- Login e rotas protegidas.
- Renderizacao de painel, graficos e usuarios.
- Fluxo de criacao e edicao dos cadastros principais.
- Permissoes por menu e bloqueio de acesso.
- Registro de sessoes e atividades.
- Calculos de custo e lucro.
- Helpers de meses e graficos.
- Permissoes administrativas.
- Duracao de sessao.

Testes Docker:

- `docker compose config`.
- Build e subida dos containers.
- Status dos containers e porta MySQL `3307`.
- Login HTTP.
- Tela de graficos.
- Tela de usuarios.
- Tabelas MySQL esperadas.
- Registros de permissoes, sessoes e atividades.

Teste standalone:

- Execucao de app + MySQL pelo Docker Compose do pacote.
- Disponibilidade da tela de login.
- Validacao rapida dos containers e portas publicadas.
