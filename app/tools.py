import datetime

# import data
from models import User, Pass, Company
import asyncio
from urllib.parse import urlparse, parse_qs
import re
import json
import qrcode
from PIL import ImageDraw, ImageFont, Image, ImageOps
from io import BytesIO
from string import ascii_letters
import textwrap
from rocketgram import GetFile, context
from aiohttp import ClientSession, FormData
from zoneinfo import ZoneInfo
import pytz
from bson.objectid import ObjectId


async def register_user(rg_user):
    now = datetime.datetime.now()

    user = User()
    user.id = rg_user.user_id
    user.created = now
    user.visited = now
    user.username = rg_user.username
    user.first_name = rg_user.first_name
    user.last_name = rg_user.last_name
    user.language_code = rg_user.language_code
    user.language = 'ua'

    # print(user)

    await user.commit()
    return user


def to_k(count):

    if count == None:
        return 0

    try:
        if count and isinstance(count, str):
            count = int(count)
    except:
        return 0

    if count > 1000000:
        return f'{count // 1000000}.{str(count % 1000000)[0]}M'
    elif count > 1000:
        return f'{count // 1000}.{str(count % 1000)[0]}K'
    else:
        return count


def to_mb(count, need_sep=True):

    if count == None or count == 0:
        return ''

    try:
        if count and isinstance(count, str):
            count = int(count)
    except:
        return 0

    first_part = ''
    if need_sep:
        first_part = '- '

    if count > 1024 * 1024:
        return f'{first_part}{count // (1024 * 1024)}.{str(count % (1024 * 1024))[0]}MB'
    elif count > 1024:
        return f'{first_part}{count // 1024}.{str(count % 1024)[0]}KB'
    else:
        return f'{first_part}{count}B'


def to_t(seconds):
    hours = seconds // 60 // 60
    seconds = seconds - hours * 60 * 60
    minutes = seconds // 60
    seconds = seconds - minutes * 60

    result = list()

    if hours:
        result.append("%02.0f" % hours)

    result.append("%02.0f" % minutes)
    result.append("%02.0f" % seconds)

    return ":".join(result)


def dt_filter(value):
    try:
        tz = pytz.timezone('Europe/Kiev')
        dt_format = '%H:%M:%S'
        if value.utcoffset():
            return value.strftime(dt_format)
        else:
            return value.replace(tzinfo=pytz.utc).astimezone(tz).strftime(dt_format)
    except Exception as e:
        print('Exception in filter: ', e)
        return value


def dt_ext_filter(value):
    try:
        tz = pytz.timezone('Europe/Kiev')
        dt_format = '%d.%m.%Y %H:%M'
        if value.utcoffset():
            return value.strftime(dt_format)
        else:
            return value.replace(tzinfo=pytz.utc).astimezone(tz).strftime(dt_format)
    except Exception as e:
        print('Exception in filter: ', e)
        return value


def sort_by_label(list):
    re_cypher = re.compile('\d*')

    def sort_func(item):
        cypher = re_cypher.search(item['label']).group()
        if cypher:
            return int(cypher)
        else:
            return 2000

    return sorted(list, key=sort_func)


async def get_model_keys(model):
    return list([str(item) for item in model.schema.fields])


def create_qr_image(caption, without_caption=False):
    try:
        qr_img = qrcode.make(caption, box_size=20, border=2)
    except qrcode.exceptions.DataOverflowError:
        return None

    if without_caption:
        return qr_img

    # Determine font
    font = ImageFont.truetype("UbuntuMono-Regular.ttf", 16)

    # Determine count of letters for current img size
    avg_char_width = sum(font.getsize(char)[0] for char in ascii_letters) / len(ascii_letters)
    max_char_count = int(((qr_img.size[0] * .95) - 80) / avg_char_width)

    # Create a wrapped text object using scaled character count
    lines = textwrap.wrap(caption, width=max_char_count)
    optimized_caption = '\n'.join(lines)

    # Create base text image
    text_img = Image.new('RGB', (qr_img.size[0], 16), color='white')
    draw = ImageDraw.Draw(text_img)

    # Define text block sizes
    text_block_width, text_block_height = draw.multiline_textsize(optimized_caption, font=font)

    # Create text image
    text_img = Image.new('RGB', (qr_img.size[0], text_block_height + 40), color='white')
    draw = ImageDraw.Draw(text_img)
    draw.multiline_text(((qr_img.size[0] - text_block_width) / 2, 20), optimized_caption, font=font, fill=(0, 0, 0))
    cur_x = 0
    cur_y = 0
    for x in range(cur_x, qr_img.size[0], 8):
        draw.line([(x, cur_y), (x + 4, cur_y)], fill=(0, 0, 0), width=6)

    # Unite images to final image
    main_image = Image.new('RGB', (qr_img.size[0], qr_img.size[1] + text_img.size[1]), (250, 250, 250))
    main_image.paste(qr_img, (0, 0))
    main_image.paste(text_img, (0, qr_img.size[1]))
    return main_image


async def file_upload_to_telegraph(file_id):
    response = await GetFile(file_id).send()
    API_FILE_URL = 'https://api.telegram.org/file/bot{}/'.format(context.bot.token)
    url = API_FILE_URL + response.file_path

    session: ClientSession = context.bot.connector._session

    response = await session.get(url)
    file_data = await response.read()

    form = FormData()
    form.add_field('file', file_data)

    async with session.post('https://telegra.ph/upload', data=form) as response:
        resp_json = await response.json()
        p = resp_json[0]['src']
        attach = f'https://telegra.ph{p}'
        return attach


