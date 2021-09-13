from datetime import datetime

class Logger():
    def write_log(self, log_message):
        file = open("log.txt", 'a+')
        file.write(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ' ' + log_message + '\n'))