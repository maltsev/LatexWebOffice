# -*- coding: utf-8 -*-
"""

* Purpose : Kompilierer

* Creation Date : 27-11-2014

* Last Modified : Mo 15 Dez 2014 13:32:09 CET

* Author : ingo

* Coauthors : christian

* Sprintnumber : 2, 4

* Backlog entry : TEK1

"""
import os
import shutil
import subprocess
import tempfile

from app.common.constants import ERROR_MESSAGES, ZIPMIMETYPE
from app.models.file.pdf import PDF
from app.models.file.texfile import TexFile
from app.models.file.binaryfile import BinaryFile
from app.models.file.plaintextfile import PlainTextFile
from app.common import util
from core.settings import BASE_DIR


def latexcompile(texid, formatid=0, compilerid=0, forcecompile=0, debug=False):
    """Kompiliert eine tex Datei mit der übergebenen texid in das entsprechende Ausgabeformat (formatid).

    formatid:   0 - PDF
                1 - HTML mit htlatex (Rückgabe als zip Datei)
                2 - DVI
                3 - PS

    Zum Kompilieren wird das Perl-Script latexmk.pl verwendet (nutzt texlive), bzw. für HTML wird htlatex genutzt.

    Latexmk:
    http://users.phys.psu.edu/~collins/software/latexmk-jcc/

    :param texid: Id der tex Datei
    :param formatid: Id des Ausgabeformates
    :param forcecompile; Wert 1 führt die Kompilierung immer durch, auch wenn die tex Datei älter als die PDF Datei ist
    :return: Tupel aus folgenden Komponenten:
        1. Liste der Fehlermeldungen, welche beim Kompilieren geworfen wurden oder None, falls keine Fehler auftraten
-        2. Array der ID und des Namens der erzeugten pdf-Datei oder None, sofern keine pdf-Datei erzeugt werden konnte
    """

    formatid = str(formatid)
    compilerid = str(compilerid)
    forcecompile = str(forcecompile)

    # tex-File der übergebenen ID
    texobj = TexFile.objects.get(id=texid)

    # wenn die tex datei zuvor ohne Fehler kompiliert wurde, forcecompile nicht gesetzt ist und das Format PDF ist
    if texobj.lastcompilestatus == 0 and forcecompile != '1' and formatid == '0':
        # liefere die id und den Namen der PDF Datei, falls vorhanden
        pdfobj = PDF.objects.filter(name=texobj.name[:-3] + 'pdf', folder=texobj.folder)

        if pdfobj.exists():
            return None, {'id': pdfobj[0].id, 'name': pdfobj[0].name}

    # Pfad des root-Verzeichnisses
    # es werden alle Dateien und Ordner des Projektes in einen temporären Ordner kopiert
    root_path = texobj.folder.getRoot().dumpFolder()

    # temp Ordner für die bei der Kompilierung erstellten Dateien
    out_dir_path = tempfile.mkdtemp(dir=texobj.folder.getTempPath())


    # returncode der Ausführung von latexmk/htlatex
    rc = 0

    file_data = {}
    errors = None

    # Parameter für die Kompilierung
    # '-f' führt die Kompilieren auch unter auftretenden Fehlern so möglich durch
    # '-interaction=nonstopmode' unterbindet die Unterbrechung des Kompiliervorgangs für eine
    # manuelle Eingabeaufforderung (falls eines der ausführenden Programm einen Fehler festgestellt hat)
    # '-outdir=FOO' Verzeichnis für die Ausgabe-Dateien
    # '-bibtex' bbl-Dateien werden über bibtex erzeugt, sofern notwendig
    # '-pdf' pdf-Datei wird über pdflatex aus der angegebenen tex-Datei erzeugt

    # mögliche Formate der Kompilierung
    latexmk_formatargs = {
        '0': '-pdf',
        '2': '-dvi',
        '3': '-ps'
    }

    # mögliche Latex Compiler
    compilerargs = {
        '0': 'pdflatex --shell-escape %O %S',
        '1': 'lualatex --shell-escape %O %S',
        '2': 'xelatex --shell-escape %O %S'
    }

    args = {
        'texobj': texobj,
        'texpath': texobj.getTempPath(),
        'format': '',
        'outdirpath': out_dir_path,
        'compilerargs': compilerargs[compilerid],
        'cwd': texobj.folder.getTempPath(),
        'force': '-f'
    }

    try:
        # wenn die tex Datei mit latexmk kompiliert werden soll
        if formatid in latexmk_formatargs:
            args['format'] = latexmk_formatargs[formatid]
            rc, file_data = latexmk(args, console_output=debug)
        # HTML Format mit htlatex
        elif formatid == '1':
            args['outdirpath'] = out_dir_path + os.sep
            rc, file_data = htlatex(args, console_output=debug)
        # Ungültige formatid
        else:
            errors = ERROR_MESSAGES['UNKNOWNFORMAT']

        # wenn beim Kompilier-Prozess ein Fehler aufgetreten ist ...
        if rc != 0:
            # Fehlermeldungen
            errors = []

            # log-Datei
            log_path = os.path.join(out_dir_path, texobj.name[:-3] + "log")

            # ... und eine log-Datei erzeugt wurde
            if os.path.exists(log_path):
                # durchsucht die erzeugte log-Datei und gibt deren entsprechende Fehlermeldungen zurück
                errors = get_Errors(log_path)

            # ... und keine log-Datei erzeugt wurde
            else:
                # gibt eine allgemeine Fehlermeldung mit dem return code des Kompilierprozesses zurück
                errors.append(ERROR_MESSAGES['COMPILATIONERROR'] + ': return code ' + str(rc))
    except Exception:
        errors.append(ERROR_MESSAGES['COMPILATIONERROR'])
    finally:
        # entferne alle temporären Ordner
        if os.path.isdir(out_dir_path):
            shutil.rmtree(out_dir_path)
        if os.path.isdir(root_path):
            shutil.rmtree(root_path)

    # Rückgabe
    # 1. Liste mit während des Kompilieren aufgetretenen Fehlermeldungen oder None, falls keine Fehler aufgetreten
    # 2. Array mit ID und Name der erzeugten pdf-Datei oder None, falls keine pdf-Datei erzeugt werden konnte
    return errors, file_data


