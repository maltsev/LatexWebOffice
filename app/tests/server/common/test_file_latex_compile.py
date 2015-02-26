"""

* Purpose : Test des LatexCompile Methode des File Views (app/views/file.py)

* Creation Date : 26-11-2014

* Last Modified : Sa 13 Dez 2014 14:50:08 CET

* Author :  christian

* Coauthors : mattis, ingo

* Sprintnumber : 2

* Backlog entry : -

"""

from app.common.constants import ERROR_MESSAGES
from app.common import util
from app.models.file.texfile import TexFile
from app.models.file.pdf import PDF
from app.models.project import Project
from app.tests.server.views.viewtestcase import ViewTestCase


class FileLatexCompileTestClass(ViewTestCase):
    def setUp(self):
        """Setup Methode für die einzelnen Tests

         Diese Funktion wird vor jeder Testfunktion ausgeführt.
         Damit werden die notwendigen Variablen und Modelle für jeden Test neu initialisiert.
         Die Methoden hierzu befinden sich im ViewTestCase (viewtestcase.py).

        :return: None
        """

        self.setUpUserAndProjects()
        self.setUpFolders()
        self.setUpFiles()
        self.setUpValues()
        self.setUpCollaborations()

    def tearDown(self):
        """Freigabe von nicht mehr notwendigen Ressourcen.

        Diese Funktion wird nach jeder Testfunktion ausgeführt.

        :return: None
        """

        # self.tearDownFiles()
        pass

    def test_latexCompile(self):
        """Test der latexCompile() Methode des file view

        Teste das Kompilieren einer einfachen .tex Datei,
        (Hier soll nur der generelle Aufruf der latexCompile() Funktion getestet werden,
        weitere Tests für die eigentliche compile Funktion befinden sich in test_compile.py)

        Testfälle:
        - user1 kompiliert eine simple .tex Datei -> Erfolg
        - user1 kompiliert eine fehlerhafte .tex Datei -> Fehler
        - user1 kompiliert eine Datei die nicht vorhanden ist -> Fehler
        - user1 kompiliert eine Datei welche user2 gehört -> Fehler

        :return: None
        """

        # erstelle ein Projekt mit 2 .tex Dateien, wobei texobj2 keine gültige .tex Datei ist
        projectobj = Project.objects.create(name=self._newname1, author=self._user1)
        src_code = "\\documentclass[a4paper,10pt]{article} \\usepackage[utf8]{inputenc} \\title{test} " \
                   "\\begin{document} \\maketitle \\begin{abstract} \\end{abstract} \\section{} \\end{document}"
        texobj1 = TexFile.objects.create(name=self._newtex_name1, folder=projectobj.rootFolder, source_code=src_code)
        texobj2 = TexFile.objects.create(name=self._newtex_name2, folder=projectobj.rootFolder, source_code='Test')

        # Sende Anfrage zum Kompilieren der .tex Datei
        response = util.documentPoster(self, command='compile', idpara=texobj1.id, idpara3=0)

        # der Name sollte dem der .tex Datei entsprechen, jedoch mit der Endung .pdf
        pdf_name = texobj1.name[:-3] + 'pdf'
        # hole das PDF Objekt
        pdfobj = PDF.objects.filter(name=pdf_name, folder=texobj1.folder)

        # Das PDF Objekt zu der .tex Datei sollte in der Datenbank vorhanden sein
        self.assertTrue(pdfobj.count() == 1)

        # erwartete Antwort des Servers
        serveranswer = {
            'id': pdfobj[0].id,
            'name': pdf_name
        }

        # überprüfe die Antwort des Servers
        # sollte success als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonSuccessResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Kompilieren einer fehlerhaften .tex Datei
        response = util.documentPoster(self, command='compile', idpara=texobj2.id, idpara3=0)

        # erwartete Antwort des Servers
        serveranswer = {'error': '["Syntax-Fehler: Es konnte kein g\\u00fcltiges \\\\end gefunden werden."]'}

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Kompilieren einer Datei die nicht vorhanden ist
        response = util.documentPoster(self, command='compile', idpara=self._invalidid, idpara3=0)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['FILENOTEXIST']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)

        # --------------------------------------------------------------------------------------------------------------
        # Sende Anfrage zum Kompilieren einer Datei die user2 gehört (als user1)
        response = util.documentPoster(self, command='compile', idpara=self._user2_tex1.id, idpara3=0)

        # erwartete Antwort des Servers
        serveranswer = ERROR_MESSAGES['NOTENOUGHRIGHTS']

        # überprüfe die Antwort des Servers
        # sollte failure als status liefern
        # die Antwort des Servers sollte mit serveranswer übereinstimmen
        util.validateJsonFailureResponse(self, response.content, serveranswer)



        src_code = "\\documentclass[a4paper,10pt]{article} \\usepackage[utf8]{inputenc} \\title{test} " \
                   "\\begin{document} \\maketitle \\begin{abstract} \\end{abstract} \\section{} \\end{document}"
        texobj = TexFile.objects.create(name=self._newtex_name1, folder=self._user2_sharedproject.rootFolder, source_code=src_code)

        response = util.documentPoster(self, command='compile', idpara=texobj.id, idpara3=0)

        pdf_name = texobj.name[:-3] + 'pdf'
        pdfobj = PDF.objects.filter(name=pdf_name, folder=texobj.folder)

        self.assertTrue(pdfobj.count() == 1)
        util.validateJsonSuccessResponse(self, response.content, {'id': pdfobj[0].id, 'name': pdf_name})