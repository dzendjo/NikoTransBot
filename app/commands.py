import asyncio
import datetime
import re

import orjson
import qrcode
from bson.objectid import ObjectId
from io import BytesIO
from PIL import ImageDraw, ImageFont, Image
from pyzbar.pyzbar import decode
import pytz

import aiohttp
from rocketgram import InlineKeyboard, SendPhoto, InputFile, InputMediaPhoto, GetChatAdministrators
from rocketgram import SendMessage, UpdateType, MessageType, GetFile, ReplyKeyboardRemove
from rocketgram import commonfilters, ChatType, context, commonwaiters, SendDocument, priority

import data
import tools
from data import jinja
from draw import start_draw
from mybot import router
from models import QRCode, User, Company, Pass
from keyboards import get_admin_ik


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/start')
async def start_message():
    T = data.current_T.get()
    user = data.current_user.get()

    if len(context.message.text.split()) > 1:
        pas_id = context.message.text.split()[-1]
        pas = await Pass.find_one(ObjectId(pas_id))
        if pas:
            company = await Company.find_one(ObjectId(pas.company_id))
            caption = T('pass/qr_caption', pas=pas, company=company)
            start_date = pas.start_date.replace(tzinfo=pytz.utc).astimezone(data.tz)
            end_date = pas.end_date.replace(tzinfo=pytz.utc).astimezone(data.tz)
            if start_date <= datetime.datetime.now(tz=data.tz) <= end_date:
                await SendMessage(context.user.id, T('main/granted_mt', pas=pas)).send()
            else:
                await SendMessage(context.user.id, T('main/not_granted_mt', pas=pas)).send()
            await SendMessage(context.user.id, caption).send()
        else:
            await SendMessage(context.user.id, T('main/qr_not_found_mt')).send()
    else:
        await SendMessage(user.id, T('start/mt'), reply_markup=ReplyKeyboardRemove()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/export')
async def start_message():
    T = data.current_T.get()

    admins = await GetChatAdministrators(data.passes_channel_id).send()
    admin_ids = [admin.user.id for admin in admins]
    print(admin_ids)

    if context.user.id not in admin_ids:
        await SendMessage(context.user.id, T('export/not_admin_mt')).send()
        return

    kb = InlineKeyboard()
    kb.callback(T('export/active_bt'), 'export active').row()
    kb.callback(T('export/all_bt'), 'export all').row()
    # kb.callback(T('export/companies_bt'), 'export_companies').row()

    await SendMessage(context.user.id, T('export/mt'), reply_markup=kb.render()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/archive')
async def start_message():
    T = data.current_T.get()
    await SendMessage(context.user.id, T('main/in_dev_mt')).send()


@router.handler
@commonfilters.update_type(UpdateType.message)
@commonfilters.message_type(MessageType.text)
@commonfilters.chat_type(ChatType.private)
@priority(2020)
async def link_command():
    T = data.current_T.get()
    await SendMessage(context.user.id, T('start/mt')).send()


# @router.handler
# @commonfilters.chat_type(ChatType.private)
# @commonfilters.command('/help')
# async def start_message():
#     T = data.current_T.get()
#
#     pas = await Pass.find_one({'num_id': '432354'})
#     company = await Company.find_one(ObjectId(pas.company_id))
#
#     tools.generate_document(pas, company)



# @router.handler
# @commonfilters.chat_type(ChatType.private)
# @commonfilters.command('/admin')
# async def start_message():
#     T = data.current_T.get()
#     user = data.current_user.get()
#
#     if not user.is_admin:
#         # Check FIO
#         if not user.FIO:
#             await SendMessage(context.user.id, T('reg/FIO_mt')).send()
#             yield commonwaiters.next_message()
#
#             user.FIO = context.message.text
#             await user.commit()
#
#         # Check Phone
#         if not user.phone:
#             await SendMessage(context.user.id, T('reg/phone_mt')).send()
#             yield commonwaiters.next_message()
#
#             if context.message.text[:4] != '+380':
#                 await SendMessage(context.user.id, T('reg/phone_error')).send()
#                 return
#
#             user.phone = context.message.text
#             await user.commit()
#
#         await SendMessage(user.id, T('reg/admin_mt')).send()
#
#     else:
#         # If user is admin:
#         kb = get_admin_ik(T)
#         await SendMessage(user.id, T('admin/mt'), reply_markup=kb.render()).send()


# @router.handler
# @commonfilters.update_type(UpdateType.message)
# @commonfilters.message_type(MessageType.document, MessageType.photo)
# @commonfilters.chat_type(ChatType.private)
# async def link_command():
#     T = data.current_T.get()
#
#     if context.message.photo:
#         file_id = context.message.photo[-1].file_id
#     elif context.message.document.mime_type in ['image/jpeg', 'image/png', 'image/jpg']:
#         file_id = context.message.document.file_id
#     else:
#         await SendMessage(context.user.id, T('errors/not_correct_document')).send()
#         return
#
#     response = await GetFile(file_id).send()
#     api_file_url = 'https://api.telegram.org/file/bot{}/'.format(context.bot.token)
#     url = api_file_url + response.file_path
#     print(url)
#
#     session: aiohttp.ClientSession = context.bot.connector._session
#
#     response = await session.get(url)
#     file_data = await response.read()
#
#     image = Image.open(BytesIO(file_data))
#     try:
#         decode_data = decode(image)[0].data.decode()
#     except IndexError as e:
#         print(e)
#         await SendMessage(context.user.id,  T('main/recognize_error_mt')).send()
#         return
#
#     try:
#         pas = await Pass.find_one(ObjectId(decode_data))
#     except Exception as e:
#         await SendMessage(context.user.id, T('main/qr_not_found_mt')).send()
#         return
#
#     if pas:
#         company = await Company.find_one(ObjectId(pas.company_id))
#         caption = T('pass/qr_caption', pas=pas, company=company)
#         start_date = pas.start_date.replace(tzinfo=pytz.utc).astimezone(data.tz)
#         end_date = pas.end_date.replace(tzinfo=pytz.utc).astimezone(data.tz)
#         if start_date <= datetime.datetime.now(tz=data.tz) <= end_date:
#             await SendMessage(context.user.id, T('main/granted_mt', pas=pas)).send()
#         else:
#             await SendMessage(context.user.id, T('main/not_granted_mt', pas=pas)).send()
#         await SendMessage(context.user.id, caption).send()
#     else:
#         await SendMessage(context.user.id, T('main/qr_not_found_mt')).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.command('/draw')
async def start_message():
    if context.user.id not in data.admins:
        return

    T = data.current_T.get()

    async with aiohttp.ClientSession() as session:
        body = {"bot_hash": data.ad_hash, "type": "draw"}
        available_campaigns = {}
        async with session.post(data.api_url_available_campaigns, json=body) as resp:
            resp_json = await resp.json()
            if resp_json['result']:
                available_campaigns = resp_json['available-campaigns']
            else:
                await SendMessage(context.user.user_id, resp_json['error']).send()
                return

    print(available_campaigns)
    total = 0
    for campaign_name, item in available_campaigns.items():
        total += item['ordered_count'] - item['done_count']
    mt = T('draw/mt', campaigns=available_campaigns, total=total)
    await SendMessage(context.user.user_id, mt).send()

    yield commonwaiters.next_message()

    if context.message.text == 'start':
        # Create task for draw
        asyncio.create_task(start_draw(context.user.user_id, list(available_campaigns.keys())[0]))
        await SendMessage(context.user.user_id, T('draw/start_draw_mt')).send()
    else:
        await SendMessage(context.user.user_id, T('draw/not_start_draw_mt')).send()