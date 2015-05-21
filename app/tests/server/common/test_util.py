# -*- coding: utf-8 -*-
"""

* Purpose : Test der Hilfsfunktionen (app/common/util.py)

* Creation Date : 21-05-2015

* Author : maltsev

"""
from django.test import TestCase
from app.common import util

class UtilTestClass(TestCase):

    def test_unescapeHTML(self):
        self.assertEqual(util.unescapeHTML('Maria&nbsp;Rebekka&nbsp;Sch&auml;fer'), u'Maria Rebekka Schäfer')