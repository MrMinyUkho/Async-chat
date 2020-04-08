#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
	login: str = None
	server: 'Server'
	transport: transports.Transport

	def __init__(self, server: 'Server'):
		self.server = server

	def CheckAvaibleLogin(self):
		for Login in self.server.UsrLogin:
			if Login == self.login:
					print("Пшёл вон бомжара")
					return False
		else:
			print("Добро пожаловать")
			return True

	def SendHistory(self):
		if len(self.server.HistoryMessage) != 0:
			self.transport.write(f"Привет, {self.login}!\nПредыдущие сообщения:\n".encode())
			for message in self.server.HistoryMessage:
				self.transport.write(message.encode())

	def data_received(self, data: bytes):
		print(data)

		decoded = data.decode()

		if self.login is not None:
			self.send_message(decoded)
		else:
			if decoded.startswith("login:"):
				self.login = decoded.replace("login:", "").replace("\r\n","") 
				if self.CheckAvaibleLogin():
					self.SendHistory()
					self.server.UsrLogin.append(self.login)
					self.server.LoginUsr.append(self)
				else:
					self.transport.write(f"Логин {self.login} занят, попробуйте другой\n".encode())
					self.login = None
			else:
				self.transport.write("Неправильный логин\n".encode())

	def connection_made(self, transport: transports.Transport):
		self.server.clients.append(self)
		self.transport = transport
		print("Пришел новый клиент")
		print(self)

	def connection_lost(self, exception):
		self.server.clients.remove(self)
		self.server.UsrLogin.remove(self.login)
		self.server.LoginUsr.remove(self)
		print("Клиент вышел")

	def send_message(self, content: str):
		message = f"{self.login}: {content}\n"
		self.server.HistoryMessage.append(f"{self.login}: {content}\n")

		for user in self.server.LoginUsr:
			user.transport.write(message.encode())


class Server:
	clients: list
	UsrLogin: list
	LoginUsr: list
	HistoryMessage: list

	def __init__(self):
		self.LoginUsr		= []
		self.clients		= []
		self.UsrLogin		= []
		self.HistoryMessage	= []

	def build_protocol(self):
		return ServerProtocol(self)

	async def start(self):
		loop = asyncio.get_running_loop()

		coroutine = await loop.create_server(
			self.build_protocol,
			'192.168.1.106',
			8888
		)

		print("Сервер запущен ...")

		await coroutine.serve_forever()


process = Server()

try:
	asyncio.run(process.start())
except KeyboardInterrupt:
	print("Сервер остановлен вручную")
