# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Hilfsfunktionen

* Creation Date : 16-12-2014

* Last Modified : Di 16 Dez 2014 13:00:02 CET

* Author :  christian

* Coauthors :

* Sprintnumber : -

* Backlog entry : -

"""

import time
import os


def measure_time(function):
    """Decorator, um die Dauer einer Funktion in der Konsole auszugeben.

    :param function: eine beliebige Funktion
    :return: function mit Ausgabe der Dauer
    """

    def wrapper(*args, **kwargs):
        """Wrapper zur Zeitmessung einer Funktion

        :param args: arguments
        :param kwargs: keyword arguments
        :return: Dauer der Ausführung einer Funktion
        """

        # startzeit
        t1 = time.time()
        # führe die übergebene Funktion aus
        function(*args, **kwargs)
        # endzeit
        t2 = time.time()
        # Dauer
        duration = t2-t1

        print('{0}: {1}'.format(function.__name__, str(duration) + os.linesep))

        return duration

    return wrapper
