""" 

* Purpose :

* Creation Date : 06-01-2015

* Last Modified : Di 06 Jan 2015 18:46:58 CET

* Author :  mattis

* Coauthors :   

* Sprintnumber : 4

* Backlog entry : 

"""
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django', 
        'NAME': 'latexweboffice',
        'USER': 'latexweboffice',
        'PASSWORD': '123456',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

ALLOWED_HOSTS=["*"]


