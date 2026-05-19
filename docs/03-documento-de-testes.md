# Documento de Testes - OficinaPro

## 1. Objetivo

Este documento define os testes funcionais, tecnicos e de validacao para o sistema OficinaPro.

## 2. Ambiente de testes

- Sistema operacional: Windows
- Navegador: Chrome, Edge ou Firefox
- Python instalado
- MySQL instalado e ativo ou Docker Desktop instalado
- Para testar o executavel standalone: Docker Desktop instalado e em execucao
- Banco criado: `oficina_pro`, quando rodar sem Docker
- Aplicacao executando em `http://127.0.0.1:5000`

## 3. Preparacao

1. Criar banco MySQL:

```sql
CREATE DATABASE oficina_pro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Configurar `.env`.

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Inicializar banco:

```bash
flask --app app init-db
```

5. Iniciar aplicacao:

```bash
python app.py
```

## 4. Credenciais iniciais

- Usuario: `admin`
- Senha: `admin123`

## 5. Casos de teste funcionais

### CT-001 - Login com credenciais validas

Pre-condicao: banco inicializado.

Passos:

1. Acessar `/login`.
2. Informar usuario `admin`.
3. Informar senha `admin123`.
4. Clicar em Entrar.

Resultado esperado:

- O sistema deve abrir o painel principal.

### CT-002 - Login com credenciais invalidas

Passos:

1. Acessar `/login`.
2. Informar usuario ou senha incorretos.
3. Clicar em Entrar.

Resultado esperado:

- O sistema deve exibir mensagem de usuario ou senha invalidos.
- O acesso ao painel deve ser negado.

### CT-003 - Bloqueio de acesso sem login

Passos:

1. Abrir uma janela anonima.
2. Acessar `/clientes`.

Resultado esperado:

- O sistema deve redirecionar para a tela de login.

### CT-004 - Cadastro de cliente

Passos:

1. Fazer login.
2. Acessar Clientes.
3. Informar nome, telefone, email e documento.
4. Clicar em Salvar.

Resultado esperado:

- Cliente deve aparecer na lista de clientes.

### CT-005 - Cadastro de usuario e permissoes

Passos:

1. Fazer login como administrador.
2. Acessar Usuarios.
3. Informar nome, usuario e senha.
4. Marcar permissoes por item de menu.
5. Clicar em Salvar.

Resultado esperado:

- Usuario deve aparecer na lista.
- Permissoes devem controlar os menus e acoes disponiveis.
- Tempo de uso e atividades devem aparecer vinculados ao usuario.

### CT-006 - Cadastro de fabricante

Passos:

1. Acessar Fabricantes.
2. Informar nome do fabricante.
3. Clicar em Salvar.

Resultado esperado:

- Fabricante deve aparecer na lista.
- Fabricante deve ficar disponivel no cadastro de carros.

### CT-007 - Cadastro de modelo

Pre-condicao:

- Existir ao menos um fabricante cadastrado.

Passos:

1. Acessar Modelos.
2. Selecionar fabricante.
3. Informar nome do modelo.
4. Clicar em Salvar.

Resultado esperado:

- Modelo deve aparecer na lista vinculado ao fabricante correto.
- Modelo deve ficar disponivel no cadastro de carros ao selecionar o fabricante.

### CT-008 - Cadastro de carro

Pre-condicao:

- Existir ao menos um cliente cadastrado.
- Existir ao menos um fabricante cadastrado.
- Existir ao menos um modelo vinculado ao fabricante.

Passos:

1. Acessar Carros.
2. Selecionar cliente.
3. Selecionar fabricante.
4. Selecionar modelo.
5. Informar ano, placa e quilometragem.
6. Clicar em Salvar.

Resultado esperado:

- Carro deve aparecer na lista vinculado ao cliente correto.

### CT-009 - Cadastro de funcionario

Passos:

1. Acessar Funcionarios.
2. Informar nome, cargo, telefone, salario e custo hora.
3. Clicar em Salvar.

Resultado esperado:

- Funcionario deve aparecer na lista.

### CT-010 - Cadastro de peca

Passos:

1. Acessar Pecas.
2. Informar nome, codigo, estoque, custo e preco de venda.
3. Clicar em Salvar.

Resultado esperado:

- Peca deve aparecer na lista com estoque e valores corretos.

### CT-011 - Cadastro de servico

Passos:

1. Acessar Servicos.
2. Informar nome, descricao, preco padrao e tempo estimado.
3. Clicar em Salvar.

Resultado esperado:

- Servico deve aparecer na lista.

### CT-012 - Cadastro de ordem de servico

Pre-condicao:

- Existir cliente.
- Existir carro.
- Existir funcionario.
- Existir servico.
- Existir peca opcional.

Passos:

1. Acessar Ordens.
2. Selecionar cliente, carro, servico e funcionario.
3. Escolher status.
4. Informar horas gastas.
5. Informar valor cobrado.
6. Selecionar pecas usadas.
7. Clicar em Salvar.

Resultado esperado:

- Ordem deve aparecer na tabela.
- Custo deve considerar pecas e custo hora do funcionario.
- Valor cobrado deve ser exibido corretamente.

### CT-013 - Painel gerencial

Pre-condicao: existir ao menos uma ordem cadastrada.

Passos:

1. Acessar Painel.

Resultado esperado:

- Faturamento deve somar os valores cobrados.
- Custo em pecas deve somar o custo das pecas usadas.
- Lucro estimado deve ser faturamento menos custo total.
- Tempo medio deve considerar as horas gastas nas ordens.
- Media por servico deve ser exibida.
- Servicos por funcionario deve ser exibido.
- Graficos mensais de servicos, carros e atendimento a clientes devem ser exibidos.

### CT-014 - Tela de graficos

Pre-condicao: usuario autenticado.

Passos:

1. Acessar Graficos no menu lateral.
2. Conferir os paineis mensais.

Resultado esperado:

- A tela `/graficos` deve abrir.
- Os graficos de servicos por mes, carros cadastrados por mes e atendimento a clientes devem aparecer.

### CT-015 - Exclusao de registro

Passos:

1. Acessar qualquer modulo com registros.
2. Clicar em Excluir.

Resultado esperado:

- Registro deve ser removido da lista.

Observacao:

- Registros vinculados a outros dados podem ser bloqueados pelo banco dependendo do relacionamento.

### CT-016 - Edicao de registro

Passos:

1. Acessar um modulo com registros cadastrados.
2. Clicar em Editar.
3. Alterar um ou mais campos.
4. Clicar em Atualizar.

Resultado esperado:

- O sistema deve salvar as alteracoes.
- O registro atualizado deve aparecer na lista.

## 6. Testes tecnicos

### Suites automatizadas

O projeto possui uma suite dedicada em `qa_tests`.

Testes unitarios e de implementacao:

```bash
.venv\Scripts\python.exe qa_tests\run_all_app_tests.py
```

Relatorio gerado:

```text
qa_tests/reports/python_app_tests_DATA_HORA.md
```

Testes de execucao Docker:

```bash
powershell.exe -ExecutionPolicy Bypass -File qa_tests\docker_execution_tests.ps1
```

Relatorio gerado:

```text
qa_tests/reports/docker_execution_tests_DATA_HORA.md
```

Teste de app em execucao local:

```bash
powershell.exe -ExecutionPolicy Bypass -File qa_tests\local_execution_tests.ps1
```

Relatorio gerado:

```text
qa_tests/reports/local_execution_tests_DATA_HORA.md
```

Cobertura adicional da suite:

- Permissoes por menu e acao.
- Bloqueio de acesso sem permissao.
- Sessoes de usuario.
- Logs de atividades.
- Tela de usuarios.
- Validacao das tabelas `user_permissions`, `user_sessions` e `activity_logs`.
- Cadastro de modelos de carros vinculados aos fabricantes.
- Validacao da tabela `car_models`.

### TT-001 - Validacao de sintaxe Python

Comando:

```bash
python -m py_compile app.py
```

Resultado esperado:

- Comando deve finalizar sem erros.

### TT-002 - Instalacao de dependencias

Comando:

```bash
pip install -r requirements.txt
```

Resultado esperado:

- Todas as dependencias devem ser instaladas sem erro.

### TT-003 - Conexao com MySQL

Passos:

1. Configurar `.env`.
2. Rodar `flask --app app init-db`.

Resultado esperado:

- Tabelas devem ser criadas no banco.
- Usuario admin deve ser criado.

### TT-004 - Acesso em rede interna

Passos:

1. Iniciar aplicacao no computador servidor.
2. Identificar IP do servidor.
3. Acessar de outro computador: `http://IP-DO-SERVIDOR:5000`.

