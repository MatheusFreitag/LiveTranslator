# 🌎 LiveTranslator

## Sobre 
LiveTranslator é uma aplicação para a linha de comando que simula as antigas janelas de bate-papo no início da última década, com o diferencial de traduzir as mensagens para diversos idiomas em tempo real.


## Estrutura de Arquivos
```bash
.root
│
├── 📄 client.py # Script para o Cliente entrar na sala.
├── 📄 server.py # Script que controla e simula o servidor  
└── 📄 translation.py # Testes com a API de tradução. Não é importante para o projeto final.
```
Obs.: É importante salientar que o arquivo contendo o token de tradução foi omitido do repositório por ser uma chave privada com limite de uso.


## Funcionamento
Para iniciar o LiveTranslator é necessário executar o comando ```python3 server.py``` pois Python 3 é uma requsição dos scripts.
Para um cliente na mesma rede se conectar à sala, basta executar ```python3 client.py```. Se estiver em outra rede, é necessário obter o endereço IP do servidor e substituir a linha a seguir
```python
def __init__(self, host = 'IP-DO-SERVIDOR-AQUI', port = 9999):
		'''Inicializa as variáveis iniciais do cliente'''
    self.host = host
```

## Protocolo de Aplicação
Foi definido um protocolo a nivel de Camada de Aplicação para este trabalho, que trata as mensagens ou comandos da maneira como segue:

| Padrão              | Descrição                                                                                                                                                                        |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *mensagem*          | Quando uma mensagem é enviada sem nenhum comando, todos os integrantes da sala receberão a mensagem, mas de forma traduzida no idioma em que escolheram. É uma mensagem pública. |
| /lista	            | Comando sem mensagem, ele retorna a lista com todos os apelidos dos integrantes da sala de bate-papo. Mensagens enviadas com esse comando são descartadas.                       |
| /apelido *mensagem* |	A mensagem *mensagem* será enviada de forma privada somente para a pessoa que possui apelido como apelido setado.                                                                |
| /tchau	            | Encerra a conexão do cliente com o servidor. Mensagens enviadas com esse comando são descartadas.                                                                                |


## Tradução
A API utilizada foi a [Microsft Translator Text API](https://www.microsoft.com/en-us/translator/translatorapi.aspx) que em sua versão gratuíta disponibiliza a tradução de 2 milhões de caracteres, quantia suficiente para este trabalho.
