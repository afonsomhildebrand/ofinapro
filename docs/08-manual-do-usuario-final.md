# Manual do Usuario - OficinaPro

## 1. Acesso ao sistema

Abra o navegador e acesse o endereco informado pelo responsavel tecnico.

Uso local:

```text
http://127.0.0.1:5000
```

Uso em rede interna:

```text
http://IP-DO-SERVIDOR:5000
```

Se estiver usando o pacote standalone, execute `OficinaPro.exe` antes de acessar o sistema.

## 2. Login

Na tela inicial, informe usuario e senha.

Credencial inicial:

```text
Usuario: admin
Senha: admin123
```

Depois do primeiro acesso, recomenda-se alterar a senha do administrador.

## 3. Menu principal

O menu lateral mostra as opcoes liberadas para o usuario logado.

Menus disponiveis no sistema:

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

Usuarios sem permissao para um menu nao visualizam ou nao acessam esse item.

## 4. Painel

O Painel apresenta o resumo operacional da oficina:

- Faturamento total.
- Custo em pecas.
- Lucro estimado.
- Tempo medio dos servicos.
- Media por servico.
- Servicos por funcionario.
- Graficos mensais.

Use o Painel para acompanhar o desempenho geral da oficina.

## 5. Graficos

A tela Graficos apresenta indicadores mensais:

- Servicos por mes.
- Carros cadastrados por mes.
- Atendimentos a clientes.
- Total de clientes cadastrados.
- Clientes unicos atendidos.

Use essa tela para visualizar movimento, volume de servicos e atendimento ao longo dos meses.

## 6. Usuarios e permissoes

Somente administradores podem acessar o cadastro de usuarios do sistema.

## Financeiro

Use a aba Financeiro para emitir notas fiscais internas de servicos concluidos e controlar pagamentos por Pix, boleto, debito e credito.

1. Conclua a ordem de servico.
2. Acesse Financeiro.
3. Clique em Emitir nota para registrar a nota interna.
4. Gere a cobranca escolhendo Pix, Boleto, Debito ou Credito.
5. Quando o pagamento for recebido, clique em Baixar.

As notas e cobrancas sao registros internos do OficinaPro. Para emissao oficial, integre o sistema com provedor fiscal, prefeitura, banco ou gateway de pagamento.

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

Permissoes:

- Ver: permite acessar o menu.
- Incluir: permite criar registros.
- Editar: permite alterar registros.
- Excluir: permite remover registros.

A tela tambem apresenta tempo de uso, quantidade de sessoes, atividades executadas e ultimas atividades.

## 7. Clientes

Use Clientes para cadastrar pessoas ou empresas atendidas pela oficina.

Para cadastrar:

1. Clique em Clientes.
2. Informe nome.
3. Informe telefone.
4. Informe email, se houver.
5. Informe documento, se houver.
6. Clique em Salvar.

Para editar, clique em Editar no registro desejado, altere os dados e clique em Atualizar.

## 8. Fabricantes

Use Fabricantes para cadastrar marcas de veiculos.

Para cadastrar:

1. Clique em Fabricantes.
2. Informe o nome do fabricante.
3. Clique em Salvar.

O fabricante cadastrado fica disponivel no cadastro de carros.

## 9. Modelos

Use Modelos para cadastrar os modelos de veiculos vinculados a cada fabricante.

Para cadastrar:

1. Clique em Modelos.
2. Selecione o fabricante.
3. Informe o nome do modelo.
4. Clique em Salvar.

O modelo ficara disponivel no cadastro de carros apenas quando o respectivo fabricante for selecionado.

## 10. Carros

Use Carros para cadastrar veiculos vinculados aos clientes.

Para cadastrar:

1. Clique em Carros.
2. Selecione o cliente.
3. Selecione o fabricante.
4. Selecione o modelo.
5. Informe ano.
6. Informe placa.
7. Informe quilometragem.
8. Clique em Salvar.

Cada carro deve estar vinculado a um cliente.

## 11. Funcionarios

Use Funcionarios para cadastrar a equipe da oficina.

Para cadastrar:

