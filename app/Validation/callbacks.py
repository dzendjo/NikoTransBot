from mybot import router
from models import Company, User
import data
import tools
from .func import send_reg_jur_message

from bson.objectid import ObjectId
from rocketgram import commonfilters, ChatType, context, AnswerCallbackQuery, ReplyKeyboardRemove
from rocketgram import SendMessage, SendPhoto, EditMessageReplyMarkup, ReplyKeyboard, InlineKeyboard
from rocketgram import commonwaiters, UpdateType, EditMessageCaption
from rocketgram import InputTextMessageContent, MessageType, SendDocument
from rocketgram.errors import RocketgramRequest400Error
from marshmallow.exceptions import ValidationError

from pprint import pp
import orjson
import datetime
import asyncio
from io import BytesIO
import re


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('register')
async def register():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()

    kb = InlineKeyboard()
    kb.callback(T('reg_cb/jur_bt'), 'reg_jur').row()
    kb.callback(T('reg_cb/fiz_bt'), 'reg_fiz').row()

    await SendMessage(context.user.id, T('reg_cb/mt'), reply_markup=kb.render()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('reg_fiz')
async def register():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()

    await SendMessage(context.user.id, T('reg_fiz/mt')).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('reg_jur')
async def register():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})

    if not company:
        company = Company(contact_user_id=context.user.id)
        await company.commit()

    await send_reg_jur_message(context.user.id, T, company=company)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('reg_jur_add_name')
async def reg_jur_add_name():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})

    if company.is_on_check:
        await SendMessage(context.user.id, T('register/on_check_mt', company=company)).send()
        return

    await SendMessage(context.user.id, T('reg_jur/add_name_mt')).send()

    yield commonwaiters.next_message()

    company.name = context.message.text
    await company.commit()

    await send_reg_jur_message(context.user.id, T, company=company)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('reg_jur_add_code')
async def reg_jur_add_code():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})

    if company.is_on_check:
        await SendMessage(context.user.id, T('register/on_check_mt', company=company)).send()
        return

    await SendMessage(context.user.id, T('reg_jur/add_code_mt')).send()

    yield commonwaiters.next_message()

    company.code = context.message.text
    await company.commit()

    await send_reg_jur_message(context.user.id, T, company=company)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('reg_jur_add_contact_FIO_bt')
async def reg_jur_add_contact_fio_bt():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})

    if company.is_on_check:
        await SendMessage(context.user.id, T('register/on_check_mt', company=company)).send()
        return

    await SendMessage(context.user.id, T('reg_jur/add_contact_FIO_mt')).send()

    yield commonwaiters.next_message()

    company.contact_FIO = context.message.text
    await company.commit()

    await send_reg_jur_message(context.user.id, T, company=company)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('reg_jur_add_contact_phone_bt')
async def reg_jur_add_contact_phone_bt():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})

    if company.is_on_check:
        await SendMessage(context.user.id, T('register/on_check_mt', company=company)).send()
        return

    await SendMessage(context.user.id, T('reg_jur/add_contact_phone_mt')).send()

    yield commonwaiters.next_message()

    company.contact_phone = context.message.text
    await company.commit()

    await send_reg_jur_message(context.user.id, T, company=company)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('reg_jur_add_contact_email_bt')
async def reg_jur_add_contact_email_bt():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})

    if company.is_on_check:
        await SendMessage(context.user.id, T('register/on_check_mt', company=company)).send()
        return

    await SendMessage(context.user.id, T('reg_jur/add_contact_email_mt')).send()

    yield commonwaiters.next_message()

    try:
        company.contact_email = context.message.text
        await company.commit()
    except ValidationError as e:
        await SendMessage(context.user.id, T('reg_jur/email_vaild_error_mt')).send()

    await send_reg_jur_message(context.user.id, T, company=company)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('reg_jur_add_extract_bt')
