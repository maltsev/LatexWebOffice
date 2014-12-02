"""

* Purpose : Test des Kompilierers (app/compile/compile.py)

* Creation Date : 28-11-2014

* Last Modified : Do 28 Nov 2014 20:45:41 CET

* Author : ingo

* Coauthors :

* Sprintnumber : 2

* Backlog entry : 

"""

import os
from app.common import compile
from django.test import TestCase
from core.settings import BASE_DIR

class CompilerTestClass(TestCase):
    
    # testet, ob latexmk.pl existiert
    def test_exists(self):
        os.chdir(BASE_DIR)
        self.assertTrue(os.path.exists(compile.latexmk_path()))
        
    # testet, ob latexmk.pl ausführbar ist
    def test_executeable(self):
        os.chdir(BASE_DIR)
        path = compile.latexmk_path()
        self.assertTrue(os.path.isfile(path) and os.access(path,os.X_OK))