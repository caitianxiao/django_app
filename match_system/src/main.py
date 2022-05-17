#! /usr/bin/env python3

import glob
import sys
sys.path.insert(0, glob.glob('../../')[0])

from match_server.match_service import Match

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from queue import Queue
from time import sleep
from threading import Thread

from acapp.asgi import channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache

queue = Queue()

class Player:
    def __init__(self, score, uuid, username, photo, channel_name):
        self.score = score
        self.uuid = uuid
        self.username = username
        self.photo = photo
        self.channel_name = channel_name
        self.waiting_time = 0  # 等待时间

class MatchPool:
    def __init__(self):
        self.players = []
    
    def add_player(self, player):
        self.players.append(player)

    def match_success(self, ps):
        print("Match success: %s %s %s" % (ps[0].username, ps[1].username, ps[2].username))
        room_name = "room-%s-%s-%s" % (ps[0].uuid, ps[1].uuid, ps[2].uuid)
        players = []
        for p in ps:
            async_to_sync(channel_layer.group_add)(room_name, p.channel_name)
            players.append({
                'uuid': p.uuid,
                'username': p.username,
                'photo': p.photo,
                'hp': 100,
            })
        cache.set(room_name, players, 3600)
        for p in ps:
            async_to_sync(channel_layer.group_send)(room_name, 
            {
                'type': "group_send_event",
                'event': "create_player",
                'uuid': p.uuid,
                'username': p.username,
                'photo': p.photo,
            })
            


    def check_match(self, player_a, player_b):
        dt = abs(player_a.score - player_b.score)
        a_max_dif = player_a.waiting_time * 50
        b_max_dif = player_b.waiting_time * 50
        return a_max_dif >= dt and b_max_dif >= dt

    def increase_waiting_time(self):
        for player in self.players:
            player.waiting_time += 1

    def match(self):
        while len(self.players) >= 3:
            self.players = sorted(self.players, key=lambda p:p.score)
            flag = False
            for i in range(len(self.players) - 2):
                player_a, player_b, player_c = self.players[i], self.players[i + 1], self.players[i + 2]
                if self.check_match(player_a, player_b) and self.check_match(player_a, player_c) and self.check_match(player_c, player_b):
                    self.match_success([player_a, player_b, player_c])
                    self.players = self.players[:i] + self.players[i+3:]
                    flag = True
                    break
            if not flag:
                break
        self.increase_waiting_time()


class MatchHandler:
    def add_player(self, score, uuid, username, photo, channel_name):
        print("Addplayer: %s %d" % (username, score))
        player = Player(score, uuid, username, photo, channel_name)
        queue.put(player)
        return 0

def get_player_from_queue():
    try:
        return queue.get_nowait()
    except:
        return None

def worker():
    print("It's time to worker....")
    pool = MatchPool()
    while True:
        player = get_player_from_queue()
        if player:
            pool.add_player(player)
        else:
            pool.match()
            sleep(1)

if __name__ == '__main__':
    handler = MatchHandler()
    processor = Match.Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadedServer(
        processor, transport, tfactory, pfactory)

    Thread(target=worker, daemon=True).start()

    print('Starting the server...')
    server.serve()
    print('done.')
