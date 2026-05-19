# Manual do Usuario - OficinaPro

## 1. Acesso ao sistema

Abra o navegador e acesse o endereco informado pelo responsavel tecnico.

Em uso local:

```text
http://127.0.0.1:5000
```

Em rede interna:

```text
http://IP-DO-SERVIDOR:5000
```

### Uso pelo executavel standalone

Quando o sistema for usado em um unico computador pelo pacote standalone:

1. Instale e abra o Docker Desktop.
2. Extraia o arquivo `OficinaPro_Standalone_Installer.zip`.
3. Abra a pasta extraida.
4. Execute `OficinaPro.exe`.
5. Aguarde o navegador abrir em `http://127.0.0.1:5000`.

O executavel inicia a aplicacao e o MySQL automaticamente por Docker. Nao e necessario instalar Python ou MySQL diretamente no Windows.

## 2. Login

Na tela inicial, informe usuario e senha.

Credencial inicial:

- Usuario: `admin`
- Senha: `admin123`

Importante: a senha inicial deve ser alterada antes do uso definitivo.

## 3. Menu principal

O menu lateral possui as seguintes opcoes:

- Painel
- Graficos
- Cadastros
  - Clientes
  - Fabricantes
  - Modelos
  - Carros
  - Funcionarios
  - Pecas
  - Servicos
  - Usuarios do sistema
- Ordens

## 4. Painel

O painel apresenta um resumo da oficina:

- Faturamento total.
- Custo em pecas.
- Lucro estimado.
- Tempo medio dos servicos.
- Media por servico.
- Servicos por funcionario.
- Graficos mensais de servicos, carros cadastrados e atendimento a clientes.

Use esta tela para acompanhar o desempenho geral da oficina.

## 5. Graficos

A tela Graficos apresenta estatisticas mensais dos ultimos meses:

- Servicos por mes.
- Carros cadastrados por mes.
- Atendimentos a clientes.
- Total de clientes cadastrados.
- Clientes unicos atendidos.

Use essa tela para acompanhar volume de trabalho e movimento da oficina por mes.

## 6. Cadastro de usuarios do sistema

O cadastro de usuarios do sistema fica dentro de Cadastros e so pode ser acessado por administradores.

## 7. Financeiro

Acesse Financeiro para consultar servicos concluidos, emitir a nota fiscal interna da ordem e gerar cobrancas por Pix, boleto, debito ou credito.

Para emitir uma nota, a ordem precisa estar com status Concluida. Clique em Emitir nota na linha da ordem. O sistema cria um numero interno e registra cliente, documento, servico, valor e imposto estimado.

Para gerar cobranca, escolha o metodo de pagamento, confirme o valor e informe vencimento quando necessario. A cobranca fica pendente ate ser baixada em Pagamentos.

As notas e cobrancas sao controles internos. A emissao oficial fiscal ou bancaria exige integracao com prefeitura, banco ou gateway.

Perfis padrao:

- Administrador: acessa todos os menus e acoes.
- Gerente: acessa todos os menus e acoes, exceto Usuarios do sistema.
- Funcionario: acessa Painel e Servicos.
- Personalizado: permite marcar permissoes manualmente por menu.

Para cadastrar um usuario:

1. Clique em Cadastros.
2. Clique em Usuarios do sistema.
2. Informe nome.
3. Informe usuario.
4. Informe senha.
5. Selecione o perfil de acesso.
6. Marque se o usuario esta ativo.
7. Configure permissoes por menu, quando usar o perfil Personalizado.
8. Clique em Salvar.

Permissoes disponiveis:

- Ver: permite acessar o menu.
- Incluir: permite criar registros.
- Editar: permite alterar registros.
- Excluir: permite remover registros.

A tela tambem mostra tempo de uso, quantidade de sessoes, atividades executadas e ultimas atividades.

## 7. Cadastro de clientes

Para cadastrar um cliente:

1. Clique em Clientes.
2. Informe nome.
3. Informe telefone.
4. Informe email, se houver.
5. Informe documento, se houver.
6. Clique em Salvar.

O cliente cadastrado aparecera na lista da mesma tela.

## 8. Cadastro de fabricantes

Para cadastrar um fabricante:

1. Clique em Fabricantes.
2. Informe o nome do fabricante.
3. Clique em Salvar.

O fabricante cadastrado ficara disponivel na tela de cadastro de carros.

## 9. Cadastro de modelos

Para cadastrar um modelo:

1. Clique em Modelos.
2. Selecione o fabricante.
3. Informe o nome do modelo.
4. Clique em Salvar.

O modelo cadastrado ficara disponivel na tela de cadastro de carros somente para o fabricante selecionado.

