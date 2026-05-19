# Definicao Tecnica - OficinaPro

## 1. Arquitetura

O OficinaPro e uma aplicacao web monolitica desenvolvida em Python com Flask. A aplicacao renderiza paginas HTML no servidor e utiliza MySQL como banco de dados relacional. Em Docker, a aplicacao roda com Gunicorn e o banco roda em um container MySQL separado.

## 2. Tecnologias

- Linguagem: Python
- Framework web: Flask
- Autenticacao: Flask-Login
- ORM: Flask-SQLAlchemy
- Banco de dados: MySQL
- Driver MySQL: PyMySQL
- Servidor WSGI em container: Gunicorn
- Containers: Docker e Docker Compose
- Launcher standalone: C# com .NET Framework
- Build protegido opcional: PyArmor, Nuitka e UPX
- Templates: Jinja2
- Estilos: CSS
- Configuracao: python-dotenv com arquivo `.env`

## 3. Estrutura do projeto

```text
.
|-- app.py
|-- Dockerfile
|-- docker-compose.yml
|-- docker/
|   `-- entrypoint.sh
|-- requirements.txt
|-- .env.example
|-- README.md
|-- OficinaPro_Standalone_Installer.zip
|-- templates/
|   |-- base.html
|   |-- login.html
|   |-- dashboard.html
|   |-- charts.html
|   |-- clients.html
|   |-- manufacturers.html
|   |-- car_models.html
|   |-- cars.html
|   |-- employees.html
|   |-- parts.html
|   |-- services.html
|   `-- orders.html
|-- static/
|   `-- css/
|       `-- app.css
|-- docs/
|-- qa_tests/
`-- standalone_installer/
    |-- OficinaPro.exe
    |-- build_secure_executable.ps1
    |-- docker-compose.yml
    |-- .env.example
    |-- install.ps1
    |-- start.ps1
    |-- stop.ps1
    |-- status.ps1
    |-- test_installation.ps1
    |-- backup.ps1
    |-- restore.ps1
    |-- uninstall.ps1
    |-- launcher/
    |   |-- OficinaProLauncher.cs
    |   `-- OficinaProNuitkaLauncher.py
    `-- app/
```

## 4. Configuracao

As configuracoes sao lidas por variaveis de ambiente, preferencialmente por meio do arquivo `.env`.

Variaveis principais:

```text
SECRET_KEY=troque-esta-chave
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua-senha
MYSQL_DATABASE=oficina_pro
MYSQL_HOST_PORT=3307
APP_HOST=0.0.0.0
APP_PORT=5000
```

No Docker, `MYSQL_HOST_PORT` define a porta externa do MySQL no computador. Dentro da rede Docker, o app usa `mysql:3306`.

## 5. Banco de dados

Banco sugerido para execucao sem Docker:

```sql
CREATE DATABASE oficina_pro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

No Docker, o banco `oficina_pro` e criado automaticamente pelo container MySQL.

## 6. Modelo de dados

### 6.1 users

- id
- name
- username
- password_hash
- access_level
- is_admin
- is_active_user
- created_at

### 6.2 user_permissions

- id
- user_id
- menu_key
- can_view
- can_create
- can_edit
- can_delete

### 6.3 user_sessions

- id
- user_id
- login_at
- last_seen_at
- logout_at

### 6.4 activity_logs

- id
- user_id
- session_id
- menu_key
- action
- method
- path
- details
- created_at

### 6.5 clients

- id
- name
- phone
- email
- document
- created_at

### 6.6 manufacturers

- id
- name

### 6.7 car_models

- id
- manufacturer_id
- name

Relacionamento:

- Muitos modelos pertencem a um fabricante.

### 6.8 cars

- id
- client_id
- manufacturer_id
- model_id
- manufacturer
- model
- year
- plate
- mileage
- created_at

Relacionamento:

- Muitos carros pertencem a um cliente.
- Muitos carros usam um modelo vinculado a um fabricante.

### 6.9 employees

- id
- name
- role
- phone
- salary
- hourly_cost

### 6.10 parts

- id
- name
- sku
- stock
- cost
- price

### 6.11 services

- id
- name
- description
- base_price
- estimated_hours

### 6.12 service_orders

- id
- client_id
- car_id
- service_id
- employee_id
- status
- hours_spent
- charged_value
- created_at

Relacionamentos:

- Uma ordem pertence a um cliente.
- Uma ordem pertence a um carro.
- Uma ordem pertence a um servico.
- Uma ordem pertence a um funcionario.
- Uma ordem pode ter varias pecas.

### 6.13 order_parts

Tabela intermediaria para relacionamento muitos-para-muitos entre ordens e pecas.

- order_id
- part_id

## 7. Rotas principais

