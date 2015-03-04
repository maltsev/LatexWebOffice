""" 

* Purpose :

* Creation Date : 06-01-2015

* Last Modified : Do 26 Feb 2015 10:18:35 CET

* Author :  mattis

* Coauthors :   

* Sprintnumber : 4

* Backlog entry : 

"""
DEBUG = True

'''
DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django', 
        'NAME': 'latexweboffice',
        'USER': 'latexweboffice',
        'PASSWORD': 'ingoistschuld',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}
'''




ALLOWED_HOSTS=["*"]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'latexweboffice@gmail.com'
EMAIL_HOST_PASSWORD = 'W?Nein!LL!'