def latexmk(args, console_output):
    """Kompiliert eine tex Datei mit dem latexmk Script und den entsprechenden Parametern

    :param args Parameter für die Ausführung
    :param console_output aktiviert die Ausgabe des Programmaufrufs in der Konsole
    :return: returncode des Programmaufrufs, id und name der erstellten Datei
    """

    command = ["perl", latexmk_path(), "-interaction=nonstopmode", "-outdir=" + args['outdirpath'], "-bibtex",
               '-pdflatex=' + args['compilerargs'], args['format'], args['texpath']]

    # Name der Ziel-Datei
    file_name = args['texobj'].name[:-3] + args['format'][1:]
    # Pfad der Ziel-Datei
    file_path = os.path.join(args['outdirpath'], file_name)
    # benenne die alte PDF Datei um
    if os.path.isfile(file_path):
        tempPdfPath = os.path.join(args['outdirpath'], file_name + '_old')
        os.rename(file_path, tempPdfPath)

    # kompiliert die tex-Datei gemäß der gesetzten Argumente:
    rc = execute_command(command, args['cwd'], console_output=console_output)

    # Rückgabe
    file_data = None

    # setze das verwendete Django Model und speichere die log Datei
    if args['format'][1:] == 'pdf':
        objecttype = PDF
    else:
        objecttype = BinaryFile

    # speichere die log Datei für pdf, ps und dvi export
    if args['format'][1:] == ('pdf' or 'ps' or 'dvi'):
        log_path = os.path.join(args['outdirpath'], args['texobj'].name[:-3] + "log")
        if os.path.isfile(log_path):
            logfile = open(log_path, 'r', encoding="cp437")
            logfile.seek(0)
            old_log = PlainTextFile.objects.filter(name=args['texobj'].name[:-3] + '<log>',
                                                   folder=args['texobj'].folder)
            if old_log.exists():
                old_log[0].delete()

            logObj = PlainTextFile.objects.create(name=args['texobj'].name[:-3] + '<log>',
                                                  folder=args['texobj'].folder,
                                                  source_code=logfile.read(),
                                                  size=util.getFileSize(logfile))
            logfile.close()


    # alte PDF
    file_src = objecttype.objects.filter(name=file_name, folder=args['texobj'].folder)

    if file_src.exists():
        file_data = {'id': file_src[0].id, 'name': file_src[0].name}

    # status der vorherigen Kompilierung
    oldstatus = args['texobj'].lastcompilestatus

    # setze den entsprechenden lastcompilestatus
    # 0 - keine Fehler
    # 1 - Fehler bei der Kompilierung
    if rc != 0:
        args['texobj'].lastcompilestatus = 1
    else:
        args['texobj'].lastcompilestatus = 0

    # speichere den status nur, wenn er sich geändert hat
    if oldstatus != args['texobj'].lastcompilestatus:
        args['texobj'].save()

    # wenn die Ziel-Datei erzeugt werden konnte
    if os.path.isfile(file_path):

        # löscht die etwaig bestehende Datei aus der Datenbank
        if file_src.exists():
            file_src[0].delete()

        file = open(file_path, 'rb')
        mimetype = util.getMimetypeFromFile(file, file_name)
        # erzeugt das Model aus der Datei
        pdfobj = objecttype.objects.createFromFile(name=file_name, folder=args['texobj'].folder, file=file,
                                                    mimeType=mimetype)
        file.close()


        # Rückgabewert
        file_data = {'id': pdfobj.id, 'name': pdfobj.name}

    return rc, file_data


