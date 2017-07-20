def get_config(filename):
    f = open(filename, 'r')
    #считывает логин, пароль, адрес хоста и порт
    index = 0
    for line in f:
        if(index == 0):
            email_account = line
        if(index == 1):
            password = line
        if(index == 2):
            host = line[0:len(line)-1]
        if(index == 3):
            port = int(line)
        index += 1
    return email_account, password, host, port
    
