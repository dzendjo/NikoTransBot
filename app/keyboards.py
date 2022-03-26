from rocketgram import MessageType, InlineKeyboard
from rocketgram import context, commonfilters, ChatType, SendMessage


def get_admin_ik(T):
    kb = InlineKeyboard()
    kb.callback(T('admin/create_pass_bt'), 'create_pass').row()
    kb.callback(T('admin/edit_pass_bt'), 'edit_pass').row()
    kb.callback(T('admin/create_vehicle_bt'), 'create_vehicle').row()
    kb.callback(T('admin/edit_vehicle_bt'), 'edit_vehicle').row()
    kb.callback(T('admin/new_admin_bt'), 'new_admin').row()
    kb.callback(T('admin/edit_admin_bt'), 'edit_admin').row()
    return kb