Resultado esperado:

- Tela de login deve abrir no outro computador.

### TT-005 - Inicializacao com Docker

Comando:

```bash
docker compose up -d --build
```

Resultado esperado:

- Container `mysql` deve ficar saudavel.
- Container `app` deve inicializar o banco.
- Sistema deve abrir em `http://localhost:5000`.
- MySQL deve ser exposto no host pela porta `3307`.
- Login `admin` / `admin123` deve funcionar.

### TT-006 - Persistencia do MySQL no Docker

Passos:

1. Iniciar com `docker compose up -d --build`.
2. Cadastrar um cliente.
3. Parar com `docker compose down`.
4. Iniciar novamente com `docker compose up -d`.
5. Acessar Clientes.

Resultado esperado:

- Cliente cadastrado deve continuar salvo.

### TT-007 - Validacao da porta MySQL alternativa

Passos:

1. Iniciar com `docker compose up -d --build`.
2. Executar `docker compose ps`.

Resultado esperado:

- O servico `mysql` deve aparecer como `healthy`.
- A porta deve aparecer como `0.0.0.0:3307->3306/tcp`.

### TT-008 - Execucao pelo executavel standalone

Pre-condicao:

- Docker Desktop instalado e em execucao.
- Porta `5000` livre ou configurada no `.env` do pacote standalone.

