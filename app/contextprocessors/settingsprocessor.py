""" 

* Purpose :

* Creation Date : 10-11-2014

* Last Modified : Mo 10 Nov 2014 12:22:41 CET

* Author :  mattis

* Coauthors :   

* Sprintnumber : 1

"""
import json

from app.common.constants import ERROR_MESSAGES
from app.views.document import available_commands, globalparas


def Error_messages(request):
    return {'ERROR_MESSAGES': json.dumps(ERROR_MESSAGES)}


def Available_commands(request):
    return {'AVAILABLE_COMMANDS': json.dumps(available_commands)}


def Global_paras(request):
    return {'GLOBAL_PARAS': json.dumps(globalparas)}