1. Clique em Funcionarios.
2. Informe nome.
3. Informe cargo.
4. Informe telefone.
5. Informe salario.
6. Informe custo por hora.
7. Clique em Salvar.

O salario e informativo. O custo por hora e usado para calcular o custo de mao de obra nas ordens de servico.

## 12. Pecas

Use Pecas para controlar itens usados nos servicos.

Para cadastrar:

1. Clique em Pecas.
2. Informe nome.
3. Informe codigo.
4. Informe estoque.
5. Informe custo.
6. Informe preco de venda.
7. Clique em Salvar.

O custo das pecas entra no calculo do custo total da ordem.

## 13. Servicos

Use Servicos para cadastrar os tipos de trabalho oferecidos pela oficina.

Para cadastrar:

1. Clique em Servicos.
2. Informe nome.
3. Informe descricao.
4. Informe preco padrao.
5. Informe tempo estimado.
6. Clique em Salvar.

Exemplos:

- Troca de oleo
- Revisao de freios
- Diagnostico eletrico
- Alinhamento
- Balanceamento

## 14. Ordens de servico

Use Ordens para registrar cada atendimento da oficina.

Antes de criar uma ordem, cadastre:

- Cliente.
- Fabricante e modelo.
- Carro.
- Funcionario.
- Servico.
- Pecas, se forem usadas.

Para criar:

1. Clique em Ordens.
2. Selecione cliente.
3. Selecione carro.
4. Selecione servico.
5. Selecione funcionario responsavel.
6. Escolha o status.
7. Informe horas gastas.
8. Informe valor cobrado.
9. Selecione pecas usadas, se houver.
10. Clique em Salvar.

## 15. Status da ordem

Status disponiveis:

- Aberta: ordem criada e ainda nao iniciada.
- Em andamento: servico em execucao.
- Concluida: servico finalizado.
- Cancelada: ordem cancelada.

Mantenha o status atualizado para melhorar o acompanhamento operacional.

## 16. Custos e lucro

O sistema calcula o custo da ordem com:

```text
custo das pecas + custo da mao de obra
```

O custo da mao de obra e:

```text
horas gastas * custo por hora do funcionario
```

O lucro estimado e:

```text
valor cobrado - custo total
```

## 17. Editar registros

Em cada modulo:

1. Localize o registro.
2. Clique em Editar.
3. Altere os campos necessarios.
4. Clique em Atualizar.

Para abandonar a edicao, clique em Cancelar.

## 18. Excluir registros

Em cada modulo, clique em Excluir no registro desejado.

Atencao:

- Evite excluir dados ja vinculados a ordens.
- Registros com dependencias podem ser bloqueados pelo sistema ou pelo banco.
- Prefira editar dados incorretos em vez de excluir historico importante.

## 19. Sair do sistema

Clique em Sair no canto superior direito.

Ao sair, o sistema registra o encerramento da sessao quando possivel.

## 20. Boas praticas

- Cadastre primeiro fabricantes, modelos, clientes, carros, funcionarios, pecas e servicos.
- Depois registre ordens de servico.
- Mantenha valores de pecas e custo por hora atualizados.
- Informe corretamente horas gastas e valor cobrado.
- Use permissoes para limitar acesso conforme a funcao de cada usuario.
- Consulte Painel e Graficos com frequencia.
- Faca backup periodico do banco.

## 21. Problemas comuns

### Nao consigo entrar

Verifique usuario e senha. Se necessario, solicite redefinicao ao administrador.

### Menu nao aparece

Seu usuario pode nao ter permissao para aquele item. Solicite ajuste ao administrador.

### Nao aparece carro para selecionar

Cadastre primeiro um cliente e depois um carro vinculado a esse cliente.

### Nao aparece modelo para selecionar

Cadastre primeiro um fabricante e depois um modelo vinculado a esse fabricante.

### Nao aparece servico, funcionario ou peca

Cadastre os registros nos respectivos menus antes de criar a ordem.

### Valores do painel parecem incorretos

Verifique se as ordens possuem valor cobrado, horas gastas, pecas e funcionario com custo por hora correto.

### Sistema nao abre

Se estiver usando o pacote standalone, confirme que o Docker Desktop esta aberto e execute `OficinaPro.exe` novamente.