def htlatex(args, console_output):
    """Kompiliert eine tex Datei mit htlatex in das HTML Format.

    :param args Parameter für die Ausführung
    :param console_output aktiviert die Ausgabe des Programmaufrufs in der Konsole
    :return: returncode des Programmaufrufs, id und name der erstellten Datei
    """

    # Rückgabe
    html_zip_data = None

    # Befehl zur Konvertierung in HTML mit htlatex
    command = ["htlatex", args['texpath'], 'html', "", "-d" + args['outdirpath'], "--interaction=nonstopmode"]
    rc = execute_command(command, args['cwd'], console_output=console_output)

    # wenn die HTML Datei erstellt werden konnte
    if os.path.isfile(os.path.join(args['outdirpath'], args['texobj'].name[:-3] + 'html')):
        # erstelle die zip Datei aus der HTML Datei
        args['outputfilename'] = args['texobj'].name[:-4] + '_html.zip'
        html_zip_data = createZipFile(args)
    return rc, html_zip_data


def pdf2htmlex(args, console_output):
    """Kompiliert eine tex Datei mit pdf2htmlEX in das HTML Format.

    :param args Parameter für die Ausführung
    :param console_output aktiviert die Ausgabe des Programmaufrufs in der Konsole
    :return: returncode des Programmaufrufs, id und name der erstellten Datei
    """

    # Rückgabe
    html_zip_data = None

    # Temp Ordner für die Erstellung der PDF Datei
    pdf_tmp_folder = util.getNewTempFolder()

    # Parameter für die PDF Kompilierung
    pdf_args = {
        'texobj': args['texobj'],
        'texpath': args['texpath'],
        'format': '-pdf',
        'outdirpath': pdf_tmp_folder,
        'compilerargs': args['compilerargs']
    }

    # kompiliere die tex Datei als PDF
    rc, pdf_file_data = latexmk(pdf_args, console_output=console_output)

    # Name der PDF-Datei
    pdf_name = args['texobj'].name[:-3] + 'pdf'
    # Pfad der PDF-Datei
    pdf_path = os.path.join(pdf_tmp_folder, pdf_name)

    # wenn die Ziel-Datei erzeugt werden konnte
    if os.path.isfile(pdf_path):
        # löscht die etwaig bestehende PDF Datei aus der Datenbank
        pdf_src = PDF.objects.filter(id=pdf_file_data['id'])
        if pdf_src.exists():
            pdf_src[0].delete()
    else:
        return rc, None

    debug = '0'
    if console_output:
        debug = '1'

    # Befehl zur Konvertierung in HTML mit pdf2htmlEX
    command = ['pdf2htmlEX', '--clean-tmp', '1', '--debug', debug, '--embed', 'cfijo', '--dest-dir',
               args['outdirpath'], pdf_path]
    rc = execute_command(command, args['cwd'], console_output=console_output)

    # wenn die HTML Datei erstellt werden konnte
    if os.path.isfile(os.path.join(args['outdirpath'], args['texobj'].name[:-3] + 'html')):
        # erstelle die zip Datei aus der HTML Datei
        args['outputfilename'] = args['texobj'].name[:-4] + '_pdf-html.zip'
        html_zip_data = createZipFile(args)

    # lösche den tmp Ordner der PDF Datei
    if os.path.isdir(pdf_tmp_folder):
        shutil.rmtree(pdf_tmp_folder)

    return rc, html_zip_data


