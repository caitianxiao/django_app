from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.conf import settings # 将房间容量信息存储在settings中
from django.core.cache import cache  # 这个cache可以理解为一个字典

class MultiPlayer(AsyncWebsocketConsumer):
    async def connect(self):  # 当前端通过刚才的链接与我们建立连接时，执行这个函数
        self.room_name = None
        for i in range(1000):
            name = "room_%d" % (i)
            if not cache.has_key(name) or len(cache.get(name)) < settings.ROOM_CAPACITY:
                self.room_name = name
                break

        if not self.room_name:
            return


        await self.accept() # 建立连接
        print('accept')

        if not cache.has_key(self.room_name):
            cache.set(self.room_name, [], 3600) # 一小时有效期

        for player in cache.get(self.room_name): # 遍历这个房间原来的玩家，将信息发送给新来的玩家
            await self.send(text_data=json.dumps({
                    'event':"create_player",
                    'uuid': player['uuid'],
                    'username': player['username'],
                    'photo':  player['photo'],
                }))
        await self.channel_layer.group_add(self.room_name, self.channel_name)



    async def disconnect(self, close_code):
        print('disconnect')
        await self.channel_layer.group_discard(self.room_name,self.channel_name)




    async def create_player(self, data): # 从新玩家前端接受信息，添加到房间的玩家列表，并发送给组里每一个老玩家
        players = cache.get(self.room_name)
        players.append({
            'uuid': data['uuid'],
            'username': data['username'],
            'photo': data['photo'],
        })
        cache.set(self.room_name, players, 3600) # 刷新时长
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': "group_create_player",
                'event': "create_player",
                'uuid': data['uuid'],
                'username': data['username'],
                'photo': data['photo'],
            }
        )

    
    async def group_create_player(self, data):
        await self.send(text_data=json.dumps(data))


    async def receive(self, text_data):
        data = json.loads(text_data)
        event = data['event']
        if event == 'create_player':
            await self.create_player(data)
        print(data)
