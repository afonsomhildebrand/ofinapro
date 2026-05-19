# Build e Protecao do Executavel - OficinaPro

## 1. Objetivo

Este documento descreve o fluxo para gerar o executavel standalone do OficinaPro e empacotar app + MySQL para uso em um unico computador com Docker Desktop.

## 2. Arquitetura adotada

O projeto atual permanece como aplicacao web em Python/Flask, executada dentro de Docker. O executavel Windows funciona como launcher local:

- Valida Docker e Docker Compose.
- Inicializa app e MySQL pelo Docker Compose.
- Aguarda a API web local responder.
- Abre o navegador na tela do sistema.

Essa abordagem preserva o uso em rede interna e permite rodar o sistema em modo standalone.

## 3. Relacao com a especificacao informada

| Item informado | Aplicacao no pacote |
| --- | --- |
| Frontend: Streamlit/PyQt/Kivy | O sistema entregue usa frontend web Flask/Jinja2. Streamlit, PyQt ou Kivy podem ser usados em uma futura versao desktop, mas exigiriam reescrita da interface. |
| Core critico: Rust/C++ | O core critico operacional fica isolado no container. Um launcher C++ pode ser criado futuramente, mas o build atual usa C#/.NET Framework como fallback disponivel no Windows. |
| Execucao: API remota | A aplicacao roda como API web local em `http://127.0.0.1:5000` e tambem pode ser acessada pela rede interna. |
| Protecao: Nuitka + PyArmor + UPX opcional | O script `standalone_installer/build_secure_executable.ps1` usa PyArmor quando instalado para ofuscar o launcher, Nuitka para compilar em executavel e UPX quando disponivel para compactacao. |

## 4. Arquivos principais

```text
standalone_installer\OficinaPro.exe
standalone_installer\build_secure_executable.ps1
standalone_installer\launcher\OficinaProLauncher.cs
standalone_installer\launcher\OficinaProNuitkaLauncher.py
standalone_installer\docker-compose.yml
standalone_installer\app\
OficinaPro_Standalone_Installer.zip
```

## 5. Gerar executavel

Na raiz do projeto:

```powershell
powershell.exe -ExecutionPolicy Bypass -File standalone_installer\build_secure_executable.ps1
```

Comportamento do script:

1. Se `pyarmor` e `nuitka` estiverem instalados, ofusca `OficinaProNuitkaLauncher.py` com PyArmor e compila com Nuitka.
2. Se apenas `nuitka` estiver instalado, compila `OficinaProNuitkaLauncher.py` diretamente.
3. Se `upx` estiver instalado, compacta o executavel gerado.
4. Se `nuitka` nao estiver instalado, compila `OficinaProLauncher.cs` com o compilador C# do .NET Framework.
5. Mantem o resultado final em `standalone_installer\OficinaPro.exe`.

## 6. Ativar Nuitka

Instale Nuitka no ambiente Python usado para build:

```powershell
pip install nuitka
```

Depois execute novamente:

```powershell
powershell.exe -ExecutionPolicy Bypass -File standalone_installer\build_secure_executable.ps1
```

## 7. Ativar PyArmor e UPX

Para ofuscar o launcher antes da compilacao, instale PyArmor:

```powershell
pip install pyarmor
powershell.exe -ExecutionPolicy Bypass -File standalone_installer\build_secure_executable.ps1
```

Para compactar o executavel, instale UPX e deixe `upx.exe` no PATH. Essa etapa e opcional.

Observacao: PyArmor pode ter limitacoes de licenca conforme o tipo de distribuicao.

## 8. Empacotar standalone

Depois de gerar o executavel:

```powershell
Compress-Archive -Path standalone_installer -DestinationPath OficinaPro_Standalone_Installer.zip -Force
```

## 9. Testar pacote

Com Docker Desktop em execucao:

```powershell
standalone_installer\OficinaPro.exe
powershell.exe -ExecutionPolicy Bypass -File standalone_installer\test_installation.ps1
```

Resultado esperado:

- Containers `oficinapro_standalone_app` e `oficinapro_standalone_mysql` iniciados.
- App acessivel em `http://127.0.0.1:5000`.
- MySQL publicado na porta `3307`.
- Login inicial `admin / admin123`.
