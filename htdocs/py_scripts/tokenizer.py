#!python.exe
import cgi
import json

import zmq


def _get_token_array(text):
    try:
        socket.send_unicode(text)
        message = socket.recv()
        return json.loads(message.decode('unicode-escape'), encoding='utf-8')
    except Exception:  # Если сервер недоступен на протяжении срока TIMEOUT - вернуть пустой List
        return []

if __name__ == '__main__':
    form = cgi.FieldStorage()

    form_text = form.getvalue('text')

    # Соединение с сервером
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://127.0.0.1:9080')
    socket.RCVTIMEO = 5000

    result = json.dumps(_get_token_array(form_text))

    print('Content-type:text/html\r\n\r\n')
    print(result)
