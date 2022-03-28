import os, ftputil

def loadftp(server, username, password, target_folder):
    # Создать папку если нет
    if not os.path.exists(target_folder):
        os.mkdir(target_folder)
    # Подключение по FTP
    try:
        with ftputil.FTPHost(server, username, password) as host:
            # Взять содержимое доступной папки по FTP
            file_list = host.listdir(host.curdir)
            for file in file_list:
                if host.path.isfile(file):
                    # При FTP загрузке кодировка Unicode треяется
                    target = target_folder+"\\"+file.encode("latin1").decode("utf8")
                    # Скачивание
                    host.download(file, target)
        return True
    # Если сервер по адресу закрыт или не найден
    except ftputil.error.FTPOSError:
       return False