import asyncio
import datetime
import re

import orjson
import qrcode
from bson.objectid import ObjectId
from io import BytesIO
from PIL import ImageDraw, ImageFont, Image
from pyzbar.pyzbar import decode

import aiohttp
from rocketgram import InlineKeyboard, SendPhoto, InputFile, InputMediaPhoto
from rocketgram import SendMessage, UpdateType, MessageType, GetFile, ReplyKeyboardRemove
from rocketgram import commonfilters, ChatType, context, commonwaiters

import data
import tools
from mybot import router
from models import QRCode, User, Company, Pass
from .func import send_new_pass_message


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/new_pass')
async def start_message():
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})
    if not company:
        await SendMessage(context.user.id, T('new_pass/no_validated_company_error')).send()
        return

    active_pas = await Pass.find_one({'create_user_id': context.user.id, 'is_active': True})
    if active_pas and active_pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=active_pas)).send()
        return

    if active_pas:
        await send_new_pass_message(context.user.id, T, active_pas)
        return

    kb = InlineKeyboard()
    kb.callback(T('pass/bt'), 'create_pass').row()
    await SendMessage(context.user.id, T('pass/mt'), reply_markup=kb.render()).send()