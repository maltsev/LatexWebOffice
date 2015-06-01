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

# Fehlermeldungen, welche von den verschiedenen Methoden zur Rückgabe genutzt werden
ERROR_MESSAGES = {
    'EMAILALREADYEXISTS': u'E-Mail-Adresse ist bereits registriert.',
    'INVALIDEMAIL': u'Ungültige E-Mail-Adresse',
    'NOEMPTYFIELDS': u'Keine leeren Eingaben erlaubt.',
    'PASSWORDSDONTMATCH': u'Passwörter stimmen nicht überein.',
    'INACTIVEACCOUNT': u'%s ist nicht verifiziert.',
    'WRONGLOGINCREDENTIALS': u'E-Mail-Adresse oder Passwort falsch.',
    'LOGINORREGFAILED': u'Anmeldung nach Registrierung fehlgeschlagen.',
    'INVALIDCHARACTERINFIRSTNAME': u'Vorname enthält ungültiges Zeichen.',
    'NOSPACESINPASSWORDS': u'Passwort darf keine Leerzeichen enthalten.',
    'NOTALLPOSTPARAMETERS': u'Es wurden nicht alle benötigten POST Parameter übermittelt',
    'PROJECTNOTCREATED': u'Fehler beim Erstellen des Projektes',
    'COMMANDNOTFOUND': u'Befehl nicht gefunden',
    'MISSINGPARAMETER': u'Fehlender Parameter: %s',
    'FILENOTCREATED': u'Datei konnte nicht erstellt werden.',
    'EMPTYTEXNOTCREATED': u'main.tex Datei konnte im neuen Projekt nicht erstellt werden.',
    'PROJECTALREADYEXISTS': u'Ein Projekt mit dem Namen %s existiert bereits.',
    'NOTENOUGHRIGHTS': u'Nutzer hat für diese Aktion nicht ausreichend Rechte',
    'FOLDERNAMEEXISTS': u'Dieses Verzeichnis existiert schon',
    'FILENAMEEXISTS': u'Diese Datei existiert schon',
    'DIRECTORYNOTEXIST': u'Dieses Verzeichnis existiert nicht',
    'FILENOTEXIST': u'Diese Datei existiert nicht',
    'FILELOCKED': u'Die Datei ist von anderem Nutzer gesperrt',
    'UNLOCKERROR': u'Die Datei konnte nicht entsperrt werden',
    'DIRLOCKED': u'Das Verzeichnis ist von anderem Nutzer gesperrt',
    'UNKOWNERROR': u'Unbekannter Fehler',
    'BLANKNAME': u'Leere Namen sind nicht erlaubt',
    'DATABASEERROR': u'Datenbankfehler',
    'COMPILATIONERROR': u'Fehler beim Kompilieren',
    'COMPILATIONERROR_CITATIONUNDEFINED': u'Zitierung undefiniert',
    'COMPILATIONERROR_FILENOTFOUND': u'Datei nicht gefunden',
    'COMPILATIONERROR_SYNTAXERROR': u'Syntax-Fehler',
    'PROJECTNOTEXIST': u'Projekt nicht gefunden',
    'INVALIDNAME': u'Unerlaubtes Zeichen verwendet',
    'NOPLAINTEXTFILE': u'Datei kann nicht bearbeitet werden, keine Text Datei.',
    'NOTEXFILE': u'Keine Tex Datei.',
    'NOPDFFILE': u'Keine PDF Datei.',
    'ILLEGALFILETYPE': u'Dateityp %s ist nicht erlaubt',
    'NOTAZIPFILE' : 'Ungültige zip-Datei',
    'EMPTYZIPFILE' : 'Leere zip-Datei',
    'TEMPLATEALREADYEXISTS': u'Eine Vorlage mit dem Namen %s existiert bereits.',
    'TEMPLATENOTEXIST': u'Vorlage nicht gefunden',
    'UNKNOWNFORMAT': u'Unbekanntes Ausgabeformat',
    'NOLOGFILE': u'Keine Log Datei vorhanden.',
    'USERALREADYINVITED': u'Dieses Projekt ist für den Nutzer %s bereits freigegeben.',
    'USERNOTFOUND': u'Ein Nutzer %s konnte nicht gefunden werden.',
    'COLLABORATIONNOTFOUND': u'Die Kollaboration konnte nicht gefunden werden.',
    'SELFCOLLABORATIONCANCEL': u'Der Nutzer darf nicht der Kollaboration an seinem Projekt kündigen.',
    'EMAILPWRECOVERSEND': u'Eine Email mit Anweisungen um ein neues Passwort zu erhalten wurde an %s versendet',
    'PASSWORDCHANGED': u'Ihr Passwort wurde erfolgreich geändert. Sie können sich nun in das System einloggen',
    'MAXFILESIZE': u'Die maximale Dateigröße von 5MB wurde überschritten',
}

MAXFILESIZE = 5000000 #5MB

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
