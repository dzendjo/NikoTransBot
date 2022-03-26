from mybot import router
from models import Company, User, Pass
import data
import tools
from .func import send_new_pass_message, generate_pas_num_id

from bson.objectid import ObjectId
from rocketgram import commonfilters, ChatType, context, AnswerCallbackQuery, ReplyKeyboardRemove
from rocketgram import SendMessage, SendPhoto, InputFile, ReplyKeyboard, InlineKeyboard
from rocketgram import commonwaiters, UpdateType, EditMessageCaption
from rocketgram import GetChatAdministrators, EditMessageText, SendDocument
from rocketgram.errors import RocketgramRequest400Error
from marshmallow.exceptions import ValidationError

from pprint import pp
import orjson
import datetime
import asyncio
from io import BytesIO, FileIO
import re
import pytz
import csv


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('create_pass')
async def register():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()

    company = await Company.find_one({'contact_user_id': context.user.id})
    pas = Pass(create_user_id=context.user.id, company_id=str(company.id))
    await pas.commit()

    await send_new_pass_message(context.user.id, T, pas)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('add_start_date')
async def register():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.callback.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    if pas.is_validated:
        await SendMessage(context.user.id, T('pass/pass_validated_mt', pas=pas)).send()
        return

    if pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    await SendMessage(context.user.id, T('new_pass/add_start_date_mt')).send()

    yield commonwaiters.next_message()

    try:
        date, time = context.message.text.split()
        day, month, year = date.split('.')
        hour, minute = time.split(':')

        start_date = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute),
                                       second=0, tzinfo=data.tz)
        pas.start_date = start_date
        pas.end_date = start_date + datetime.timedelta(hours=data.pass_active_hours)
        pas.num_id = await generate_pas_num_id(start_date)
        await pas.commit()
    except Exception as e:
        print(e)
        await SendMessage(context.user.id, T('new_pass/parse_date_error')).send()
        await asyncio.sleep(4)

    await send_new_pass_message(context.user.id, T, pas)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('add_vehicle_number')
async def register():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.callback.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    if pas.is_validated:
        await SendMessage(context.user.id, T('pass/pass_validated_mt', pas=pas)).send()
        return

    if pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    await SendMessage(context.user.id, T('new_pass/add_vehicle_number_mt')).send()

    yield commonwaiters.next_message()

    pas.vehicle_number = context.message.text
    await pas.commit()

    await send_new_pass_message(context.user.id, T, pas)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('add_trailer_number')
async def add_trailer_number():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.callback.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    if pas.is_validated:
        await SendMessage(context.user.id, T('pass/pass_validated_mt', pas=pas)).send()
        return

    if pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    await SendMessage(context.user.id, T('new_pass/add_trailer_number_mt')).send()

    yield commonwaiters.next_message()

    pas.trailer_number = context.message.text
    await pas.commit()

    await send_new_pass_message(context.user.id, T, pas)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('add_start_place')
async def add_start_place():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.callback.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    if pas.is_validated:
        await SendMessage(context.user.id, T('pass/pass_validated_mt', pas=pas)).send()
        return

    if pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    await SendMessage(context.user.id, T('new_pass/add_start_place_mt')).send()

    yield commonwaiters.next_message()

    pas.start_place = context.message.text
    await pas.commit()

    await send_new_pass_message(context.user.id, T, pas)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('add_end_place')
async def add_end_place():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.callback.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    if pas.is_validated:
        await SendMessage(context.user.id, T('pass/pass_validated_mt', pas=pas)).send()
        return

    if pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    await SendMessage(context.user.id, T('new_pass/add_end_place_mt')).send()

    yield commonwaiters.next_message()

    pas.end_place = context.message.text
    await pas.commit()

    await send_new_pass_message(context.user.id, T, pas)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('add_driver_FIO')
