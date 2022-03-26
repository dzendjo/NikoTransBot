import datetime

from models import Pass, Company
from rocketgram import InlineKeyboard, SendMessage
import data
import random
import asyncio


async def generate_pas_num_id(start_date: datetime.datetime) -> str:
    for i in range(100):
        num = random.randint(100000, 999999)

        day_str = str(start_date.day + data.secret_number)
        if len(day_str) == 1:
            day_str = f'0{day_str}'

        num_list = list(str(num))
        num_list[1] = day_str[0]
        num_list[4] = day_str[1]
        num_str = ''.join(num_list)

        pas = await Pass.find_one({'num_id': str(num_str)})
        if pas:
            continue
        else:
            return num_str


def get_progress(pas: Pass):
    progress = 0
    if pas.start_date:
        progress += 1
    if pas.vehicle_number:
        progress += 1
    if pas.start_place:
        progress += 1
    if pas.end_place:
        progress += 1
    if pas.driver_FIO:
        progress += 1
    if pas.driver_phone:
        progress += 1
    if pas.goods:
        progress += 1
    return progress


async def send_new_pass_message(user_id: int, T, pas: Pass):
    if pas.is_on_check:
        await SendMessage(user_id, T('pass/pass_on_check_mt', pas=pas)).send()
        return

    progress = get_progress(pas)

    if not pas.is_active and progress:
        pas.is_active = True
        await pas.commit()

    kb = InlineKeyboard()
    kb.callback(T('new_pass/add_start_date_bt', pas=pas), f'add_start_date {pas.id}').row()
    kb.callback(T('new_pass/add_vehicle_number_bt', pas=pas), f'add_vehicle_number {pas.id}').row()
    kb.callback(T('new_pass/add_trailer_number_bt', pas=pas), f'add_trailer_number {pas.id}').row()
    kb.callback(T('new_pass/add_start_place_bt', pas=pas), f'add_start_place {pas.id}').row()
    kb.callback(T('new_pass/add_end_place_bt', pas=pas), f'add_end_place {pas.id}').row()
    kb.callback(T('new_pass/add_driver_FIO_bt', pas=pas), f'add_driver_FIO {pas.id}').row()
    kb.callback(T('new_pass/add_driver_phone_bt', pas=pas), f'add_driver_phone {pas.id}').row()
    kb.callback(T('new_pass/add_goods_bt', pas=pas), f'add_goods {pas.id}').row()
    kb.callback(T('new_pass/send_bt', pas=pas, progress=progress), f'pass_send_validation {pas.id}').row()

    await data.bot.send(SendMessage(user_id, T('new_pass/mt', pas=pas, progress=progress), reply_markup=kb.render()))


if __name__ == '__main__':
    print(asyncio.run(generate_pas_num_id(datetime.datetime.now())))