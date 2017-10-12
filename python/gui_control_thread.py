import time
from threading import Thread

class ControlThread:


    def __init__(self, player, control):

        print('start control thread')

        if player:
                    
            thread = Thread(target=self.run, args=(player,control), daemon=True)
            terminate = False
            thread.start()                           


    def run(self, player, control):            
            
        while True:            
            control.update(player.status())
            time.sleep(0.5)
            