async def add_driver_FIO():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.callback.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    if pas.is_validated:
        await SendMessage(context.user.id, T('pass/pass_validated_mt', pas=pas)).send()
        return

    if pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    await SendMessage(context.user.id, T('new_pass/add_driver_FIO_mt')).send()

    yield commonwaiters.next_message()

    pas.driver_FIO = context.message.text
    await pas.commit()

    await send_new_pass_message(context.user.id, T, pas)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('add_driver_phone')
async def add_driver_phone():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.callback.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    if pas.is_validated:
        await SendMessage(context.user.id, T('pass/pass_validated_mt', pas=pas)).send()
        return

    if pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    await SendMessage(context.user.id, T('new_pass/add_driver_phone_mt')).send()

    yield commonwaiters.next_message()

    pas.driver_phone = context.message.text
    await pas.commit()

    await send_new_pass_message(context.user.id, T, pas)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('add_goods')
async def add_goods():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.callback.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    if pas.is_validated:
        await SendMessage(context.user.id, T('pass/pass_validated_mt', pas=pas)).send()
        return

    if pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    await SendMessage(context.user.id, T('new_pass/add_goods_mt'),disable_web_page_preview=True).send()

    yield commonwaiters.next_message()

    pas.goods = context.message.text
    await pas.commit()

    await send_new_pass_message(context.user.id, T, pas)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('pass_send_validation')
async def add_goods():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.callback.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    if pas.is_validated:
        await SendMessage(context.user.id, T('pass/pass_validated_mt', pas=pas)).send()
        return

    if pas.is_on_check:
        await SendMessage(context.user.id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    if pas.add_manager_date:
        pas.add_manager_date = None
    if pas.complete_date:
        pas.complete_date = None

    company = await Company.find_one(ObjectId(pas.company_id))

    pas.send_date = datetime.datetime.now(tz=data.tz)
    pas.is_on_check = True
    await pas.commit()

    # 1. Send message to channel
    kb = InlineKeyboard()
    kb.callback(T('pass/add_manager_bt'), f'pas_add_manager {pas.id}').row()
    await SendDocument(data.passes_channel_id, company.extract_file_id,
                       caption=T('pass/caption', pas=pas, company=company),
                       reply_markup=kb.render()).send()

    # 2. Send message to user
    await SendMessage(context.user.id, T('pass/pass_sent_mt')).send()


@router.handler
@commonfilters.update_type(UpdateType.callback_query)
@commonfilters.callback('pas_add_manager')
async def pas_add_manager():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.get_t('ua')

    pas_id = context.update.callback_query.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))
    company = await Company.find_one(ObjectId(pas.company_id))
    manager = await User.find_one(context.user.id)

    # 1. Add add_manager_date and message_id
    pas.add_manager_date = datetime.datetime.now(tz=data.tz)
    pas.message_id = context.message.message_id
    pas.manager_username = manager.username
    pas.manager_user_id = manager.id
    await pas.commit()

    # 2. Change keyboard and text
    kb = InlineKeyboard()
    kb.callback(T('pass/in_process_bt', pas=pas), f'pass_in_process {pas.id}').row()
    await EditMessageCaption(data.passes_channel_id, pas.message_id,
                             caption=T('pass/caption', pas=pas, company=company),
                             reply_markup=kb.render()).send()

    # 3. Send info to manager
    kb = InlineKeyboard()
    kb.callback(T('pass/validate_bt'), f'pass_validate {pas.id}').row()
    kb.callback(T('pass/reject_bt'), f'pass_reject {pas.id}').row()
    await SendDocument(pas.manager_user_id, company.extract_file_id,
                       caption=T('pass/caption', pas=pas, company=company),
                       reply_markup=kb.render()).send()

    # 4. Send notifacation add manager to client
    await SendMessage(pas.create_user_id, T('pass/add_manager_mt', pas=pas)).send()


@router.handler
@commonfilters.update_type(UpdateType.callback_query)
@commonfilters.callback('pass_in_process')
async def pass_in_process():
    T = data.get_t('ua')

    pas_id = context.update.callback_query.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))

    await AnswerCallbackQuery(context.update.callback_query.id, T('pass/in_process_cb_mt', pas=pas)).send()


