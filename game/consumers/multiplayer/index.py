from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.conf import settings # 将房间容量信息存储在settings中
from django.core.cache import cache  # 这个cache可以理解为一个字典

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from game.consumers.multiplayer.match_client.match_service import Match
from game.models.player.player import Player
from channels.db import database_sync_to_async


class MultiPlayer(AsyncWebsocketConsumer):
    async def connect(self):  # 当前端通过刚才的链接与我们建立连接时，执行这个函数
        await self.accept() # 建立连接


    async def disconnect(self, close_code):
        if self.room_name:
            await self.channel_layer.group_discard(self.room_name,self.channel_name)




    async def create_player(self, data): # 从新玩家前端接受信息，添加到房间的玩家列表，并发送给组里每一个老玩家
        self.room_name = None
        self.uuid = data['uuid']

        # Make socket
        transport = TSocket.TSocket('localhost', port=9090)
    
        # Buffering is critical. Raw sockets are very slow
        transport = TTransport.TBufferedTransport(transport)
    
        # Wrap in a protocol
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
    
        # Create a client to use the protocol encoder
        client = Match.Client(protocol)
        def db_get_player():
            return Player.objects.get(user__username=data['username'])
        
        player = await database_sync_to_async(db_get_player)()
        # Connect!
        transport.open()

        client.add_player(player.score, data['uuid'], data['username'], data['photo'], self.channel_name)

        transport.close()

    
    async def group_send_event(self, data):
        if not self.room_name:
            keys = cache.keys('*%s*' % (self.uuid))
            if keys:
                self.room_name = keys[0]
        await self.send(text_data=json.dumps(data))


    async def move_to(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "move_to",
                'uuid': data['uuid'],
                'tx': data['tx'],
                'ty': data['ty'],
            }
        )

    async def shoot_fireball(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "shoot_fireball",
                'uuid': data['uuid'],
                'tx': data['tx'],
                'ty': data['ty'],
                'ball_uuid': data['ball_uuid'],
            }
        )

    async def attack(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "attack",
                'uuid': data['uuid'],
                'attackee_uuid': data['attackee_uuid'],
                'x': data['x'],
                'y': data['y'],
                'angle': data['angle'],
                'damage': data['damage'],
                'ball_uuid': data['ball_uuid'],
            }
        )
    async def flash(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "flash",
                'uuid': data['uuid'],
                'tx': data['tx'],
                'ty': data['ty'],
            }
        )

    async def message(self, data):
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_send_event",
                'event': "message",
                'uuid': data['uuid'],
                'username': data['username'],
                'text': data['text'],
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        event = data['event']
        if event == "create_player":
            await self.create_player(data)
        elif event == "move_to":
            await self.move_to(data)
        elif event == "shoot_fireball":
            await self.shoot_fireball(data)
        elif event == "attack":
            await self.attack(data)
        elif event == "flash":
            await self.flash(data)
        elif event == "message":
            await self.message(data)

