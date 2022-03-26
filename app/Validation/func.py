from models import Company
from rocketgram import InlineKeyboard, SendMessage
import data


def get_progress(company: Company):
    progress = 0
    if company.name:
        progress += 1
    if company.code:
        progress += 1
    if company.contact_FIO:
        progress += 1
    if company.contact_phone:
        progress += 1
    if company.contact_email:
        progress += 1
    if company.extract_file_id:
        progress += 1
    return progress


async def send_reg_jur_message(user_id: int, T, company: Company):
    if company.is_on_check:
        await SendMessage(user_id, T('register/on_check_mt', company=company)).send()
        return

    progress = get_progress(company)

    kb = InlineKeyboard()
    kb.callback(T('reg_jur/add_name_bt', company=company), 'reg_jur_add_name').row()
    kb.callback(T('reg_jur/add_code_bt', company=company), 'reg_jur_add_code').row()
    kb.callback(T('reg_jur/add_contact_FIO_bt', company=company), 'reg_jur_add_contact_FIO_bt').row()
    kb.callback(T('reg_jur/add_contact_phone_bt', company=company), 'reg_jur_add_contact_phone_bt').row()
    kb.callback(T('reg_jur/add_contact_email_bt', company=company), 'reg_jur_add_contact_email_bt').row()
    kb.callback(T('reg_jur/add_extract_bt', company=company), 'reg_jur_add_extract_bt').row()
    kb.callback(T('reg_jur/send_bt', progress=progress), 'reg_jur_send').row()

    await data.bot.send(SendMessage(user_id,
                                    T('reg_jur/mt', progress=progress, company=company),
                                    reply_markup=kb.render()))