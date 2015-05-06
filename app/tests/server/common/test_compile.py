# -*- coding: utf-8 -*-
"""

* Purpose : Test des Kompilierers (app/compile/compile.py)

* Creation Date : 28-11-2014

* Last Modified : Do 26 Feb 2015 17:39:38 CET

* Author : ingo

* Coauthors :

* Sprintnumber : 2

* Backlog entry : -

"""

import os
import shutil

from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from app.common import compile
from app.models.file.pdf import PDF
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.texfile import TexFile

from app.models.project import Project
from settings import BASE_DIR


class CompilerTestClass(TestCase):
    def setUp(self):
        """Setup Methode für die einzelnen Tests

         Diese Funktion wird vor jeder Testfunktion ausgeführt.
         Damit werden die notwendigen Variablen und Modelle für jeden Test neu initialisiert.
         Die Methoden hierzu befinden sich im ViewTestCase (viewtestcase.py).

        :return: None
        """

        # erstellt einen neuen Benutzer
        self.user = User.objects.create_user('user@test.de', password='123456')

        # loggt den erzeugten Benutzer ein
        self.client.login(username=self.user.username, password='123456')

        # ----------------------------------------------------------------------------------------------------
        # VERZEICHNISSE
        # ----------------------------------------------------------------------------------------------------

        # erstellt ein neues Projekt für den erzeugten Benutzer
        self.project = Project.objects.createWithMainTex(name='project', author=self.user)

        self.root = self.project.rootFolder

        # erzeugt ein Unterverzeichnis im root-Verzeichnis des Projektes
        self.subfolder_path = os.path.join(self.root.getTempPath(), 'subfolder')
        if not os.path.isdir(self.subfolder_path):
            os.makedirs(self.subfolder_path)

    def tearDown(self):
        """Freigabe von nicht mehr notwendigen Ressourcen.

        Diese Funktion wird nach jeder Testfunktion ausgeführt.

        :return: None
        """

        # self.tearDownFiles()
        pass

    def test_compile_tex(self):
        """Testet das (mehrfache) Kompilieren einer tex-Datei ohne Referenzen.

        :return: None
        """

        # ----------------------------------------------------------------------------------------------------
        # KOMPILIEREN EINER GÜLTIGEN TEX-DATEI
        # ----------------------------------------------------------------------------------------------------

        # erzeugt eine gültige tex-Datei im root-Verzeichnis des Projektes
        self.file_tex = TexFile(name="test.tex", folder=self.root)
        self.file_tex.source_code = '\\documentclass{article} \\begin{document} \\LaTeX{} \\end{document}'
        self.file_tex.save()

        # kompiliert die gültige tex-Datei
        errors, pdf = compile.latexcompile(self.file_tex.id, formatid=0, forcecompile=1)

        # es sollten keine Fehlermeldungen aufgetreten und eine pdf-Datei erzeugt worden sein
        self.assertTrue(errors == None)
        self.assertTrue(pdf != None)

        # in der Datenbank sollte nun eine entsprechende pdf-Datei vorliegen
        pdf_src = PDF.objects.filter(name=pdf['name'], folder=self.file_tex.folder)
        self.assertTrue(pdf_src != None and len(pdf_src) == 1)

        # ----------------------------------------------------------------------------------------------------
        # ERNEUTES KOMPILIEREN DERSELBEN TEX-DATEI
        # ----------------------------------------------------------------------------------------------------

        # kompiliert dieselbe tex-Datei ein weiteres Mal
        errors, pdf = compile.latexcompile(self.file_tex.id, formatid=0, forcecompile=1)

        # es sollten erneut keine Fehlermeldungen aufgetreten und eine pdf-Datei erzeugt worden sein
        self.assertTrue(errors == None)
        self.assertTrue(pdf != None)

        # in der Datenbank sollte nun (genau) eine entsprechende pdf-Datei vorliegen
        pdf_src = PDF.objects.filter(name=pdf['name'], folder=self.file_tex.folder)
        self.assertTrue(pdf_src != None and len(pdf_src) == 1)


        # ----------------------------------------------------------------------------------------------------
        #                                   KOMPILIEREN DER LEEREN TEX-DATEI                                  
        # ----------------------------------------------------------------------------------------------------

        # leert die tex-Datei
        self.file_tex.source_code = ''
        self.file_tex.save()
        pdf_src[0].delete()

        # kompiliert die leere tex-Datei
        errors, pdf = compile.latexcompile(self.file_tex.id, formatid=0, forcecompile=1)

        # das Kompilieren einer leeren tex-Datei sollte zu einem SYNTAXERROR führen, wobei keine pdf erzeugt wird
        self.assertTrue(
            errors != None)  # and len(errors)==1 and errors[0].startswith(ERROR_MESSAGES['COMPILATIONERROR_SYNTAXERROR']))
        #self.assertTrue(pdf == None)

        # in der Datenbank sollte nun keine entsprechende pdf-Datei vorliegen
        pdf_src = PDF.objects.filter(name=self.file_tex.name[:3] + 'pdf', folder=self.file_tex.folder)
        self.assertTrue(pdf_src != None or len(pdf_src) == 0)

    def test_compile_img_tex(self):
        """Testet das Kompilieren einer tex-Datei, welche auf eine bestehende Bild-Datei referenziert.

        :return: None
        """

        # ----------------------------------------------------------------------------------------------------
        # GÜLTIGE BILD-REFERENZIERUNG
        # ----------------------------------------------------------------------------------------------------

        # erzeugt eine Bild-Datei im root-Verzeichnis des Projektes
        # (verwendet logo.png als echte Bild-Datei, da leere Bild-Dateien nicht kompilierbar sind)
        image_name = "image.png"
        shutil.copyfile(os.path.join(BASE_DIR, "app", "static", "img", "logo.png"),
                        os.path.join(self.subfolder_path, image_name))

        # erzeugt eine tex-Datei, welche eine Bild-Datei gültig referenziert
        # (verwendet app/static/img/logo.png als echte Bild-Datei, da leere Bild-Dateien nicht kompilierbar sind)
        self.file_tex_img = TexFile(name="img.tex", folder=self.root)
        self.file_tex_img.source_code = '\\documentclass{article} \\usepackage{graphicx} \\begin{document} \\includegraphics{subfolder/image} \\end{document}'
        self.file_tex_img.save()

        # kompiliert die, die Bild-Datei referenzierende, tex-Datei
        errors, pdf = compile.latexcompile(self.file_tex_img.id, formatid=0, forcecompile=1)

        # es sollten keine Fehlermeldungen auftreten und eine pdf-Datei erzeugt worden sein
        self.assertTrue(errors == None)
        self.assertTrue(pdf != None)

        # ----------------------------------------------------------------------------------------------------
        # UNGÜLTIGE BILD-REFERENZIERUNG
        # ----------------------------------------------------------------------------------------------------

        # ändert die Bild-Referenzierung auf eine nicht-existierende Bild-Datei
        self.file_tex_img.source_code = '\\documentclass{article} \\usepackage{graphicx} \\begin{document} \\includegraphics{nosuchfile.jpg} \\end{document}'
        self.file_tex_img.save()

        # kompiliert die tex-Datei erneut
        # (die Bild-Datei wurde nach obigem Kompilierprozess entfernt)
        errors, pdf = compile.latexcompile(self.file_tex_img.id, formatid=0, forcecompile=1)

        # das Kompilieren einer tex-Datei mit ungültiger Bild-Referenz sollte zu einem FILENOTFOUND führen, wobei dennoch eine pdf-Datei erzeugt wird
        self.assertTrue(errors != None)  # and errors[1].startswith(ERROR_MESSAGES['COMPILATIONERROR_FILENOTFOUND']))
        self.assertTrue(pdf != None)

    def test_compile_bibtex_tex(self):
        """Testet das Kompilieren einer tex-Datei, welche auf eine bibtex-Datei referenziert,
        deren Referenzen vollständig sind.

        :return: None
        """

        # ----------------------------------------------------------------------------------------------------
        # GÜLTIGE BIBTEX-REFERENZIERUNG
        # ----------------------------------------------------------------------------------------------------

        # erzeugt eine bibtex-Datei im root-Verzeichnis des Projektes
        self.file_bib = PlainTextFile(name="bibtex.bib", folder=self.root)
        self.file_bib.source_code = "@article{a1, author=\"Author\", title=\"Titel\", journal=\"Magazin\", volume=\"1\", issue=\"1\", pages=\"42\", year=2014 }"
        self.file_bib.save()

        # erzeugt eine tex-Datei, welche die bibtex-Datei referenziert
        self.file_tex_bibtex = TexFile(name="bib.tex", folder=self.root)
        self.file_tex_bibtex.source_code = '\\documentclass{article} \\begin{document} \\bibliographystyle{plain} Test~\\cite{a1} \\bibliography{bibtex} \\end{document}'
        self.file_tex_bibtex.save()

        # kompiliert die tex-Datei
        errors, pdf = compile.latexcompile(self.file_tex_bibtex.id, formatid=0, forcecompile=1)

        # es sollten keine Fehlermeldungen aufgetreten und eine pdf-Datei erzeugt worden sein
        self.assertTrue(errors == None)
        self.assertTrue(pdf != None)

        # ----------------------------------------------------------------------------------------------------
        # UNGÜLTIGE BIBTEX-REFERENZIERUNG
        # ----------------------------------------------------------------------------------------------------

        # ändert die Referenzierung auf eine nicht-bestehende Referenz ~\cite{a2}
        self.file_tex_bibtex.source_code = '\\documentclass{article} \\begin{document} \\bibliographystyle{plain} Test~\\cite{xyz} \\bibliography{bibtex} \\end{document}'
        self.file_tex_bibtex.save()

        # kompiliert die tex-Datei
        errors, pdf = compile.latexcompile(self.file_tex_bibtex.id, formatid=0, forcecompile=1)

        # das Kompilieren einer tex-Datei mit ungültiger bibtex-Referenz sollte zu einem CITATIONUNDEFINED führen, wobei dennoch eine pdf-Datei erzeugt wird
        # TODO
        #self.assertTrue(errors!=None)
        self.assertTrue(pdf != None)

    def test_compile_deep_tex(self):
        """Testet das Kompilieren einer tex-Datei mit Referenz auf eine Datei, welche in der Verzeichnishierarchie
        unterhalb des angegebenen relativen Pfades liegt.

        :return:
        """

        # ----------------------------------------------------------------------------------------------------
        # GÜLTIGE BILD-REFERENZIERUNG
        # ----------------------------------------------------------------------------------------------------

        # erzeugt eine Bild-Datei im subfolder-Verzeichnis
        image_name = "image.png"
        shutil.copyfile(os.path.join(BASE_DIR, "app", "static", "img", "logo.png"),
                        os.path.join(self.subfolder_path, image_name))

        # erzeugt eine tex-Datei, welche die Bild-Datei lediglich über ihren Namen (nicht aber über den relativen Pfad) referenziert
        self.file_tex_dp = TexFile(name="deep.tex", folder=self.root)
        self.file_tex_dp.source_code = '\\documentclass{article} \\usepackage{graphicx} \\begin{document} \\includegraphics{image} \\end{document}'
        self.file_tex_dp.save()

        # kompiliert die referenzierende tex-Datei
        errors, pdf = compile.latexcompile(self.file_tex_dp.id, formatid=0, forcecompile=1)

        # es sollte eine Fehlermeldung aufgetreten und keine pdf-Datei erzeugt worden sein
        self.assertTrue(errors != None)
        self.assertTrue(pdf == None)
