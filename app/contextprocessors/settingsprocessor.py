""" 

* Purpose :

* Creation Date : 10-11-2014

* Last Modified : Mo 10 Nov 2014 11:12:36 CET

* Author :  mattis

* Coauthors :   

* Sprintnumber : 1

"""


from django.conf import settings

def error_messages(request):
    return {'ERROR_MESSAGES':settings.ERROR_MESSAGES}
