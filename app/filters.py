from rocketgram import make_filter, make_waiter
from rocketgram import context, commonfilters, priority
from rocketgram import UpdateType, MessageType, ChatType
from models import User
import data


@make_filter
async def admin_require():
    admins = await User.find({'is_admin': True}).to_list(None)
    admins_ids = set([admin.id for admin in admins])
    admins_ids = admins_ids | set(data.admins)

    if 'inline_query' in context.update.raw:
        user_id = context.update.raw['inline_query']['from']['id']
        if user_id in admins_ids:
            return True
        else:
            return False

    if context.message.user.id in admins_ids:
        return True
    return False

