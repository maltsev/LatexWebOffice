# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Fehlermeldungen und Nachrichten

* Creation Date : 23-11-2014

* Last Modified : Mo 24 Nov 2014 12:23:23 CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : -

* Backlog entry : -

"""

# error messages
ERROR_MESSAGES = {
    'EMAILALREADYEXISTS': 'E-Mail-Adresse ist bereits registriert.',
    'INVALIDEMAIL': 'Ungültige E-Mail-Adresse',
    'NOEMPTYFIELDS': 'Keine leeren Eingaben erlaubt.',
    'PASSWORDSDONTMATCH': 'Passwörter stimmen nicht überein.',
    'INACTIVEACCOUNT': '{0} ist nicht verifiziert.',
    'WRONGLOGINCREDENTIALS': 'E-Mail-Adresse oder Passwort falsch.',
    'LOGINORREGFAILED': 'Anmeldung nach Registrierung fehlgeschlagen.',
    'INVALIDCHARACTERINFIRSTNAME': 'Vorname enthält ungültiges Zeichen.',
    'NOSPACESINPASSWORDS': 'Passwort darf keine Leerzeichen enthalten.',
    'NOTALLPOSTPARAMETERS': 'You suck',
    'PROJECTNOTCREATED': 'Fehler beim Erstellen des Projektes',
    'COMMANDNOTFOUND': 'Befehl nicht gefunden',
    'MISSINGPARAMETER': 'Fehlender Parameter: {0}',
    'PROJECTNAMEONLYWHITESPACE': 'Projektname darf nicht nur aus Leerzeichen bestehen.',
    'EMPTYTEXNOTCREATED': 'main.tex Datei konnte im neuen Projekt nicht erstellt werden.',
    'PROJECTALREADYEXISTS': 'Ein Projekt mit dem Namen \"{0}\" existiert bereits.',
}

SUCCESS = 'success'
FAILURE = 'failure'
