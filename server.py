import socket
import sys
import threading
import os
import time
import http.client, urllib.parse, uuid, json

class Servidor:
	'''Serve como servidor de um bate papo. Essa classe é responsável por gerenciar as mensagens que chegam dos clientes
	e envia-la a outros clientes.'''
	
	def __init__(self, host = '', port = 9999):
		'''Inicializa as variáveis iniciais do servidor'''
		self.finaliza = '/SERVIDOR_OFF'
		self.host = host
		self.port = port
		self.palavras_reservadas = ['/tchau', '/lista', '/SERVIDOR_OFF', '/apelido']
		self.clientes = {} #key: apelido. Value: (con, idm)
		with open('token.txt', 'r') as myfile:
			self.token=myfile.read().replace('\n', '')
        
	def main(self):
		'''Começa a execução do servidor, aqui as threads são inicializadas e enviadas aos respectivos métodos'''
		try:
			self.cria_conexao_tcp()
			self.aceita_conexao_clientes()
		except:
			self.envia_mensagem_publica([], self.finaliza)
			os._exit(1)
            
            
	def cria_conexao_tcp(self):
		'''Cria uma conexão TCP '''
		dest = (self.host, self.port)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET is the family address - in this case, Internet Protocol v4 addresses, SOCK_STREAM means that it is a TCP socket.
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #SO_REUSEADDR Indicates that the rules used in validating addresses supplied should allow reuse of local addresses.
		try:
			self.s.bind(dest) #Vincula socket a um endereço particular e porta
			print ('Servidor Iniciado')
		except:
			print ('Bind falhou')
			os._exit(1)
		self.s.listen(5)


	def traduz_mensagem(self, token, idioma, msg):
		subscriptionKey = token
		host = 'api.cognitive.microsofttranslator.com'
		path = '/translate?api-version=3.0'
		# List of supported languages: https://docs.microsoft.com/en-us/azure/cognitive-services/translator/languages
		params = "&to=" + idioma;
		text = msg

		def translate (content):
		    headers = {
		        'Ocp-Apim-Subscription-Key': subscriptionKey,
		        'Content-type': 'application/json',
		        'X-ClientTraceId': str(uuid.uuid4())
		    }
		    conn = http.client.HTTPSConnection(host)
		    conn.request ("POST", path + params, content, headers)
		    response = conn.getresponse ()
		    return response.read ()

		requestBody = [{
		    'Text' : text,
		}]

		content = json.dumps(requestBody, ensure_ascii=False).encode('utf-8')
		result = translate (content) #Array de bytes
		result = result.decode('utf8').replace("'", '"').replace("[", "").replace("]", "") # Lista com caracteres retornados tratados
		result = json.loads(result) #Json tratado
		# print('-'*7)
		# print(content)
		# print(result)
		if (result["translations"]["text"]):
			return (result["translations"]["text"])
		else:
			return "Falha de tradução"
		
		
	def aceita_conexao_clientes(self):
		'''Aceita conexão de clientes que se conectam ao servidor'''
		while True:
			con, addr = self.s.accept()
			thread = threading.Thread(target = self.controle_conexao, args = (con,))
			thread.start()
            
            
            
	def controle_conexao(self, con):
		'''Faz o controle de conexão de cada cliente. Cada cliente é executado por uma thread a partir desse ponto'''
		con.send('Bem-vindo ao bate-papo LiveTranslator! Digite seu apelido:'.encode('utf-8'))
		apelido = con.recv(1024).decode('utf-8')
		
		#Verifica se o apelido é válido
		existe = self.verifica_apelido(apelido)
		while existe:
			con.send('Este apelido já está sendo usado. Tente outro apelido:'.encode('utf-8'))
			apelido = con.recv(1024).decode('utf-8')
			existe = self.verifica_apelido(apelido)
		
		con.send('Em qual idioma você gostaria de receber as mensagems? (pt, en, es):'.encode('utf-8'))
		idioma = con.recv(1024).decode('utf-8')
		
		print("{} conectou-se ao bate-papo LiveTranslator e fala {}.".format(apelido, idioma))

		#key: apelido. Value: (con, idioma)
		self.clientes[apelido] = (con, idioma)		

		msg = 'Nova pessoa no chat.'
		self.envia_mensagem_publica(apelido, msg)
		self.recebe_mensagem(apelido, con)
        
        
	def envia_mensagem_publica(self, remetente, msg):
		'''Envia mensagens para todos os clientes.'''

		for apelido, value in list(self.clientes.items()):
			con, idm = value  #Conexão do destino e idioma que o cliente fala
			#Verifica que o usuario que irá receber a mensagem não é o mesmo que envia a mensagem.
			if apelido != remetente:
				#Aqui deve rolar a tradução
				msg_traduzida = self.traduz_mensagem(self.token, idm, msg)
				print('-'*7)
				print("{} mandou mensagem pública para {}".format(remetente, apelido) )
				self.envio_mensagem(con, msg_traduzida)
	
		if not self.clientes: #Servidor vai fechar e não tem ninguém conectado
			return
         
         
	def envio_mensagem(self, con, msg):
		'''Esse método é chamado internamente pela função envia_mensagem_publica e envia_mensagem_privada.
		Ele envia através do socket(con) a mensagem ao destinatário.'''
		try:
			con.send(msg.encode('utf-8'))
		except:
			pass
	  
    
	def recebe_mensagem(self, apelido, con):
		'''Recebe mensagem do usuário'''
		while True:
			try:
				msg = con.recv(4026).decode('utf-8')
				self.comando_msg(apelido, msg)
			except:
				break  
           
            
	def encerra_conexao_tcp(self):
		'''Encerra a conexão TCP'''
		self.s.close()
        
        
	def verifica_apelido(self, novo_apelido):
		'''Verifica se já existe o apelido no chat e se não é uma palavra reservada/regra.
		Se já existir retorna True, se não, retorna False'''
		if novo_apelido in self.palavras_reservadas:
			return True
		return novo_apelido in self.clientes   
        
        
	def comando_msg(self, remetente, msg):
		'''Verifica se a mensagem enviada é um comando ou se é mensagem pública.
		Lista de comandos:
		/tchau				#Cliente encerra conexão com servidor
		/lista				#Mosta uma lista com todos os usuários do chat
		/apelido 			#Cliente manda mensagem privada para usuario definido por APELIDO
		'''
	
		is_comando = msg.strip() #Tira espaços em branco no início e fim da mensagem
		is_comando = list(is_comando) #Coloca numa lista todas as letras da mensagem
	
		if is_comando[0] == '/':
			is_comando = msg.split() #Coloca as substrings da mensagem numa lista
	
			if is_comando[0] == '/tchau':
				print('{} saiu do bate-papo.'.format(remetente))
				self.fim_conexao(remetente)
			
			elif is_comando[0] == '/lista':
				msg = self.lista_online()
				self.envia_mensagem_privada([], remetente, msg)
				
			else:
				#É uma mensagem privada, e o apelido está logo depois do /
				destinatario = self.pega_apelido(msg[1:])
	
				if self.verifica_apelido(destinatario):
					msg = msg.replace('/' + destinatario, '') #Retira o apelido da mensagem
					self.envia_mensagem_privada(remetente, destinatario, msg)
				else:
					msg = 'Nenhum usuário com este apelido está conectado.'
					self.envia_mensagem_privada([], remetente, msg)
					return
		else:
			#É uma mensagem pública
			self.envia_mensagem_publica(remetente, msg)
            
            
	def pega_apelido(self, nome):
		'''Para mandar privado, essa função retorna o apelido da pessoa'''
		destinatario = ''
		for apelido in self.clientes:
			if nome.startswith(apelido):
				destinatario = apelido
				break
		return destinatario
        
	
	def fim_conexao(self, apelido):
		'''Esse método é chamado internamente pela encerrar conexão de um cliente.'''
		#Pega conexão que será encerrada
		con,idm = self.clientes.get(apelido)
		
		#Remove do dicionário
		del self.clientes[apelido]
		
		msg = '{} saiu do bate-papo.'.format(apelido)
		self.envia_mensagem_publica(apelido, msg)
		con.close()


	def lista_online(self):
		'''Retorna string com clientes online para o cliente'''
		online = 'Lista de clientes conectados no bate-papo no momento:\n'
		for cliente in list(self.clientes.keys()):
			online = online + cliente + '\n'
		return online	
		
		
	def envia_mensagem_privada(self, remetente, destinatario, msg):
		'''Envia mensagem de um cliente para um único usuário'''
		con, idm = self.clientes.get(destinatario)
		if remetente == []:
			remetente = "Servidor"
		
		#Envia mensagem privada
		msg_traduzida = self.traduz_mensagem(self.token, idm, msg)
		print('-'*7)
		print("{} mandou mensagem privada para {}".format(remetente, destinatario) )
		msg = '<' + remetente + '- Privado>: ' + msg_traduzida
		self.envio_mensagem(con, msg)
	
	
	

		
		
if __name__ == "__main__":
	server = Servidor()
	server.main()