| Rota | Metodo | Descricao |
| --- | --- | --- |
| `/login` | GET/POST | Login do usuario |
| `/logout` | GET | Encerrar sessao |
| `/` | GET | Painel gerencial |
| `/graficos` | GET | Graficos mensais |
| `/usuarios` | GET/POST | Listar e cadastrar usuarios |
| `/financeiro` | GET | Painel financeiro, notas e cobrancas |
| `/ordens/<id>/emitir-nota` | POST | Registrar nota fiscal interna de ordem concluida |
| `/ordens/<id>/pagamentos` | POST | Gerar cobranca Pix, boleto, debito ou credito |
| `/pagamentos/<id>/baixar` | POST | Baixar pagamento como pago |
| `/notas/<id>/cancelar` | POST | Cancelar nota fiscal no controle interno |
| `/clientes` | GET/POST | Listar e cadastrar clientes |
| `/fabricantes` | GET/POST | Listar e cadastrar fabricantes |
| `/modelos` | GET/POST | Listar e cadastrar modelos por fabricante |
| `/carros` | GET/POST | Listar e cadastrar carros |
| `/funcionarios` | GET/POST | Listar e cadastrar funcionarios |
| `/pecas` | GET/POST | Listar e cadastrar pecas |
| `/servicos` | GET/POST | Listar e cadastrar servicos |
| `/ordens` | GET/POST | Listar e cadastrar ordens |
| `/<modulo>/<id>/editar` | GET/POST | Editar registros |
| `/excluir/<entity>/<item_id>` | POST | Excluir registro |

## 8. Autenticacao

O sistema utiliza Flask-Login. Todas as rotas internas exigem usuario autenticado. As senhas sao salvas como hash usando Werkzeug.

As permissoes sao controladas pela tabela `user_permissions`. Cada usuario pode receber permissao por menu para ver, incluir, editar e excluir. Usuarios administradores possuem permissao total.

Perfis padrao em `access_level`:

- `admin`: acesso total.
- `manager`: acesso total, exceto menu `users`.
- `employee`: acesso ao painel e ao menu de servicos.
- `custom`: usa as permissoes marcadas manualmente em `user_permissions`.

As sessoes de uso sao armazenadas em `user_sessions`, e as atividades executadas em `activity_logs`.

Usuario inicial criado pelo comando `flask --app app init-db`:

- Usuario: `admin`
- Senha: `admin123`

Recomendacao: alterar a senha inicial antes de usar em producao.

## 9. Calculos

### 9.1 Custo de pecas

Soma do custo unitario das pecas vinculadas a ordem.

### 9.2 Custo de mao de obra

```text
horas_gastas * custo_hora_funcionario
```

### 9.3 Custo total

```text
custo_pecas + custo_mao_de_obra
```

### 9.4 Lucro estimado

```text
valor_cobrado - custo_total
```

### 9.5 Tempo medio

```text
soma_horas_gastas / quantidade_ordens
```

### 9.6 Estatisticas mensais

Os graficos consideram os ultimos 6 meses:

- Servicos por mes: quantidade de ordens de servico abertas no mes.
- Carros cadastrados por mes: quantidade de carros cadastrados no mes.
- Atendimento a clientes: quantidade de ordens abertas no mes.

Os agrupamentos usam o campo `created_at`.

## 10. Execucao local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app app init-db
python app.py
```

## 11. Disponibilizacao na rede interna

O servidor Flask deve rodar em:

```text
0.0.0.0:5000
```

Outros computadores da rede acessam por:

```text
http://IP-DO-SERVIDOR:5000
```

## 12. Execucao com Docker

O projeto possui um `Dockerfile` para a aplicacao e um `docker-compose.yml` com os servicos `app` e `mysql`.

Comando de inicializacao:

```bash
docker compose up -d --build
```

Servicos:

- `app`: aplicacao Flask executada com Gunicorn, publicada em `5000`.
- `mysql`: banco MySQL 8 com volume persistente `mysql_data`.

O MySQL usa `3306` dentro da rede Docker e, por padrao, fica exposto no host pela porta alternativa `3307`.

O script `docker/entrypoint.sh` aguarda o MySQL ficar disponivel, executa `flask --app app init-db` e inicia a aplicacao.

## 13. Executavel standalone

O pacote `standalone_installer` permite executar o OficinaPro em um unico computador Windows sem instalar Python ou MySQL diretamente no sistema operacional.

Componentes principais:

- `OficinaPro.exe`: launcher principal para o usuario final.
- `build_secure_executable.ps1`: script para recriar o executavel com PyArmor, Nuitka e UPX quando as ferramentas estiverem disponiveis.
- `launcher/OficinaProLauncher.cs`: codigo-fonte do launcher em C#.
- `launcher/OficinaProNuitkaLauncher.py`: launcher Python preparado para compilacao com Nuitka.
- `docker-compose.yml`: sobe app e MySQL em containers.
- `app/`: copia da aplicacao Flask.
- Scripts PowerShell e CMD para instalacao, inicio, parada, status, teste, backup, restauracao e desinstalacao.

Fluxo do executavel:

1. Valida se esta na pasta correta do pacote standalone.
2. Cria `.env` a partir de `.env.example`, quando necessario.
3. Verifica disponibilidade do Docker e Docker Compose.
4. Executa `docker compose up -d --build`.
5. Aguarda a aplicacao responder em `http://127.0.0.1:5000/login`.
6. Abre o navegador em `http://127.0.0.1:5000`.

Requisito para uso:

- Windows com Docker Desktop instalado e em execucao.

Pacote para distribuicao:

```text
OficinaPro_Standalone_Installer.zip
```

## 14. Recomendacoes para ambiente real

- Usar senhas fortes no MySQL e no usuario administrador.
- Alterar `SECRET_KEY`.
- Alterar a senha do usuario `admin`.
- Configurar firewall liberando apenas as portas necessarias na rede interna.
- Fazer backup periodico do banco.
- Manter o volume MySQL em disco confiavel.
- Ajustar usuarios e senhas no `docker-compose.yml` ou em variaveis de ambiente antes de usar definitivamente.
