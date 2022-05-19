### “术士之战”联机对战页游，部署于阿里云

下载项目文件
运行以下命令：
`python3 manage.py runserver 0.0.0.0:8000`

`daphne -b 0.0.0.0 -p 5015 acapp.asgi:application`

`acapp/match_system/src$里面的 ./main.py `

`
from django.core.cache import cache
def clear():                                     
  for key in cache.keys('*'):                                                                           
    cache.delete(key)
cache.keys('*')
clear()
`
