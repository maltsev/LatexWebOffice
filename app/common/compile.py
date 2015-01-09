"""

* Purpose : Kompilierer

* Creation Date : 27-11-2014

* Last Modified : Mo 15 Dez 2014 13:32:09 CET

* Author : ingo

* Coauthors :

* Sprintnumber : 2

* Backlog entry : TEK1

"""
import ntpath, os, re, shutil, subprocess, tempfile, time
from app.common.constants import ERROR_MESSAGES, ZIPMIMETYPE
from app.models.file.file import File
from app.models.file.pdf import PDF
from app.models.file.texfile import TexFile
from app.models.folder import Folder
from app.models.project import Project
from app.models.file.binaryfile import BinaryFile
from app.common import util
from core.settings import BASE_DIR


def latexcompile(texid, formatid=0):
    """Kompiliert eine tex Datei mit der übergebenen texid in das entsprechende Ausgabeformat (formatid).

    formatid:   0 - PDF
                1 - HTML (Rückgabe als zip Datei)
                2 - DVI
                3 - PS

    Zum Kompilieren wird das Perl-Script latexmk.pl verwendet (nutzt texlive), bzw. für HTML wird htlatex genutzt.

    Latexmk:
    http://users.phys.psu.edu/~collins/software/latexmk-jcc/

    :param texid: Id der tex Datei
    :param formatid: Id des Ausgabeformates
    :return: Tupel aus folgenden Komponenten:
        1. Liste der Fehlermeldungen, welche beim Kompilieren geworfen wurden oder None, falls keine Fehler auftraten
        2. Array der ID und des Namens der erzeugten pdf-Datei oder None, sofern keine pdf-Datei erzeugt werden konnte
    """

    # sichere das alte Arbeitsverzeichnis
    oldwd = os.getcwd()

    # tex-File der übergebenen ID
    texobj = TexFile.objects.get(id=texid)

    # Verzeichnis der tex-Datei
    tex_dir = texobj.folder

    # root-Verzeichnis der tex-Datei
    rootobj = tex_dir.getRoot()

    # Pfad des root-Verzeichnisses
    # es werden alle Dateien und Ordner des Projektes in einen temporären Ordner kopiert
    root_path = rootobj.dumpFolder()

    # temporärer Pfad der, der übergebenen tex-ID entsprechenden, tex-Datei
    tex_path = texobj.getTempPath()

    # Datei-Name der übergebenen tex-Datei
    tex_name = texobj.name

    # Verzeichnis-Pfad der übergebenen tex-Datei
    tex_dir_path = ntpath.dirname(tex_path)

    # erzeugt ein temporäres Ausgabe-Verzeichnis im Verzeichnis der übergebenen tex-Datei
    out_dir_path = tempfile.mkdtemp(dir=tex_dir_path)

    # wechselt in das Verzeichnis der tex-Datei
    os.chdir(texobj.folder.getTempPath())

    formatid = str(formatid)
    rc = 0
    file_data = {}
    errors = None

    # Parameter für die Kompilierung
    # '-f' führt die Kompilieren auch unter auftretenden Fehlern so möglich durch
    # '-interaction=nonstopmode' unterbindet die Unterbrechung des Kompiliervorgangs für eine
    #   manuelle Eingabeaufforderung (falls eines der ausführenden Programm einen Fehler festgestellt hat)
    # '-outdir=FOO' Verzeichnis für die Ausgabe-Dateien
    # '-bibtex' bbl-Dateien werden über bibtex erzeugt, sofern notwendig
    # '-pdf' pdf-Datei wird über pdflatex aus der angegebenen tex-Datei erzeugt

    # mögliche Formate der Kompilierung
    latexmk_formatargs = {
        '0': '-pdf',
        '2': '-dvi',
        '3': '-ps'
    }

    # verwendeter Latex Compiler
    compilerargs = 'pdflatex --shell-escape %O %S'

    # wenn die tex Datei mit latexmk kompiliert werden soll
    if formatid in latexmk_formatargs:
        args = ["perl", latexmk_path(), "-f", "-interaction=nonstopmode", "-outdir=" + out_dir_path, "-bibtex",
                '-pdflatex=' + compilerargs, latexmk_formatargs[formatid], texobj.getTempPath()]
        rc, file_data = latexmk(texobj, out_dir_path, args, latexmk_formatargs[formatid][1:])
    # HTML Format mit htlatex
    elif formatid == '1':
        args = ["htlatex", texobj.getTempPath(), "", "", "-d" + util.getFolderName(out_dir_path) + os.sep]
        rc, file_data = htlatex(texobj, out_dir_path, args)
    # Ungültige formatid
    else:
        errors = ERROR_MESSAGES['UNKNOWNFORMAT']

    # wenn beim Kompilier-Prozess ein Fehler aufgetreten ist ...
    if rc != 0:
        # Fehlermeldungen
        errors = []

        # log-Datei
        log_path = os.path.join(out_dir_path, tex_name[:-3] + "log")

        # ... und eine log-Datei erzeugt wurde
        if os.path.exists(log_path):
            # durchsucht die erzeugte log-Datei und gibt deren entsprechende Fehlermeldungen zurück
            errors = get_Errors(log_path)

        # ... und keine log-Datei erzeugt wurde
        else:
            # gibt eine allgemeine Fehlermeldung mit dem return code des Kompilierprozesses zurück
            errors.append(ERROR_MESSAGES['COMPILATIONERROR'] + ': return code ' + str(rc))

    # stelle das vorherige Arbeitsverzeichnis wieder her
    os.chdir(oldwd)

    # entferne das temporäre root-Verzeichnis und sämtliche Unterordner
    shutil.rmtree(root_path)

    # Rückgabe
    # 1. Liste mit während des Kompilieren aufgetretenen Fehlermeldungen oder None, falls keine Fehler aufgetreten
    # 2. Array mit ID und Name der erzeugten pdf-Datei oder None, falls keine pdf-Datei erzeugt werden konnte
    return errors, file_data


