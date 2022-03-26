from mybot import router
from models import User, QRCode, Pass
from data import jinja
import data
import filters
import tools

from bson.objectid import ObjectId
from rocketgram import commonfilters, ChatType, context, AnswerCallbackQuery, InputFile, ParseModeType
from rocketgram import SendMessage, SendPhoto, InputMediaPhoto, EditMessageMedia, InlineKeyboard
from rocketgram import commonwaiters, UpdateType, AnswerInlineQuery, InlineQueryResultArticle
from rocketgram import InputTextMessageContent, InlineKeyboardMarkup, ReplyKeyboard, ReplyKeyboardRemove
from rocketgram.errors import RocketgramRequest400Error

from pprint import pp
import orjson
import datetime
import asyncio
from io import BytesIO
import re


url_pattern = re.compile(r'(?P<url>(mailto:|https?:\/\/)(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#()?&//=]*))')
pattern = re.compile('^[A-Za-z0-9]+$')


# @router.handler
# @commonfilters.chat_type(ChatType.private)
# @commonfilters.callback('set_controller')
# async def download_link():
#     await AnswerCallbackQuery(context.update.callback_query.id).send()
#     T = data.current_T.get()
#
#     await SendMessage(context.user.id, T('controller/mt')).send()
#
#
# @router.handler
# @commonfilters.chat_type(ChatType.private)
# @commonfilters.callback('set_driver')
# async def download_link():
#     await AnswerCallbackQuery(context.update.callback_query.id).send()
#     T = data.current_T.get()
#     user = data.current_user.get()
#
#     if not user.FIO or not user.phone or not user.vehicles:
#         await SendMessage(context.user.id, T('reg/mt')).send()
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
#         # Check Vehicle
#         if not user.vehicles:
#             await SendMessage(context.user.id, T('reg/vehicle_mt')).send()
#             yield commonwaiters.next_message()
#
#             if not pattern.match(context.message.text):
#                 await SendMessage(context.user.id, T('reg/vehicle_error')).send()
#                 return
#
#             vehicle = Vehicle(number=context.message.text, driver_id=str(user.id))
#             await vehicle.commit()
#
#             user.vehicles.append({'number': context.message.text, 'id': vehicle.id})
#             await user.commit()
#
#         user.is_registered = True
#         await user.commit()
#
#         await SendMessage(context.user.id, T('reg/finish_mt')).send()
#
#
# @router.handler
# @commonfilters.chat_type(ChatType.private)
# @commonfilters.callback('create_pass')
# async def create_pass():
#     await AnswerCallbackQuery(context.update.callback_query.id).send()
#     T = data.current_T.get()
#     user = data.current_user.get()
#
#     kb = InlineKeyboard()
#     kb.inline_current(T('pass/create/search_bt'), switch_inline_query_current_chat='#search_vehicle ').row()
#     await SendMessage(user.id, T('pass/create/mt1'), reply_markup=kb.render()).send()
#
#
# @router.handler
# @commonfilters.update_type(UpdateType.inline_query)
# @commonfilters.inline('#search_vehicle')
# @filters.admin_require()
# async def inline_goods_choosing():
#     T = data.get_t('ru')
#     query = context.update.inline_query.query.split(' ')[-1]
#     inline_items = []
#
#     if query != '#search_vehicle':
#         items = await Vehicle.find({'number': {'$regex': query}}).to_list(None)
#     else:
#         items = await Vehicle.find({}).sort("_id", -1).to_list(10)
#
#     for i, item in enumerate(items):
#         mt = InputTextMessageContent(message_text=T('pass/create/vehicle_mt', vehicle=item),
#                                      parse_mode=ParseModeType.html)
#         kb = InlineKeyboard()
#         kb.callback(T('pass/create/vehicle_bt'), f'create_pass_with_vehicle {item.number}').row()
#         inline_item = InlineQueryResultArticle(i, item.number,
#                                                input_message_content=mt,
#                                                reply_markup=kb.render())
#         inline_items.append(inline_item)
#
#     if not inline_items:
#         mt = InputTextMessageContent(message_text=T('pass/create/not_found_mt'),
#                                      parse_mode=ParseModeType.html)
#         inline_item = InlineQueryResultArticle(0, T('pass/create/not_found_mt'),
#                                                input_message_content=mt)
#         inline_items.append(inline_item)
#
#     await AnswerInlineQuery(context.update.inline_query.id, inline_items, cache_time=10).send()
#
#
# async def send_new_pass_message(user_id, T, new_pass, vehicle):
#     kb = InlineKeyboard()
#     kb.callback(T('pass/create/add_date_bt', new_pass=new_pass), f'pass_add_date {new_pass.id}').row()
#     kb.callback(T('pass/create/add_comment_bt', new_pass=new_pass), f'pass_add_comment {new_pass.id}').row()
#     kb.callback(T('pass/create/create_pass_bt'), f'pass_create_pass {new_pass.id}').row()
#     await data.bot.send(SendMessage(user_id,
#                                     T('pass/create/mt_main', vehicle=vehicle, new_pass=new_pass),
#                                     reply_markup=kb.render()))
#
#
# @router.handler
# @commonfilters.update_type(UpdateType.callback_query)
# @commonfilters.callback('create_pass_with_vehicle')
# async def create_pass_with_vehicle():
#     await AnswerCallbackQuery(context.update.callback_query.id).send()
#     T = data.get_t('ru')
#
#     number = context.update.callback_query.data.split()[-1]
#     vehicle = await Vehicle.find_one({'number': number})
#     new_pass = Pass(vehicle_number=number)
#     await new_pass.commit()
#
#     await send_new_pass_message(context.user.id, T, new_pass, vehicle)
#
#
# @router.handler
# @commonfilters.chat_type(ChatType.private)
# @commonfilters.callback('pass_add_date')
# async def pass_add_date():
#     await AnswerCallbackQuery(context.update.callback_query.id).send()
#     T = data.current_T.get()
#     user = data.current_user.get()
#     new_pass = await Pass.find_one(ObjectId(context.callback.data.split()[-1]))
#     vehicle = await Vehicle.find_one({'number': new_pass.vehicle_number})
#
#     kb = ReplyKeyboard()
#     kb.text(T('pass/create/today_bt'))
#     kb.text(T('pass/create/tomorrow_bt'))
#     kb.text(T('pass/create/own_bt'))
#     kb.arrange_scheme((2, 1))
#     await SendMessage(context.user.id, T('pass/create/mt2'), reply_markup=kb.render()).send()
#
#     yield commonwaiters.next_message()
#
#     now = datetime.datetime.utcnow()
#     if context.message.text == T('pass/create/own_bt'):
#         await SendMessage(context.user.id, T('pass/create/enter_date_mt'), reply_markup=ReplyKeyboardRemove()).send()
#
#         # Parse datetime
#         yield commonwaiters.next_message()
#         new_pass.end_date = (now + datetime.timedelta(hours=24)).replace(hour=23, minute=59, second=59)
#
#     if context.message.text == T('pass/create/today_bt'):
#         new_pass.end_date = now.replace(hour=23, minute=59, second=59)
#     elif context.message.text == T('pass/create/tomorrow_bt'):
#         new_pass.end_date = (now + datetime.timedelta(hours=24)).replace(hour=23, minute=59, second=59)
#
#     await new_pass.commit()
#
#     await SendMessage(context.user.id, T('pass/create/date_saved_mt'), reply_markup=ReplyKeyboardRemove()).send()
#     await send_new_pass_message(context.user.id, T, new_pass, vehicle)
#
#
# @router.handler
# @commonfilters.chat_type(ChatType.private)
# @commonfilters.callback('pass_add_comment')
# async def pass_add_comment():
#     await AnswerCallbackQuery(context.update.callback_query.id).send()
#     T = data.current_T.get()
#     user = data.current_user.get()
#     new_pass = await Pass.find_one(ObjectId(context.callback.data.split()[-1]))
#     vehicle = await Vehicle.find_one({'number': new_pass.vehicle_number})
#
#     await SendMessage(context.user.id, T('pass/create/mt3')).send()
#
#     yield commonwaiters.next_message()
#     new_pass.comment = context.message.text
#     await new_pass.commit()
#
#     await SendMessage(context.user.id, T('pass/create/comment_saved_mt')).send()
#     await send_new_pass_message(context.user.id, T, new_pass, vehicle)
#
#
# @router.handler
# @commonfilters.chat_type(ChatType.private)
# @commonfilters.callback('pass_create_pass')
# async def pass_create_pass():
#     await AnswerCallbackQuery(context.update.callback_query.id).send()
#     T = data.current_T.get()
#     user = data.current_user.get()
#     new_pass = await Pass.find_one(ObjectId(context.callback.data.split()[-1]))
#     vehicle = await Vehicle.find_one({'number': new_pass.vehicle_number})
#
#     # 1. Create QR code
#     qr_data = {
#         'pass_id': str(new_pass.id),
#         'message': 'For recognize this QR use @nikotransbot'
#     }
#     qr_image = tools.create_qr_image(orjson.dumps(qr_data), without_caption=True)
#     img_io = BytesIO()
#     qr_image.save(img_io, 'PNG')
#     qr_file = InputFile('qr.png', 'image/png', img_io.getvalue())
#
#     caption = T('pass/create/qr_caption', new_pass=new_pass, vehicle=vehicle)
#     await SendPhoto(context.user.id, qr_file, caption=caption).send()
#
#     # 2. Send message to user
#     driver = await User.find_one(vehicle.driver_id)
#     await SendMessage(context.user.id, T('pass/create/complete_pass_mt', vehicle=vehicle, driver=driver)).send()
#
#     # 3. Send to driver
#     await SendPhoto(driver.id, qr_file, caption=caption).send()

    # Add without caption file_id to DB
    # qr.qr_without_caption_id = m.photo[-1].file_id
    # await qr.commit()

    # 3. Send QR code to driver and admin