async def reg_jur_add_extract_bt():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})

    if company.is_on_check:
        await SendMessage(context.user.id, T('register/on_check_mt', company=company)).send()
        return

    await SendMessage(context.user.id, T('reg_jur/add_extract_mt')).send()

    yield commonwaiters.next_message(MessageType.photo, MessageType.document)

    # Add document
    if context.message.type == MessageType.document and context.message.document.mime_type == 'application/pdf':
        company.extract_file_id = context.message.document.file_id
        await company.commit()
    else:
        await SendMessage(context.user.id, T('reg_jur/extract_format_error')).send()

    await send_reg_jur_message(context.user.id, T, company=company)


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('reg_jur_send')
async def reg_jur_send():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company = await Company.find_one({'contact_user_id': context.user.id})

    if company.is_on_check:
        await SendMessage(context.user.id, T('register/on_check_mt', company=company)).send()
        return

    # 2. Make company checked and send message to user
    company.is_on_check = True
    company.application_create_date = datetime.datetime.now(tz=data.tz)
    if company.application_add_manager_date:
        company.application_add_manager_date = None
    if company.application_complete_date:
        company.application_complete_date = None
    await company.commit()

    # 2. Send info to admin channel
    kb = InlineKeyboard()
    kb.callback(T('validation/process_bt'), f'validation_add_manager {company.num_id}').row()

    await SendDocument(data.validation_channel_id,
                       company.extract_file_id,
                       caption=T('validation/caption', company=company),
                       reply_markup=kb.render()).send()

    await SendMessage(context.user.id, T('validation/sent_mt')).send()


@router.handler
@commonfilters.update_type(UpdateType.callback_query)
@commonfilters.callback('validation_add_manager')
async def validation_add_manager():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.get_t('ua')

    company_num_id = int(context.update.callback_query.data.split()[-1])
    company = await Company.find_one({'num_id': company_num_id})

    company.application_add_manager_date = datetime.datetime.now(tz=data.tz)
    company.message_id = context.message.message_id
    await company.commit()

    # 1. Edit message keyboard in channel
    await EditMessageCaption(data.validation_channel_id,
                             context.message.message_id,
                             caption=T('validation/caption', company=company)).send()

    kb = InlineKeyboard()
    kb.callback(T('validation/in_process_bt', company=company), f'validation_in_progress {context.user.id}').row()
    await EditMessageReplyMarkup(data.validation_channel_id,
                                 context.message.message_id,
                                 reply_markup=kb.render()).send()

    # 2. Send process message to admin user
    kb = InlineKeyboard()
    kb.callback(T('validation/approve_bt'), f'validation_approve {company.num_id}').row()
    kb.callback(T('validation/reject_bt'), f'validation_reject {company.num_id}').row()

    await SendDocument(context.user.id,
                       company.extract_file_id,
                       caption=T('validation/caption', company=company),
                       reply_markup=kb.render()).send()


@router.handler
@commonfilters.update_type(UpdateType.callback_query)
@commonfilters.callback('validation_in_progress')
async def validation_in_progress():
    T = data.get_t('ua')
    user_id = int(context.update.callback_query.data.split()[-1])
    user = await User.find_one(user_id)

    await AnswerCallbackQuery(context.update.callback_query.id, T('validation/in_process_cb_mt', user=user)).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('validation_approve')