def latexmk(texobj, out_dir_path, args, outputtype):
    """Kompiliert eine tex Datei mit dem latexmk Script und den entsprechenden Parametern

    :param texobj: TexFile Objekt, welches kompiliert werden soll
    :param out_dir_path: temp Ordner, in welchen die Ausgabedateien erstellt werden
    :param args: Auszuführender Befehl mit den zugehörigen Parametern
    :param outputtype: Dateiendung für Ausgabedatei (z.B. 'pdf', 'dvi')
    :return: returncode des Programmaufrufs, id und name der erstellten Datei
    """

    # kompiliert die tex-Datei gemäß der gesetzten Argumente:
    rc = execute_command(args)

    # Rückgabe
    file_data = None

    # setze das verwendete Django Model
    if outputtype == 'pdf':
        objecttype = PDF
    else:
        objecttype = BinaryFile

    # Name der Ziel-Datei
    file_name = texobj.name[:-3] + outputtype
    # Pfad der Ziel-Datei
    file_path = os.path.join(out_dir_path, file_name)

    # wenn die Ziel-Datei erzeugt werden konnte
    if os.path.isfile(file_path):

        # löscht die etwaig bestehende Datei aus der Datenbank
        file_src = objecttype.objects.filter(name=file_name, folder=texobj.folder)
        if file_src.exists():
            file_src[0].delete()

        file = open(file_path, 'rb')
        mimetype = util.getMimetypeFromFile(file, file_name)
        # erzeugt das Model aus der Datei
        fileobj = objecttype.objects.createFromFile(name=file_name, folder=texobj.folder, file=file, mimeType=mimetype)
        file.close()

        # Rückgabewert
        file_data = {'id': fileobj.id, 'name': fileobj.name}

    return rc, file_data


def htlatex(texobj, out_dir_path, args):
    """Kompiliert eine tex Datei mit htlatex in das HTML Format.

    :param texobj: TexFile Objekt, welches kompiliert werden soll
    :param out_dir_path: temp Ordner, in welchen die Ausgabedateien erstellt werden
    :param args: Auszuführender Befehl mit den zugehörigen Parametern
    :return: returncode des Programmaufrufs, id und name der erstellten Datei
    """

    # Rückgabe
    html_zip_data = None

    # Kompiliere als HTML
    rc = execute_command(args)

    # wenn die HTML Datei erstellt werden konnte
    if os.path.isfile(os.path.join(out_dir_path, texobj.name[:-3] + 'html')):
        # Temp Ordner zur Speicherung der zip Datei
        tmp_folder = util.getNewTempFolder()

        # Name der zip Datei test.tex -> test_html.zip
        zip_file_name = texobj.name[:-4] + '_html.zip'
        zip_file_path = os.path.join(tmp_folder, zip_file_name)

        # überprüfe, ob die zip Datei bereits existiert, falls ja dann lösche diese
        binsrcobj = BinaryFile.objects.filter(name=zip_file_name, folder=texobj.folder)
        if binsrcobj.exists():
            binsrcobj[0].delete()

        # erstelle die zip Datei aus dem Ordner
        util.createZipFromFolder(out_dir_path, zip_file_path)

        # speichere die zip Datei in der Datenbank
        binary_file = open(zip_file_path, 'rb')
        binaryobj = BinaryFile.objects.createFromFile(name=zip_file_name, file=binary_file, folder=texobj.folder,
                                                      mimeType=ZIPMIMETYPE)
        binary_file.close()

        html_zip_data = {'id': binaryobj.id, 'name': binaryobj.name}

        # lösche den temp Ordner
        shutil.rmtree(tmp_folder)

    return rc, html_zip_data


def get_Errors(log_path):
    """Liefert eine Liste der Fehlermeldungen der log-Datei des übergebenen Datei-Pfades.

    :param log_path: Pfad der log-Datei deren Fehlermeldungen zurückgegeben werden sollen
    :return: eine Liste der Fehlermeldungen der übergebenen log-Datei
    """

    errors = []

    log = open(log_path, "r")

    # durchläuft sämtliche Zeilen der log-Datei
    for l in log:

        line = str.lower(l)

        # ----------------------------------------------------------------------------------------------------
        #                                         FILE NOT FOUND ERROR
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
                error = ERROR_MESSAGES[
                            'COMPILATIONERROR_FILENOTFOUND'] + ': Die Datei \'' + filename + '\' konnte nicht gefunden werden.'
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
        #                                             SYNTAX ERROR
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


def execute_command(args):
    """

    :param args: Liste mit dem auszuführenden Befehl und den zugehörigen Parametern
    :return: return code des Programmaufrufs
    """

    return subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, bufsize=0)