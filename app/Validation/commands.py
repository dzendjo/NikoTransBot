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
from .func import send_reg_jur_message


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/register')
async def start_message():
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})
    if company:
        if company.is_validated:
            await SendMessage(context.user.id, T('register/has_registered_mt', company=company)).send()
            return
        if company.is_on_check:
            await SendMessage(context.user.id, T('register/on_check_mt', company=company)).send()
        if not company.is_validated and not company.is_on_check:
            await send_reg_jur_message(context.user.id, T, company)
    else:
        kb = InlineKeyboard()
        kb.callback(T('register/bt'), 'register').row()
        await SendMessage(context.user.id, T('register/mt'), reply_markup=kb.render()).send()