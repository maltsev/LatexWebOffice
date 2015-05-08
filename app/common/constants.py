# -*- coding: utf-8 -*-
"""

* Purpose : allgemeine Fehlermeldungen und Nachrichten

* Creation Date : 23-11-2014

* Last Modified : Do 05 Mär 2015 13:00:34 CET

* Author :  christian

* Coauthors : mattis, ingo, Kirill

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
    'INACTIVEACCOUNT': '%s ist nicht verifiziert.',
    'WRONGLOGINCREDENTIALS': 'E-Mail-Adresse oder Passwort falsch.',
    'LOGINORREGFAILED': 'Anmeldung nach Registrierung fehlgeschlagen.',
    'INVALIDCHARACTERINFIRSTNAME': 'Vorname enthält ungültiges Zeichen.',
    'NOSPACESINPASSWORDS': 'Passwort darf keine Leerzeichen enthalten.',
    'NOTALLPOSTPARAMETERS': 'Es wurden nicht alle benötigten POST Parameter übermittelt',
    'PROJECTNOTCREATED': 'Fehler beim Erstellen des Projektes',
    'COMMANDNOTFOUND': 'Befehl nicht gefunden',
    'MISSINGPARAMETER': 'Fehlender Parameter: %s',
    'FILENOTCREATED': 'Datei konnte nicht erstellt werden.',
    'EMPTYTEXNOTCREATED': 'main.tex Datei konnte im neuen Projekt nicht erstellt werden.',
    'PROJECTALREADYEXISTS': 'Ein Projekt mit dem Namen %s existiert bereits.',
    'NOTENOUGHRIGHTS': 'Nutzer hat für diese Aktion nicht ausreichend Rechte',
    'FOLDERNAMEEXISTS': 'Dieses Verzeichnis existiert schon',
    'FILENAMEEXISTS': 'Diese Datei existiert schon',
    'DIRECTORYNOTEXIST': 'Dieses Verzeichnis existiert nicht',
    'FILENOTEXIST': 'Diese Datei existiert nicht',
    'FILELOCKED': 'Die Datei ist von anderem Nutzer gesperrt',
    'UNLOCKERROR': 'Die Datei konnte nicht entsperrt werden',
    'DIRLOCKED': 'Das Verzeichnis ist von anderem Nutzer gesperrt',
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
    'NOTEXFILE': 'Keine Tex Datei.',
    'NOPDFFILE': 'Keine PDF Datei.',
    'ILLEGALFILETYPE': 'Dateityp %s ist nicht erlaubt',
    'NOTAZIPFILE' : 'Ungültige zip-Datei',
    'EMPTYZIPFILE' : 'Leere zip-Datei',
    'TEMPLATEALREADYEXISTS': 'Eine Vorlage mit dem Namen %s existiert bereits.',
    'TEMPLATENOTEXIST': 'Vorlage nicht gefunden',
    'UNKNOWNFORMAT': 'Unbekanntes Ausgabeformat',
    'NOLOGFILE': 'Keine Log Datei vorhanden.',
    'USERALREADYINVITED': 'Dieses Projekt ist für den Nutzer %s bereits freigegeben.',
    'USERNOTFOUND': 'Ein Nutzer %s konnte nicht gefunden werden.',
    'COLLABORATIONNOTFOUND': 'Die Kollaboration konnte nicht gefunden werden.',
    'SELFCOLLABORATIONCANCEL': 'Der Nutzer darf nicht der Kollaboration an seinem Projekt kündigen.',
    'EMAILPWRECOVERSEND': 'Eine Email mit Anweisungen um ein neues Passwort zu erhalten wurde an %s versendet',
    'PASSWORDCHANGED': 'Ihr Passwort wurde erfolgreich geändert. Sie können sich nun in das System einloggen',
    'MAXFILESIZE': 'Die maximale Dateigröße von 5MB wurde überschritten',
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

        'application/pdf': PDF,
        'application/postscript': BinaryFile,
        'application/x-dvi': BinaryFile,
        'application/zip': BinaryFile,
        'application/CDFV2-corrupt': BinaryFile
    }
}

MAXFILESIZE = 5000000; #5MB

ZIPMIMETYPE = 'application/zip'
STANDARDENCODING = 'utf-8'

# Ungültige Zeichen für Dateien und Ordner
INVALIDCHARS = '<>;|"\/?*'

# Namensschema für automatische Benennung bei bereits vorhandenen Namen
DUPLICATE_NAMING_REGEX = '%s (%s)'
# Startwert für numerische Suffixe
DUPLICATE_INIT_SUFFIX_NUM = 2

SUCCESS = 'success'
FAILURE = 'failure'

SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2