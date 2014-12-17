# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Fehlermeldungen und Nachrichten

* Creation Date : 23-11-2014

* Last Modified : Tue 16 Dec 2014 05:11:47 PM CET

* Author :  christian

* Coauthors : mattis

* Sprintnumber : -

* Backlog entry : -

"""
from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from app.models.file.pdf import PDF
from app.models.file.image import Image

# Fehlermeldungen, welche von den verschiedenen Methoden zur Rückgabe genutzt werden
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
    'NOTALLPOSTPARAMETERS': 'Es wurden nicht alle benötigten POST Parameter übermittelt',
    'PROJECTNOTCREATED': 'Fehler beim Erstellen des Projektes',
    'COMMANDNOTFOUND': 'Befehl nicht gefunden',
    'MISSINGPARAMETER': 'Fehlender Parameter: {0}',
    'FILENOTCREATED': 'Datei konnte nicht erstellt werden.',
    'EMPTYTEXNOTCREATED': 'main.tex Datei konnte im neuen Projekt nicht erstellt werden.',
    'PROJECTALREADYEXISTS': 'Ein Projekt mit dem Namen \"{0}\" existiert bereits.',
    'NOTENOUGHRIGHTS': 'Nutzer hat für diese Aktion nicht ausreichend Rechte',
    'FOLDERNAMEEXISTS': 'Dieses Verzeichnis existiert schon',
    'FILENAMEEXISTS': 'Diese Datei existiert schon',
    'DIRECTORYNOTEXIST': 'Dieses Verzeichnis existiert nicht',
    'FILENOTEXIST': 'Diese Datei existiert nicht',
    'UNKOWNERROR': 'Unbekannter Fehler',
    'BLANKNAME': 'Leere Namen sind nicht erlaubt',
    'DATABASEERROR': 'Datenbankfehler',
    'COMPILATIONERROR': 'Fehler beim Kompilieren',
    'COMPILATIONERROR_CITATIONUNDEFINED': 'Zitierung undefiniert',
    'COMPILATIONERROR_FILENOTFOUND': 'Datei nicht gefunden',
    'COMPILATIONERROR_SYNTAXERROR': 'Syntax-Fehler',
    'PROJECTNOTEXIST': 'Projekt nicht gefunden',
    'INVALIDNAME': 'Unerlaubtes Zeichen verwendet',
    'NOPLAINTEXTFILE': 'Datei kann nicht bearbeitet werden, keine Text Datei.',
    'ILLEGALFILETYPE': 'Dateityp ist nicht erlaubt',
    'TEMPLATEALREADYEXISTS': 'Eine Vorlage mit dem Namen \"{0}\" existiert bereits.',
    'TEMPLATENOTEXIST': 'Vorlage nicht gefunden',
}

ALLOWEDMIMETYPES = {
    'plaintext': {
        'text/x-tex': TexFile,                      # Linux
        'application/x-tex': TexFile,               # Windows
        'text/plain': PlainTextFile,

        'text/x-c': PlainTextFile,                  # C Source File
        'text/html': PlainTextFile,                 # HTML
        'text/x-java-source,java': PlainTextFile    # Java Source File
    },
    'binary': {
        'image/png': Image,
        'image/jpg': Image,
        'image/jpeg': Image,
        'image/gif': Image,
        'application/tga': Image,

        'application/pdf': PDF
    }
}


# Ungültige Zeichen für Dateien und Ordner
INVALIDCHARS = '<>;|"\/?*'

SUCCESS = 'success'
FAILURE = 'failure'