def get_Errors(log_path):
    """Liefert eine Liste der Fehlermeldungen der log-Datei des übergebenen Datei-Pfades.

    :param log_path: Pfad der log-Datei deren Fehlermeldungen zurückgegeben werden sollen
    :return: eine Liste der Fehlermeldungen der übergebenen log-Datei
    """

    errors = []

    log = open(log_path, "r", encoding="cp437")

    # durchläuft sämtliche Zeilen der log-Datei
    for l in log:

        line = str.lower(l)

        # ----------------------------------------------------------------------------------------------------
        # FILE NOT FOUND ERROR
        # ----------------------------------------------------------------------------------------------------
        # bestimmt die Index-Position von 'file' in der aktuell betrachteten Zeile
        index_file = line.find('file')
        # falls 'file' in der aktuell betrachteten Zeile enthalten ist
        if 'latex' in line and index_file != -1:
            # bestimmt die Index-Position von 'not found' in der aktuell betrachteten Zeile
            index_notf = line.find('not found')
            # falls 'not found' in der aktuell betrachteten Zeile enthalten ist
            if index_notf != -1:
                # extrahiert den Namen der fehlenden Datei aus der aktuell betrachteten Zeile
                filename = line[index_file + len('file') + 2: index_notf - 2]
                error = ERROR_MESSAGES['COMPILATIONERROR_FILENOTFOUND'] + \
                        ': Die Datei \'' + filename + '\' konnte nicht gefunden werden.'
                # bestimmt die Index-Position von 'line' in der aktuell betrachteten Zeile
                index_line = line.find('line')
                # falls 'line' in der aktuell betrachteten Zeile enthalten ist
                if index_line != -1:
                    # extrahiert die Zeilennummer für die fehlende Datei aus der aktuell betrachteten Zeile
                    line_no = line[index_line + len('line') + 1: len(line) - 2]
                    error += ' (Zeile ' + line_no + ')'
                # fügt die ermittelte Fehlermeldung hinzu
                errors.append(error)

        # ----------------------------------------------------------------------------------------------------
        # SYNTAX ERROR
        # ----------------------------------------------------------------------------------------------------
        if 'job aborted' in line:
            if 'no legal \end found' in line:
                errors.append(
                    ERROR_MESSAGES['COMPILATIONERROR_SYNTAXERROR'] + ': Es konnte kein gültiges \end gefunden werden.')
        # undefiniertes Steuerzeichen
        if 'undefined control sequence' in line:
            error = ERROR_MESSAGES['COMPILATIONERROR_SYNTAXERROR'] + ': Undefiniertes Steuerzeichen.'
            # extrahiert die Zeilennummer für das undefinierte Steuerzeichen aus der nächsten log-Zeile
            nxt_line = str(log.readline())
            line_no = nxt_line[2:nxt_line.find(' ')]
            error += ' (Zeile ' + line_no + ')'
            # fügt die ermittelte Fehlermeldung hinzu
            errors.append(error)

        # ----------------------------------------------------------------------------------------------------
        #                                          CITATION UNDEFINED
        # ----------------------------------------------------------------------------------------------------
        if "citation" in line:
            errors.append(ERROR_MESSAGES['COMPILATIONERROR_CITATIONUNDEFINED'])

    log.close()

    # bei unbehandelten Fehlern wird eine allgemeine Kompilierungsfehlermeldung zurückgegeben
    if len(errors) == 0:
        errors.append(ERROR_MESSAGES['COMPILATIONERROR'])
    return errors


