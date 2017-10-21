import os

import tools

class Server:


    pid = tools.INVALID


    def start(self, path, conf='mpd.conf'):
        
        pid = tools.procid(os.path.basename(path))
        if pid != tools.INVALID:
            tools.procstop(pid)

        if tools.islinux():
            pass # TODO
        else:
            self.pid = tools.procstart(path, [conf]) 
    

    def stop(self):
        
        tools.procstop(self.pid)


if __name__ == '__main__':

    server = Server()
    server.start('..\\mpd\\mpd.exe', conf='mpd.conf')
    server.stop()