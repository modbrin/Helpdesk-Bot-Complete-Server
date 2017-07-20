#!python.exe
import cgi
import subprocess
import os


def _verify_change(username, old_pass, new_pass):
    old_dir = os.path.abspath('')
    os.chdir('..\\..')
    server_dir = os.path.abspath('')
    os.chdir(old_dir)
    answer = subprocess.call([server_dir + r'\bin\htpasswd', '-v', '-b',
                              server_dir + r'\htdocs\.htpasswd', username, old_pass])
    message = 'Invalid credentials'
    if answer == 0:
        subprocess.call([server_dir + r'\bin\htpasswd', '-b', server_dir + r'\htdocs\.htpasswd', username, new_pass])
        message = 'Password changed successfully'
    return message

if __name__ == '__main__':
    form = cgi.FieldStorage()
    old = form.getvalue('old_pass')
    new = form.getvalue('new_pass')

    result = _verify_change('admin', old, new)

    print('Content-type:text/html\r\n\r\n')
    print('<html>')
    print('<head>')
    print('<title></title>')
    print('</head>')
    print('<body>')
    print(result)
    print('</body>')
    print('</html>')
