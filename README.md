# OficinaPro

Sistema web em Python para controle de oficina mecanica com MySQL e login.

## Recursos

- Login de usuarios
- Cadastro de usuarios com permissoes por menu
- Controle de direito de visualizacao, inclusao, edicao e exclusao
- Registro de tempo de uso e atividades executadas
- Clientes
- Fabricantes de carros
- Modelos de carros vinculados aos fabricantes
- Carros por cliente, fabricante, modelo e ano
- Funcionarios com cargo, salario e custo por hora
- Pecas com estoque, custo e preco de venda
- Servicos disponiveis
- Ordens de servico com cliente, carro, servico, funcionario, pecas, custo, valor e tempo gasto
- Financeiro com notas fiscais internas para servicos concluidos
- Pagamentos por Pix, boleto, debito e credito, com baixa de cobrancas
- Painel com faturamento, custo em pecas, lucro estimado, tempo medio, media por servico e servicos por funcionario
- Graficos mensais de servicos, carros cadastrados e atendimento a clientes
- Criacao, edicao e exclusao dos principais cadastros

> Observacao: notas fiscais, boletos e cobrancas Pix sao registrados como controle interno. Para emissao fiscal ou bancaria oficial, conecte o sistema a um provedor de NFS-e/NF-e, banco ou gateway de pagamento.

## Preparar o MySQL

Crie o banco:

```sql
CREATE DATABASE oficina_pro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Configurar

Copie `.env.example` para `.env` e ajuste usuario, senha, host e banco do MySQL.

## Instalar e iniciar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
python app.py
```

## Iniciar com Docker

Com Docker Desktop instalado, rode:

```bash
docker compose up -d --build
```

Depois acesse:

```text
http://localhost:5000
```

Login inicial:

- Usuario: `admin`
- Senha: `admin123`

O Docker Compose cria dois servicos:

- `app`: aplicacao web OficinaPro em Python.
- `mysql`: banco MySQL 8 com dados persistidos no volume `mysql_data`.

Por padrao, o MySQL do Docker fica exposto no computador pela porta alternativa `3307`, evitando conflito com um MySQL local na porta `3306`.

Conexao externa ao MySQL do container:

```text
host: 127.0.0.1
porta: 3307
banco: oficina_pro
usuario: oficinapro
senha: oficinapro123
```

Para trocar a porta externa, defina `MYSQL_HOST_PORT` no `.env`.

Para detalhes completos, consulte `docs/05-documentacao-docker.md`.

## Instalador standalone

Foi criado um pacote separado em `standalone_installer` para rodar app + MySQL em um unico computador com Docker Desktop.

Arquivo compactado para distribuicao:

```text
OficinaPro_Standalone_Installer.zip
```

Dentro da pasta, execute:

```text
OficinaPro.exe
```

O executavel verifica Docker/Docker Compose, inicia app + MySQL, aguarda a tela de login e abre o navegador automaticamente.

Tambem existem scripts auxiliares na pasta, incluindo instalacao, inicio, parada, status, teste, backup, restauracao e desinstalacao.

Para recriar o executavel com o fluxo de protecao:

```bash
powershell.exe -ExecutionPolicy Bypass -File standalone_installer\build_secure_executable.ps1
```

O script usa PyArmor + Nuitka quando instalados, aplica UPX quando `upx.exe` esta disponivel e usa o launcher C# como fallback quando essas ferramentas nao existem no computador.

Para parar:

```bash
docker compose down
```

Para apagar tambem os dados do banco:

```bash
docker compose down -v
```

## Testar

Depois de instalar as dependencias, rode:

```bash
.venv\Scripts\python.exe -c "import tests.test_smoke as t; tests=[t.test_login_and_dashboard_render,t.test_private_route_redirects_to_login,t.test_create_client_car_employee_part_service_and_order]; [fn() for fn in tests]; print(f'{len(tests)} tests ok')"
```

Suite completa de QA:

```bash
.venv\Scripts\python.exe qa_tests\run_all_app_tests.py
```

Testes de execucao Docker:

```bash
powershell.exe -ExecutionPolicy Bypass -File qa_tests\docker_execution_tests.ps1
```

Teste rapido do pacote standalone:

```bash
powershell.exe -ExecutionPolicy Bypass -File standalone_installer\test_installation.ps1
```

Os relatorios detalhados sao gerados em `qa_tests/reports`.

## Acesso na rede interna

O app roda por padrao em `0.0.0.0:5000`. Em outro computador da mesma rede, acesse:

```text
http://IP-DO-COMPUTADOR:5000
```

Troque `IP-DO-COMPUTADOR` pelo IP da maquina onde o sistema esta rodando.

## Documentacao

- `docs/01-definicao-do-projeto.md`
- `docs/02-definicao-tecnica.md`
- `docs/03-documento-de-testes.md`
- `docs/04-manual-do-usuario.md`
- `docs/05-documentacao-docker.md`
- `docs/06-build-protecao-executavel.md`
- `docs/07-manual-instalacao-pacote-standalone.md`
- `docs/08-manual-do-usuario-final.md`
- `qa_tests/README.md`