Passos:

1. Abrir a pasta `standalone_installer`.
2. Executar `OficinaPro.exe`.
3. Aguardar o build e a subida dos containers.
4. Confirmar abertura do navegador em `http://127.0.0.1:5000`.
5. Acessar `/login` e entrar com `admin` / `admin123`.
6. Executar o teste rapido:

```bash
powershell.exe -ExecutionPolicy Bypass -File standalone_installer\test_installation.ps1
```

Resultado esperado:

- O executavel deve iniciar app e MySQL pelo Docker Compose.
- O navegador deve abrir automaticamente.
- A tela de login deve responder.
- O teste `test_installation.ps1` deve concluir sem falhas.

## 7. Criterios de aceite

- Usuario consegue acessar o sistema com login.
- Usuario nao autenticado nao acessa telas internas.
- Cadastros principais funcionam.
- Ordens de servico podem ser registradas.
- Custos e indicadores aparecem no painel.
- Sistema pode ser acessado por outro computador na rede interna.
- Sistema pode ser iniciado pelo `OficinaPro.exe` no pacote standalone.

## 8. Riscos e pontos de atencao

- Falta de Python no PATH pode impedir execucao dos comandos.
- Firewall do Windows pode bloquear acesso externo a porta 5000.
- Credenciais incorretas do MySQL impedem inicializacao.
- Docker Desktop fechado impede uso do Docker e do executavel standalone.
- Exclusao de registros vinculados pode gerar erro se houver dependencias.
- O servidor de desenvolvimento do Flask nao e recomendado para producao pesada.
