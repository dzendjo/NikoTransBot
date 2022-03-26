import datetime
import os

from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Document, fields
from umongo.frameworks import MotorAsyncIOInstance
import pymongo
from zoneinfo import ZoneInfo


db_host = os.environ.get('DB_HOST', 'localhost')
db = AsyncIOMotorClient(f'mongodb://{db_host}:27017')['NikoTransBot']
instance = MotorAsyncIOInstance(db)


@instance.register
class Company(Document):
    class Meta:
        collection_name = 'companies'
        indexes = ['contact_user_id', 'num_id']

    num_id = fields.IntField(required=True)
    reg_date = fields.DateTimeField(default=datetime.datetime.now(tz=ZoneInfo('Europe/Kiev')))
    contact_user_id = fields.IntField(required=True)
    contact_FIO = fields.StrField(allow_none=True)
    contact_phone = fields.StrField(allow_none=True)
    contact_email = fields.EmailField(allow_none=True)
    name = fields.StrField(allow_none=True)
    code = fields.StrField(allow_none=True)
    extract_file_id = fields.StrField(allow_none=True)
    extract_url = fields.UrlField(allow_none=True)

    is_validated = fields.BooleanField(default=False)
    is_on_check = fields.BooleanField(default=False)

    manager_user_id = fields.IntField()
    manager_username = fields.StrField()
    application_create_date = fields.DateTimeField(allow_none=True)
    application_add_manager_date = fields.DateTimeField(allow_none=True)
    application_complete_date = fields.DateTimeField(allow_none=True)
    rejection_text = fields.StrField()

    message_id = fields.IntField()

    async def pre_insert(self):
        last_item = await self.find_one({}, {'num_id': 1},
                                        sort=[("num_id", pymongo.DESCENDING)])
        self.num_id = last_item.num_id + 1 if last_item else 1


@instance.register
class Pass(Document):
    class Meta:
        collection_name = 'passes'
        indexes = ['vehicle_number', 'num_id']

    num_id = fields.StrField(allow_none=True)
    create_user_id = fields.IntField(required=True)

    start_date = fields.DateTimeField(allow_none=True)
    end_date = fields.DateTimeField(allow_none=True)

    vehicle_number = fields.StrField(allow_none=True)
    trailer_number = fields.StrField(allow_none=True)

    start_place = fields.StrField(allow_none=True)
    end_place = fields.StrField(allow_none=True)

    goods = fields.StrField(allow_none=True)

    driver_FIO = fields.StrField(allow_none=True)
    driver_phone = fields.StrField(allow_none=True)
    company_id = fields.StrField(allow_none=True)

    send_date = fields.DateTimeField(allow_none=True)
    add_manager_date = fields.DateTimeField(allow_none=True)
    complete_date = fields.DateTimeField(allow_none=True)

    is_on_check = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=False)
    is_validated = fields.BooleanField(default=False)

    rejection_text = fields.StrField()

    message_id = fields.IntField(allow_none=True)
    manager_user_id = fields.IntField(allow_none=True)
    manager_username = fields.StrField(allow_none=True)

    pdf_file_id = fields.StrField()
    qr_file_id = fields.StrField()


@instance.register
class Advert(Document):
    class Meta:
        collection_name = 'adverts'
        indexes = []

    date = fields.DateTimeField(default=datetime.datetime.now())
    name = fields.StrField(required=True, unique=True)
    type = fields.StrField(allow_none=True)
    done_users = fields.ListField(fields.IntField, default=[])
    admin_user_id = fields.IntField(required=True)


@instance.register
class User(Document):
    class Meta:
        collection_name = 'botusers'
        indexes = ['is_active']

    id = fields.IntField(attribute='_id')
    process_flag = fields.BooleanField(default=False)
    created = fields.DateTimeField(required=True)
    visited = fields.DateTimeField(required=True)
    username = fields.StrField(required=True, allow_none=True)
    first_name = fields.StrField(required=True)
    last_name = fields.StrField(required=True, allow_none=True)
    language_code = fields.StrField(required=True, allow_none=True)
    language = fields.StrField(required=True)
    is_active = fields.BooleanField(default=True)

    is_registered = fields.BooleanField(default=False)
    FIO = fields.StrField()
    phone = fields.StrField()
    vehicles = fields.ListField(fields.DictField, default=[])

    is_admin = fields.BooleanField(default=False)


@instance.register
class QRCode(Document):
    class Meta:
        collection_name = 'qrcodes'
        indexes = []

    date = fields.DateTimeField(default=datetime.datetime.now())
    data = fields.StrField(required=True)
    user_id = fields.IntField(allow_none=True)
    qr_with_caption_id = fields.StrField(allow_none=True)
    qr_without_caption_id = fields.StrField(allow_none=True)
    is_active_with_sign = fields.BooleanField(default=True)


async def create_indexes():
    await User.ensure_indexes()
    await Advert.ensure_indexes()
    await Pass.ensure_indexes()
    await QRCode.ensure_indexes()


if __name__ == '__main__':
    pass
