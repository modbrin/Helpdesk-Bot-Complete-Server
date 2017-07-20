import zmq
import json

#  Подключаемся к токенизатору
context = zmq.Context()
print("Connecting to Tokenizer server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:9080")
socket.RCVTIMEO = 5000  # лимит ожидания ответа TIMEOUT (в миллисекундах)

#  Обращение к серверу токенизатора
def get_token_array(text):
	try:
		# Отправляем текст токенизатору
		socket.send_unicode(text)
		# Ожидаем json массив токенов
		message = socket.recv()
		# Парсим массив токенов
		return json.loads(message.decode("unicode-escape"), encoding="utf-8")
	except:  # Если сервер не отвечает за указанный промежуток времени (TIMEOUT) возврашаем пустой массив
		return []

#  Пример
# while True:
	# nb = input("\nYour input: ")
	# print("Tokens: %s" % get_token_array(nb))