def format_name(name: str, y_phone_cord: int) -> (str, int):
    name_words = name.split()
    name_words = list([f'{word} ' for word in name_words])
    if len(name_words) > 2:
        name_words.insert(2, '\n')
        y_phone_cord += 62
    new_name = ''.join(name_words)
    return new_name, y_phone_cord


def generate_document(pas: Pass, company: Company, qr_img: Image) -> Image:
    document_number_font = ImageFont.truetype("montserrat_extra_bold.ttf", 100)
    vehicle_number_font = ImageFont.truetype("montserrat_bold.ttf", 86)
    phone_font = ImageFont.truetype("Montserrat-Regular.ttf", 62)
    name_font = ImageFont.truetype("Montserrat-SemiBold.ttf", 62)
    category_font = ImageFont.truetype("Montserrat-SemiBold.ttf", 52)
    img = Image.open("base_without_sign.png")
    line_img = Image.open("line.png")
    draw = ImageDraw.Draw(img)
    tz = pytz.timezone('Europe/Kiev')

    # Pass number
    draw.text((1600, 210), pas.num_id, (0, 0, 0), font=document_number_font)

    # Vehicle number
    draw.text((960, 620), pas.vehicle_number, (0, 0, 0), font=vehicle_number_font)

    # Trailer number
    trailer_number = pas.trailer_number if pas.trailer_number else '------'
    draw.text((1600, 620), trailer_number, (0, 0, 0), font=vehicle_number_font)

    # Start date
    start_date = pas.start_date.replace(tzinfo=pytz.utc).astimezone(tz).strftime('%d.%m.%Y %H:%M').replace(' ', ', ')
    draw.text((960, 900), start_date, (0, 0, 0), font=vehicle_number_font)

    # End date
    end_date = pas.end_date.replace(tzinfo=pytz.utc).astimezone(tz).strftime('%d.%m.%Y %H:%M').replace(' ', ', ')
    draw.text((960, 1010), end_date, (0, 0, 0), font=vehicle_number_font)

    # Driver name
    name, y_phone_cord = format_name(pas.driver_FIO, 1480)
    draw.text((250, 1380), name, (0, 0, 0), font=name_font)

    # Driver phone
    draw.text((250, y_phone_cord), str(pas.driver_phone), (0, 0, 0), font=phone_font)

    # Owner name
    name, y_phone_cord = format_name(company.contact_FIO, 1480)
    draw.text((1300, 1380), name, (0, 0, 0), font=name_font)

    # Owner phone
    draw.text((1300, y_phone_cord), company.contact_phone, (0, 0, 0), font=phone_font)

    # Start place
    start_place = pas.start_place.upper()
    x_cord = 400

    if len(start_place.split()) > 1 or vehicle_number_font.getsize(start_place)[0] > 700:
        start_place = '\n'.join(start_place.split())
        x_cord = 250

    if len(start_place.split('-')) > 1:
        start_place = '\n'.join(start_place.split('-'))
        x_cord = 250

    draw.text((x_cord, 1740), start_place, (0, 0, 0), font=vehicle_number_font, align='center')

    # End place
    end_place = pas.end_place.upper()
    x_cord = 1500
    if len(end_place.split()) > 1 or vehicle_number_font.getsize(start_place)[0] > 700:
        end_place = '\n'.join(end_place.split())

    if len(end_place.split('-')) > 1:
        end_place = '\n'.join(end_place.split('-'))

    draw.text((x_cord, 1740), end_place, (0, 0, 0), font=vehicle_number_font, align='center')

    # Category list
    category_list = pas.goods

    x_cord_name = 150
    x_cord_weight = 1360
    y_cord = 2180

    for line in category_list.split('\n'):
        if '-' in line:
            name, weight = line.split('-')
        else:
            name, weight = line.split()
        draw.text((x_cord_name, y_cord), name.strip(), (0, 0, 0), font=category_font)
        draw.text((x_cord_weight, y_cord), weight.strip(), (0, 0, 0), font=category_font)
        y_cord += 120
        img.paste(line_img, (x_cord_name-26, y_cord-31))

    # Draw logistics head name
    # logistic_head_name = 'Гайдаржи\nВалентин Васильович'
    # draw.text((130, 3150), logistic_head_name, (0, 0, 0), font=name_font, align='center')

    # Draw date
    current_date = pas.complete_date.strftime('%d.%m.%Y')
    draw.text((1800, 3200), current_date, (0, 0, 0), font=name_font, align='center')

    # Draw QR code
    img.paste(qr_img, (130, 440))

    # Draw sign
    # sign = Image.open('sign.png')
    # sign = sign.resize((277, 325))

    # img = img.convert("RGBA")
    # sign = sign.convert("RGBA")
    # img.paste(sign, (1900, 3090), sign)

    # img.show()

    return img.convert("RGB")


if __name__ == '__main__':
    pas = asyncio.run(Pass.find_one({'num_id': '534866'}))
    # company = asyncio.run(Company.find_one({'company_id': ObjectId(pas.company_id)}))
    # generate_document(pas, company)