############################################################
@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('pass_validate')
async def validation_approve():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.update.callback_query.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))
    company = await Company.find_one(ObjectId(pas.company_id))
    manager = await User.find_one(context.user.id)

    kb = ReplyKeyboard()
    kb.text(T('yes_no/yes'))
    kb.text(T('yes_no/no'))

    await SendMessage(context.user.id, T('pass/confirm_validate_mt'), reply_markup=kb.render()).send()

    yield commonwaiters.next_message()

    if context.message.text.lower() == T('yes_no/yes').lower():
        pas.is_validated = True
        pas.is_active = False
        pas.complete_date = datetime.datetime.now(tz=data.tz)
        await pas.commit()

        # 1. Send success message to admin
        await SendMessage(context.user.id,
                          T('pass/admin_approved_mt', pas=pas),
                          reply_markup=ReplyKeyboardRemove()).send()

        # 2. Change keyboard in channel
        kb = InlineKeyboard()
        kb.callback(T('pass/approved_cb_bt'),
                    f'channel_pas_approved {pas_id}').row()
        await EditMessageCaption(data.passes_channel_id,
                                 pas.message_id,
                                 caption=T('pass/caption', company=company, pas=pas),
                                 reply_markup=kb.render()).send()

        # 3. Send success message to client
        await SendMessage(pas.create_user_id, T('pass/client_approved_mt', company=company)).send()

        # 4. Generate QR code and documents
        qr_url = f'https://t.me/{data.bot.name}?start={pas_id}'
        qr_image = tools.create_qr_image(qr_url, without_caption=True)
        img_io = BytesIO()
        qr_image.save(img_io, 'PNG')
        qr_file = InputFile('qr.png', 'image/png', img_io.getvalue())

        caption = T('pass/qr_caption', pas=pas, company=company)
        m = await SendPhoto(pas.create_user_id, qr_file, caption=caption).send()

        pas.qr_file_id = m.photo[-1].file_id
        await pas.commit()

        # 5. Generate PDF file
        loop = asyncio.get_running_loop()
        doc_img = await loop.run_in_executor(None, tools.generate_document, pas, company)

        img_io = BytesIO()
        doc_img.save(img_io, 'PDF')
        pdf_file = InputFile('pass.pdf', 'application/pdf', img_io.getvalue())

        m = await SendDocument(pas.create_user_id, pdf_file).send()

        pas.pdf_file_id = m.document.file_id
        await pas.commit()

        # 5. Change keyboard for manager
        pass

    else:
        await SendMessage(context.user.id,
                          T('validation/admin_not_approved_mt', company=company),
                          reply_markup=ReplyKeyboardRemove()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('pass_reject')
async def validation_reject():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.update.callback_query.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))
    company = await Company.find_one(ObjectId(pas.company_id))

    kb = ReplyKeyboard()
    kb.text(T('yes_no/yes'))
    kb.text(T('yes_no/no'))

    await SendMessage(context.user.id, T('pass/confirm_reject_mt'), reply_markup=kb.render()).send()

    yield commonwaiters.next_message()

    if context.message.text.lower() == T('yes_no/yes').lower():
        await SendMessage(context.user.id, T('validation/reason_mt'), reply_markup=ReplyKeyboardRemove()).send()

        yield commonwaiters.next_message()

        pas.rejection_text = context.message.text
        await pas.commit()

        kb = InlineKeyboard()
        kb.callback(T('validation/send_reject_bt'), f'pas_send_rejection {pas_id}').row()
        kb.callback(T('validation/edit_reject_text_bt'), f'pas_edit_rejection {pas_id}').row()

        await SendMessage(context.user.id,
                          T('pass/reject_mt', company=company, pas=pas),
                          reply_markup=kb.render()).send()

    else:
        await SendMessage(context.user.id,
                          T('validation/reject_not_approved_mt', company=company),
                          reply_markup=ReplyKeyboardRemove()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('pas_edit_rejection')
async def validation_edit_rejection():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.update.callback_query.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))
    company = await Company.find_one(ObjectId(pas.company_id))

    await SendMessage(context.user.id, T('validation/reason_mt')).send()

    yield commonwaiters.next_message()

    pas.rejection_text = context.message.text
    await pas.commit()

    kb = InlineKeyboard()
    kb.callback(T('validation/send_reject_bt'), f'pas_send_rejection {pas_id}').row()
    kb.callback(T('validation/edit_reject_text_bt'), f'pas_edit_rejection {pas_id}').row()

    await SendMessage(context.user.id,
                      T('pass/reject_mt', company=company, pas=pas),
                      reply_markup=kb.render()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('pas_send_rejection')
async def validation_edit_rejection():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    pas_id = context.update.callback_query.data.split()[-1]
    pas = await Pass.find_one(ObjectId(pas_id))
    company = await Company.find_one(ObjectId(pas.company_id))

    pas.is_on_check = False
    pas.complete_date = datetime.datetime.now(tz=data.tz)
    await pas.commit()

    # 1. Send message to admin
    await SendMessage(context.user.id, T('validation/reject_send_admin_mt', company=company)).send()

    # 2. Change keyboard in channel
    kb = InlineKeyboard()
    kb.callback(T('validation/application_rejected_cb_bt'),
                f'channel_pass_rejected {pas_id}').row()
    await EditMessageCaption(data.passes_channel_id,
                             pas.message_id,
                             caption=T('pass/caption', company=company, pas=pas),
                             reply_markup=kb.render()).send()

    # 3. Send Message to client
    await SendMessage(pas.create_user_id, T('pass/reject_send_client_mt', pas=pas, )).send()


@router.handler
@commonfilters.update_type(UpdateType.callback_query)
@commonfilters.callback('channel_pass_rejected')
async def channel_application_rejected():
    T = data.get_t('ua')
    await AnswerCallbackQuery(context.update.callback_query.id, T('validation/application_rejected_cb_bt')).send()


@router.handler
@commonfilters.update_type(UpdateType.callback_query)
@commonfilters.callback('channel_pas_approved')
async def channel_application_approved():
    T = data.get_t('ua')
    await AnswerCallbackQuery(context.update.callback_query.id, T('pass/approved_cb_mt')).send()


#################################################
##############     Export     ###################
#################################################


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('export')
async def export_active():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()

    variant = context.callback.data.split()[-1]

    m = await SendMessage(context.user.id, T('export/start_export_mt')).send()

    passes = await Pass.find({}).to_list(None)
    now = datetime.datetime.now(tz=data.tz)

    header = ['Номер пропуска',
            'Имя компании',
            'Контактная особа',
            'Контактный телефон',
            'Дата начала пропуска',
            'Дата окончания пропуска',
            'Номер транспорта',
            'Номер прицепа',
            'Место старта',
            'Конечная точка',
            'Имя водителя',
            'Телефон водителя',
            'Перечень категорий',
            'Дата подачи заявления',
            'Дата выдачи пропуска',
            'Менеджер']

    file_name = 'active_passes.csv' if variant == 'active' else 'all_passes.csv'
    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for pas in passes:
            start_date = pas.start_date.replace(tzinfo=pytz.UTC).astimezone(data.tz)
            end_date = pas.end_date.replace(tzinfo=pytz.UTC).astimezone(data.tz)

            if variant == 'active' and (now <= start_date or now >= end_date):
                continue

            company = await Company.find_one(ObjectId(pas.company_id))
            row = [
                pas.num_id,
                company.name,
                company.contact_FIO,
                company.contact_phone,
                pas.start_date,
                pas.end_date,
                pas.vehicle_number,
                pas.trailer_number,
                pas.start_place,
                pas.end_place,
                pas.driver_FIO,
                pas.driver_phone,
                pas.goods,
                pas.send_date,
                pas.complete_date,
                pas.manager_username
            ]
            writer.writerow(row)

    await SendDocument(context.user.id, InputFile(file_name, 'text/csv', FileIO(file_name))).send()
    await EditMessageText(T('export/end_export_mt'), context.user.id, m.message_id).send()



