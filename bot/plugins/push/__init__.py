from nonebot import require, get_bot, get_driver
from nonebot.adapters.cqhttp import MessageSegment, Message

from .config import Config
from .bili_api import *

sched = require('nonebot_plugin_apscheduler').scheduler

bili_status = {}

global_config = get_driver().config
plugin_config = Config(**global_config.dict())

@sched.scheduled_job('interval', seconds=5)
async def push_bili():
    global bili_status
    for item in plugin_config.bili_user:
        pre:bool = bili_status.get(item, True)  # 避免bot启动时正在直播，又推送了，默认True

        user = bili_api.user(item)
        now:bool = user.room.liveStatus == 1
        if now and not pre:
            msg: Message = MessageSegment.text('开播啦！') \
                + MessageSegment.text(user.room.title) \
                + MessageSegment.image(user.room.cover) \
                + MessageSegment.text(user.room.url)
            for group in plugin_config.bili_push_groups:
                await get_bot().call_api('send_group_msg', **{
                    'message': msg,
                    'group_id': group})
        
        bili_status[item] = now