## 10. Cadastro de carros

Para cadastrar um carro:

1. Clique em Carros.
2. Selecione o cliente dono do carro.
3. Selecione o fabricante.
4. Selecione o modelo vinculado ao fabricante.
5. Informe ano.
6. Informe placa.
7. Informe quilometragem.
8. Clique em Salvar.

Cada carro fica vinculado a um cliente.

## 11. Cadastro de funcionarios

Para cadastrar um funcionario:

1. Clique em Funcionarios.
2. Informe nome.
3. Informe cargo.
4. Informe telefone.
5. Informe salario.
6. Informe custo por hora.
7. Clique em Salvar.

O salario e informativo para controle interno. O custo por hora sera usado para calcular o custo de mao de obra nas ordens de servico.

## 12. Cadastro de pecas

Para cadastrar uma peca:

1. Clique em Pecas.
2. Informe nome da peca.
3. Informe codigo.
4. Informe quantidade em estoque.
5. Informe custo da peca.
6. Informe preco de venda.
7. Clique em Salvar.

O custo da peca sera usado no calculo das ordens de servico.

## 13. Cadastro de servicos

Para cadastrar um servico disponivel:

1. Clique em Servicos.
2. Informe nome do servico.
3. Informe descricao.
4. Informe preco padrao.
5. Informe tempo estimado.
6. Clique em Salvar.

Exemplos de servicos:

- Troca de oleo
- Revisao de freios
- Diagnostico eletrico
- Alinhamento
- Balanceamento

## 14. Criar ordem de servico

Para criar uma ordem:

1. Clique em Ordens.
2. Selecione o cliente.
3. Selecione o carro.
4. Selecione o servico.
5. Selecione o funcionario responsavel.
6. Escolha o status.
7. Informe horas gastas.
8. Informe valor cobrado.
9. Selecione as pecas usadas, se houver.
10. Clique em Salvar.

A ordem aparecera na tabela com cliente, carro, servico, funcionario, status, tempo, custo e valor.

## 15. Status da ordem

Os status disponiveis sao:

- Aberta: ordem criada, ainda nao iniciada.
- Em andamento: servico em execucao.
- Concluida: servico finalizado.
- Cancelada: ordem cancelada.

## 16. Entendendo os custos

O sistema calcula o custo da ordem usando:

```text
custo das pecas + custo da mao de obra
```

O custo da mao de obra e calculado por:

```text
horas gastas * custo por hora do funcionario
```

O lucro estimado e:

```text
valor cobrado - custo total
```

## 17. Excluir registros

Em cada modulo, clique em Excluir para remover um registro.

Atencao:

- Evite excluir clientes, carros, funcionarios ou servicos que ja estejam vinculados a ordens.
- Se um registro estiver em uso, o sistema ou o banco pode impedir a exclusao.

## 18. Editar registros

Em cada modulo, clique em Editar no registro desejado.

O formulario da tela sera preenchido com os dados atuais. Altere os campos necessarios e clique em Atualizar.

Para abandonar a edicao, clique em Cancelar.

## 19. Sair do sistema

Clique em Sair no canto superior direito.

## 20. Boas praticas de uso

- Cadastre primeiro clientes, fabricantes, modelos, carros, funcionarios, pecas e servicos.
- Depois registre as ordens de servico.
- Informe corretamente o tempo gasto para melhorar as medias.
- Mantenha os custos de pecas e funcionarios atualizados.
- Verifique o painel periodicamente para acompanhar desempenho.

## 21. Problemas comuns

### Nao consigo acessar o sistema pela rede

Verifique:

- Se o computador servidor esta ligado.
- Se a aplicacao esta rodando.
- Se o IP esta correto.
- Se o firewall liberou a porta 5000.

### Login nao funciona

Verifique:

- Se usuario e senha foram digitados corretamente.
- Se o banco foi inicializado com `flask --app app init-db`.
- Se o Docker Desktop esta aberto, quando estiver usando Docker ou `OficinaPro.exe`.

### Executavel nao inicia o sistema

Verifique:

- Se o Docker Desktop esta instalado e em execucao.
- Se a porta 5000 nao esta sendo usada por outro programa.
- Se o arquivo `OficinaPro.exe` esta dentro da pasta `standalone_installer` com os demais arquivos do pacote.

### Nao aparece carro para selecionar

Cadastre primeiro um cliente e depois um carro vinculado a esse cliente.

### Nao aparece modelo para selecionar

Cadastre primeiro um fabricante e depois um modelo vinculado a esse fabricante.

### Nao aparece servico, funcionario ou peca

Cadastre os registros nos respectivos menus antes de criar a ordem.