def latexmk_path():
    """Liefert den Dateipfad zum Latexmk-Script.

    :return: Dateipfad zum Latexmk-Script
    """

    return os.path.join(BASE_DIR, "app", "common", "latexmk.pl")


def execute_command(args, workingdir, console_output=False):
    """Führt einen Befehl mit den zugehörigen Parametern aus.

    :param args: Liste mit dem auszuführenden Befehl und den zugehörigen Parametern
    :param workingdir: Arbeitsverzeichnis, in welchem der Befehl ausgeführt wird
    :param console_output: aktiviert/deaktiviert die Ausgabe des ausgeführten Programmes in der Konsole (für Debug)
    :return: return code des Programmaufrufs
    """

    if console_output:
        return subprocess.call(args, bufsize=0, cwd=workingdir)
    else:
        return subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, bufsize=0, cwd=workingdir)


def htlatex_script(parameter, console_output=False):
    """htlatex Skript aus texlive (unter Linux in /usr/bin/htlatex)

    :param parameter: notwendige Paramater für die Ausführung des htlatex Skripts
    :param console_output aktiviert die Ausgabe des Programmaufrufs in der Konsole
    :return: return code der Ausführung
    """

    code = r'\makeatletter\def\HCode{\futurelet\HCode\HChar}\def\HChar{\ifx"\HCode\def\HCode"##1"{\Link##1}\expandafter\
    HCode\else\expandafter\Link\fi}\def\Link#1.a.b.c.{\g@addto@macro\@documentclasshook{\RequirePackage[#1,html]' \
           '{tex4ht}}\let\HCode\documentstyle\def\documentstyle{\let\documentstyle\HCode\expandafter\def\csname tex4ht\
           endcsname{#1,html}\def\HCode####1{\documentstyle[tex4ht,}\@ifnextchar[{\HCode}{\documentstyle[tex4ht]}}}' \
           '\makeatother\HCode ' + parameter['2'] + r'.a.b.c.\input '
    execute_command(['latex', parameter['5'], code, parameter['1']], console_output)
    execute_command(['latex', parameter['5'], code, parameter['1']], console_output)
    execute_command(['latex', parameter['5'], code, parameter['1']], console_output)
    execute_command(['tex4ht', r'-f/' + parameter['1'], r'-i~/tex4ht.dir/texmf/tex4ht/ht-fonts/' + parameter['3']],
                    console_output)
    return execute_command(['t4ht', r'-f/' + parameter['1'], parameter['4']], console_output)


def createZipFile(args):
    """Erstellt eine zip Datei aus der HTML Datei.

    :param args: Argumente welche für die Erstellung der zip Datei notwendig sind, z.B. Pfadangaben
    :return: id und name der erstellten Datei
    """

    # Temp Ordner zur Speicherung der zip Datei
    tmp_folder = util.getNewTempFolder()

    # Name der zip Datei test.tex -> test_pdf-html.zip|test_html.zip
    zip_file_name = args['outputfilename']
    zip_file_path = os.path.join(tmp_folder, zip_file_name)

    # überprüfe, ob die zip Datei bereits existiert, falls ja dann lösche diese
    binsrcobj = BinaryFile.objects.filter(name=zip_file_name, folder=args['texobj'].folder)
    if binsrcobj.exists():
        binsrcobj[0].delete()

    # erstelle die zip Datei aus dem Ordner
    util.createZipFromFolder(args['outdirpath'], zip_file_path)

    # speichere die zip Datei in der Datenbank
    binary_file = open(zip_file_path, 'rb')
    binaryobj = BinaryFile.objects.createFromFile(name=zip_file_name, file=binary_file,
                                                  folder=args['texobj'].folder, mimeType=ZIPMIMETYPE)
    binary_file.close()

    # lösche den temp Ordner
    if os.path.isdir(tmp_folder):
        shutil.rmtree(tmp_folder)

    return {'id': binaryobj.id, 'name': binaryobj.name}