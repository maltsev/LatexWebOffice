"""

* Purpose : Test der Allgemeinen Links

* Creation Date : 25-11-2014

* Last Modified : Sat 10 Jan 2015 12:46:36 AM CET

* Author :  mattis

* Coauthors :

* Sprintnumber : 2

* Backlog entry :

"""

from app.tests.server.views.viewtestcase import ViewTestCase


class MainTestClass(ViewTestCase):
    # Initialiserung der benötigten Objekte
    # -> wird vor jedem Test ausgeführt
    def setUp(self):
        self.setUpSingleUser()


    # Freigabe von nicht mehr benötigten Resourcen
    # -> wird nach jedem Test ausgeführt
    def tearDown(self):
        pass


    # Test der Impressum Seite
    def test_impressum(self):
        # Teste ob Impressum unter der URL aufrufbar ist und das richtige Template nutzt
        response = self.client.get('/impressum/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'impressum.html')


    # Test der faq Seite
    def test_faq(self):
        # Teste ob FAQ unter der URL aufrufbar ist und das richtige Template nutzt
        response = self.client.get('/faq/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'faq.html')


    # Test der Editor Seite
    def test_editor(self):
        # Teste ob Editor unter der URL aufrufbar ist und das richtige Template nutzt
        response = self.client.get('/editor/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editor.html')

        # Teste ob Editor zur login Seite weiterleitet, sofern kein Benutzer eingeloggt ist
        # logge user1 aus
        self.client.logout()
        response = self.client.get('/editor/')
        #redirect zur loginseite
        self.assertEqual(response.status_code, 302)
