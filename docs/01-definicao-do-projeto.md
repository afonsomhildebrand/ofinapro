# Definicao do Projeto - OficinaPro

## 1. Visao geral

O OficinaPro e um sistema web para controle de oficina mecanica, voltado para uso em rede interna. O objetivo e centralizar cadastros, ordens de servico, controle de pecas, funcionarios, veiculos, custos, tempos e indicadores operacionais.

## 2. Objetivos

- Controlar clientes e seus veiculos.
- Cadastrar fabricantes de carros.
- Cadastrar modelos de carros vinculados aos fabricantes.
- Cadastrar carros por fabricante, modelo, ano, placa e quilometragem.
- Gerenciar funcionarios, cargos, salario e custo por hora.
- Controlar pecas, estoque, custo e preco de venda.
- Cadastrar servicos disponiveis com preco padrao e tempo estimado.
- Registrar ordens de servico com cliente, carro, servico, funcionario responsavel, pecas usadas, valor cobrado e tempo gasto.
- Permitir editar e excluir registros cadastrados.
- Calcular custo por servico, lucro estimado, tempo medio e media por tipo de servico.
- Exibir produtividade por funcionario.
- Exibir graficos mensais de servicos, carros cadastrados e atendimento a clientes.
- Permitir acesso por login em ambiente web interno.
- Gerenciar usuarios com niveis de acesso por item de menu.
- Registrar notas fiscais internas para servicos concluidos.
- Gerar e acompanhar cobrancas por Pix, boleto, debito e credito.
- Controlar direitos de visualizacao, inclusao, edicao e exclusao.
- Registrar tempo de uso e atividades executadas por usuario.
- Disponibilizar execucao por Docker e pacote standalone com executavel Windows para uso em um unico computador.

## 3. Publico-alvo

- Donos e administradores de oficinas.
- Atendentes responsaveis por cadastro e abertura de ordens.
- Mecanicos e funcionarios responsaveis por execucao dos servicos.
- Gestores que precisam acompanhar custo, faturamento e produtividade.

## 4. Escopo funcional

### 4.1 Login

O sistema deve exigir autenticacao para acesso as telas internas.

### 4.2 Usuarios e permissoes

Permite cadastrar usuarios, definir perfil Administrador, Gerente, Funcionario ou Personalizado, controlar status ativo/inativo e selecionar permissoes por item de menu quando aplicavel.

Permissoes disponiveis:

- Ver
- Incluir
- Editar
- Excluir

O sistema registra sessoes de uso e atividades executadas.

Regras dos perfis:

- Administrador: acesso total, incluindo Usuarios do sistema.
- Gerente: acesso total, exceto Usuarios do sistema.
- Funcionario: acesso a Painel e Servicos.
- Personalizado: permissoes marcadas manualmente.

### 4.3 Clientes

Permite cadastrar clientes com nome, telefone, email e documento.

### 4.4 Fabricantes

Permite cadastrar fabricantes de carros para uso no cadastro de veiculos.

### 4.5 Modelos

Permite cadastrar modelos de carros vinculados a um fabricante.

### 4.6 Carros

Permite cadastrar carros vinculados a clientes, informando fabricante, modelo, ano, placa e quilometragem.

### 4.7 Funcionarios

Permite cadastrar funcionarios com nome, cargo, telefone, salario e custo por hora.

### 4.8 Pecas

Permite cadastrar pecas com nome, codigo, estoque, custo unitario e preco de venda.

### 4.9 Servicos

Permite cadastrar servicos disponiveis, com descricao, preco padrao e tempo estimado.

### 4.10 Ordens de servico

Permite registrar ordens vinculando cliente, carro, servico, funcionario, status, tempo gasto, valor cobrado e pecas utilizadas.

### 4.11 Painel gerencial

Apresenta indicadores de faturamento, custo de pecas, lucro estimado, tempo medio, medias por servico, servicos por funcionario e graficos mensais.

## 5. Escopo nao funcional

- Aplicacao web acessivel por navegador.
- Uso em rede interna.
- Banco de dados MySQL.
- Interface responsiva para desktop, notebook e tablet.
- Controle de acesso por usuario e senha.
- Dados persistidos em banco relacional.
- Instalacao simplificada por Docker Compose ou executavel standalone em Windows com Docker Desktop.

## 6. Regras de negocio

- Uma ordem de servico deve estar vinculada a um cliente, carro, servico e funcionario.
- Um carro deve pertencer a um cliente.
- Um modelo de carro deve estar vinculado a um fabricante.
- Registros cadastrados podem ser editados pelos usuarios autenticados.
- Usuarios comuns so podem acessar menus e acoes autorizadas.
- Administradores possuem acesso total.
- Cada sessao de usuario registra horario de login, ultima atividade e logout quando disponivel.
- O custo de uma ordem e formado pelo custo das pecas utilizadas mais o custo de mao de obra.
- O custo de mao de obra e calculado por horas gastas multiplicadas pelo custo hora do funcionario.
- O lucro estimado e calculado pelo valor cobrado menos o custo total.
- A media por servico considera todas as ordens vinculadas ao mesmo tipo de servico.
- O sistema inicia com um usuario administrador padrao apos inicializacao do banco.

## 7. Status das ordens

Os status previstos sao:

- Aberta
- Em andamento
- Concluida
- Cancelada

## 8. Entregaveis

- Aplicacao web em Python com Flask.
- Banco de dados MySQL.
- Sistema de login.
- Telas de cadastro e consulta.
- Painel gerencial.
- Documentacao do projeto.
- Manual do usuario.
- Documento de testes.
- Documentacao Docker.
- Suite de testes automatizados e relatorios em `qa_tests/reports`.
- Instalador standalone em `standalone_installer`.
- Executavel Windows `OficinaPro.exe`.
- Pacote compactado `OficinaPro_Standalone_Installer.zip`.

## 9. Premissas

- A oficina possui uma rede interna funcional.
- O computador servidor possui Python e acesso ao MySQL, ou Docker Desktop instalado.
- Para o executavel standalone, o Windows deve ter Docker Desktop instalado e em execucao.
- Os usuarios acessarao o sistema por navegador.
- A seguranca inicial sera baseada em login e senha.

## 10. Possiveis evolucoes futuras

- Controle de baixa automatica de estoque.
- Impressao de ordem de servico.
- Relatorios por periodo.
- Controle de pagamentos por Pix, boleto, debito e credito, com baixa manual.
- Emissao de notas fiscais internas para ordens concluidas, pronta para futura integracao com prefeitura/provedor fiscal.
- Backup automatico do banco.
- Historico completo por veiculo.
