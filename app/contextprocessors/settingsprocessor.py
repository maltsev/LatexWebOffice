"""

* Purpose :

* Creation Date : 10-11-2014

* Last Modified : Fr 19 Dez 2014 15:24:14 CET

* Author :  mattis

* Coauthors :

* Sprintnumber : 1

"""
from app.common.constants import ERROR_MESSAGES
from app.views.document import available_commands_output, globalparas

def Error_messages(request):
    return {'ERROR_MESSAGES': ERROR_MESSAGES}

def Available_commands(request):
    return {'AVAILABLE_COMMANDS': available_commands_output}

def Global_paras(request):
    return {'GLOBAL_PARAS': globalparas}