async def validation_approve():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company_num_id = int(context.callback.data.split()[-1])
    company = await Company.find_one({'num_id': company_num_id})

    kb = ReplyKeyboard()
    kb.text(T('yes_no/yes'))
    kb.text(T('yes_no/no'))

    await SendMessage(context.user.id, T('validation/approve_mt', company=company), reply_markup=kb.render()).send()

    yield commonwaiters.next_message()

    if context.message.text.lower() == T('yes_no/yes').lower():
        company.is_validated = True
        company.application_complete_date = datetime.datetime.now(tz=data.tz)
        await company.commit()

        # 1. Send success message to admin
        await SendMessage(context.user.id,
                          T('validation/admin_approved_mt', company=company),
                          reply_markup=ReplyKeyboardRemove()).send()

        # 2. Change keyboard in channel
        await EditMessageCaption(data.validation_channel_id,
                                 company.message_id,
                                 caption=T('validation/caption', company=company)).send()

        kb = InlineKeyboard()
        kb.callback(T('validation/application_approved_cb_bt'),
                    f'channel_application_approved {company.num_id}').row()
        await EditMessageReplyMarkup(data.validation_channel_id, company.message_id, reply_markup=kb.render()).send()


        # 3. Send success message to client
        await SendMessage(company.contact_user_id, T('validation/client_approved_mt', company=company)).send()

    else:
        await SendMessage(context.user.id,
                          T('validation/admin_not_approved_mt', company=company),
                          reply_markup=ReplyKeyboardRemove()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('validation_reject')
async def validation_reject():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company_num_id = int(context.callback.data.split()[-1])
    company = await Company.find_one({'num_id': company_num_id})

    kb = ReplyKeyboard()
    kb.text(T('yes_no/yes'))
    kb.text(T('yes_no/no'))

    await SendMessage(context.user.id, T('validation/reject_confirm_mt', company=company), reply_markup=kb.render()).send()

    yield commonwaiters.next_message()

    if context.message.text.lower() == T('yes_no/yes').lower():
        await SendMessage(context.user.id, T('validation/reason_mt'), reply_markup=ReplyKeyboardRemove()).send()

        yield commonwaiters.next_message()

        company.rejection_text = context.message.text
        await company.commit()

        kb = InlineKeyboard()
        kb.callback(T('validation/send_reject_bt'), f'validation_send_rejection {company_num_id}').row()
        kb.callback(T('validation/edit_reject_text_bt'), f'validation_edit_rejection {company_num_id}').row()

        await SendMessage(context.user.id, T('validation/reject_mt', company=company), reply_markup=kb.render()).send()

    else:
        await SendMessage(context.user.id,
                          T('validation/reject_not_approved_mt', company=company),
                          reply_markup=ReplyKeyboardRemove()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('validation_edit_rejection')
async def validation_edit_rejection():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company_num_id = int(context.callback.data.split()[-1])
    company = await Company.find_one({'num_id': company_num_id})

    await SendMessage(context.user.id, T('validation/reason_mt')).send()

    yield commonwaiters.next_message()

    company.rejection_text = context.message.text
    await company.commit()

    kb = InlineKeyboard()
    kb.callback(T('validation/send_reject_bt'), f'validation_send_rejection {company_num_id}').row()
    kb.callback(T('validation/edit_reject_text_bt'), f'validation_edit_rejection {company_num_id}').row()

    await SendMessage(context.user.id, T('validation/reject_mt', company=company), reply_markup=kb.render()).send()


@router.handler
@commonfilters.chat_type(ChatType.private)
@commonfilters.callback('validation_send_rejection')
async def validation_edit_rejection():
    await AnswerCallbackQuery(context.update.callback_query.id).send()
    T = data.current_T.get()
    company_num_id = int(context.callback.data.split()[-1])
    company = await Company.find_one({'num_id': company_num_id})

    company.is_on_check = False
    company.application_complete_date = datetime.datetime.now(tz=data.tz)
    await company.commit()

    # 1. Send message to admin
    await SendMessage(context.user.id, T('validation/reject_send_admin_mt', company=company)).send()

    # 2. Change keyboard in channel
    await EditMessageCaption(data.validation_channel_id,
                             company.message_id,
                             caption=T('validation/caption', company=company)).send()

    kb = InlineKeyboard()
    kb.callback(T('validation/application_rejected_cb_bt'),
                f'channel_application_rejected {company.num_id}').row()
    await EditMessageReplyMarkup(data.validation_channel_id, company.message_id, reply_markup=kb.render()).send()

    # 3. Send Message to client
    await SendMessage(company.contact_user_id, T('validation/reject_send_client_mt', company=company)).send()


@router.handler
@commonfilters.update_type(UpdateType.callback_query)
@commonfilters.callback('channel_application_rejected')
async def channel_application_rejected():
    T = data.get_t('ua')

    company_num_id = int(context.update.callback_query.data.split()[-1])
    company = await Company.find_one({'num_id': company_num_id})
    user = await User.find_one(company.contact_user_id)

    await AnswerCallbackQuery(context.update.callback_query.id,
                              T('validation/application_rejected_cb_mt', company=company, user=user)).send()


@router.handler
@commonfilters.update_type(UpdateType.callback_query)
@commonfilters.callback('channel_application_approved')
async def channel_application_approved():
    T = data.get_t('ua')

    company_num_id = int(context.update.callback_query.data.split()[-1])
    company = await Company.find_one({'num_id': company_num_id})
    user = await User.find_one(company.contact_user_id)

    await AnswerCallbackQuery(context.update.callback_query.id,
                              T('validation/application_approved_cb_mt', company=company, user=user)).send()
