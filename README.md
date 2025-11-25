# Sistema Distribuído de Gerenciamento de Arquivos via TCP

Um sistema cliente-servidor para transferência de arquivos utilizando sockets TCP, implementado em Python. O projeto permite upload, download e listagem de arquivos de forma confiável através do protocolo TCP.

## Sobre o Projeto

Este sistema distribuído implementa um modelo cliente-servidor que permite:
- **Upload de arquivos**: Envie arquivos do cliente para o servidor
- **Download de arquivos**: Baixe arquivos armazenados no servidor
- **Listagem de arquivos**: Visualize todos os arquivos disponíveis no servidor
- **Múltiplas conexões**: O servidor suporta múltiplos clientes simultaneamente através de threads

O sistema utiliza sockets TCP para garantir transferência confiável de dados, com controle de fluxo e confirmação de recebimento.

## Tecnologias Utilizadas

- **Python 3.x**
- **Socket TCP** - Para comunicação cliente-servidor
- **Threading** - Para suportar múltiplas conexões simultâneas
- **Tkinter** - Para interface gráfica do cliente

## Estrutura do Projeto

```
tcp-file-manager/
│
├── server.py              # Servidor TCP que gerencia arquivos
├── client_core.py         # Cliente em linha de comando (CLI)
├── client_gui.py          # Cliente com interface gráfica (GUI)
├── server_files/          # Diretório onde o servidor armazena arquivos
├── client_downloads/      # Diretório onde os arquivos baixados são salvos
└── README.md             # Este arquivo
```

## Instalação

### Pré-requisitos

- Python 3.6 ou superior instalado
- Sistema operacional: Windows, Linux ou macOS

### Verificar versão do Python

```powershell
python --version
```

### Dependências

Este projeto utiliza apenas bibliotecas padrão do Python, portanto **não é necessário instalar dependências externas**.

As bibliotecas utilizadas são:
- `socket` - Comunicação de rede
- `threading` - Processamento paralelo
- `tkinter` - Interface gráfica (incluída na maioria das instalações Python)
- `os`, `sys` - Operações de sistema

## Como Executar

### 1. Iniciar o Servidor

Primeiro, inicie o servidor que ficará escutando conexões na porta 5000:

```powershell
python server.py
```

Você verá a mensagem:
```
[OUVINDO] Servidor rodando em 0.0.0.0:5000
```

O servidor criará automaticamente o diretório `server_files/` para armazenar os arquivos recebidos.

### 2. Executar o Cliente

Você pode escolher entre duas interfaces:

#### Opção A: Cliente em Linha de Comando (CLI)

```powershell
python client_core.py
```

#### Opção B: Cliente com Interface Gráfica (GUI)

```powershell
python client_gui.py
```

## Comandos Disponíveis

### Cliente CLI (`client_core.py`)

Após conectar ao servidor, você pode usar os seguintes comandos:

#### **UPLOAD <nome_do_arquivo>**
Envia um arquivo do diretório atual para o servidor.
```
>>> UPLOAD exemplo.txt
```

#### **DOWNLOAD <nome_do_arquivo>**
Baixa um arquivo do servidor para o diretório `client_downloads/`.
```
>>> DOWNLOAD exemplo.txt
```

#### **LIST**
Lista todos os arquivos disponíveis no servidor.
```
>>> LIST
```

#### **EXIT**
Encerra a conexão com o servidor.
```
>>> EXIT
```

### Cliente GUI (`client_gui.py`)

A interface gráfica oferece:
- Botão **"Conectar ao Servidor"** - Estabelece conexão
- Botão **"Atualizar Lista (LIST)"** - Atualiza a lista de arquivos
- Botão **"Baixar (DOWNLOAD)"** - Baixa o arquivo selecionado
- Botão **"Enviar (UPLOAD)"** - Abre diálogo para selecionar arquivo a enviar
- **Log de Operações** - Mostra o histórico de ações realizadas

## Configuração

### Alterar Host e Porta

Por padrão, o sistema usa:
- **Host do Servidor**: `0.0.0.0` (aceita conexões de qualquer interface)
- **Host do Cliente**: `127.0.0.1` (localhost)
- **Porta**: `5000`

Para alterar essas configurações, edite as constantes no início dos arquivos:

**server.py:**
```python
HOST = '0.0.0.0'
PORT = 5000
```

**client_core.py e client_gui.py:**
```python
HOST = '127.0.0.1'
PORT = 5000
```

### Tamanho do Buffer

O tamanho do buffer de transferência pode ser ajustado:
```python
BUFFER_SIZE = 4096  # 4KB
```

## Funcionamento do Sistema

### Protocolo de Comunicação

O sistema utiliza um protocolo simples baseado em texto com separador `|`:

1. **UPLOAD**: `UPLOAD|nome_arquivo|tamanho_bytes`
2. **DOWNLOAD**: `DOWNLOAD|nome_arquivo`
3. **LIST**: `LIST`
4. **EXIT**: `EXIT`

### Fluxo de Upload

1. Cliente envia: `UPLOAD|arquivo.txt|1024`
2. Servidor responde: `OK`
3. Cliente envia dados binários do arquivo
4. Servidor confirma: `SUCCESS`

### Fluxo de Download

1. Cliente envia: `DOWNLOAD|arquivo.txt`
2. Servidor responde: `EXISTS|1024` (tamanho do arquivo)
3. Cliente confirma: `READY`
4. Servidor envia dados binários do arquivo

### Suporte a Múltiplas Conexões

O servidor utiliza threads para gerenciar cada conexão de cliente independentemente, permitindo que múltiplos clientes se conectem e transfiram arquivos simultaneamente.

## Características de Segurança

- Validação de nomes de arquivo usando `os.path.basename()` para evitar path traversal
- Controle de tamanho de arquivo antes da transferência
- Tratamento de exceções para evitar crashes
- Confirmações em cada etapa da transferência

## Exemplos de Uso

### Exemplo 1: Upload de arquivo

```
>>> UPLOAD documento.txt
[UPLOAD] Arquivo 'documento.txt' enviado com sucesso!
```

### Exemplo 2: Listar e baixar arquivo

```
>>> LIST
--- Arquivos no Servidor ---
- documento.txt
- imagem.png
----------------------------

>>> DOWNLOAD documento.txt
[DOWNLOAD] Arquivo 'documento.txt' encontrado no servidor (1024 bytes).
[DOWNLOAD] Arquivo 'documento.txt' salvo em 'client_downloads' com sucesso.
```

## Solução de Problemas

### Erro: "Address already in use"
- O servidor já está rodando em outra instância
- Aguarde alguns segundos ou altere a porta

### Erro: "Connection refused"
- Verifique se o servidor está rodando
- Confirme o host e porta corretos no cliente

### Arquivo não encontrado no upload
- Certifique-se de que o arquivo está no diretório atual
- Use o caminho completo ou navegue até o diretório do arquivo

## Licença

Este projeto foi desenvolvido para fins educacionais como parte de um trabalho acadêmico sobre sistemas distribuídos.
