import os

import tools

class Server:


    logger = None
    pid = tools.INVALID


    def __init__(self, logger = None):
        self.logger = logger


    def start(self, path, conf='mpd.conf'):
        
        pid = tools.procid(os.path.basename(path))
        if pid != tools.INVALID:
            tools.procstop(pid)

        if tools.islinux():
            pass # TODO
        else:
            tools.info('start process ' + path, self.logger)
            self.pid = tools.procstart(path, [conf]) 
    

    def stop(self):
        
        tools.info('stop process ' + str(self.pid), self.logger)
        tools.procstop(self.pid)


if __name__ == '__main__':

    server = Server()
    server.start('..\\mpd\\mpd.exe', conf='mpd.conf')
    server.stop()