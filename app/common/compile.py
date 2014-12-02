"""

* Purpose : Kompilierer

* Creation Date : 27-11-2014

* Last Modified : Do 28 Nov 2014 20:57:31 CET

* Author : ingo

* Coauthors :

* Sprintnumber : 2

* Backlog entry : TEK1

"""
import ntpath, os, shutil, tempfile
from app.common.constants import ERROR_MESSAGES
from core.settings import BASE_DIR

#
# Kompiliert die übergebene tex-Datei unter Einbindung der angegebenen Dateien in eine pdf-Datei und gibt diese zurück.
# Hierbei wird zum Kompilieren das Perl-Script latexmk.pl verwendet.
#
# @param texfile Pfad der tex-Datei, welche kompiliert werden soll
# @param files Pfade der zu der übergebenen tex-Datei zugehörigen Dateien
#
# @return die aus den übergebenen Dateien kompilierte pdf-Datei
#         oder eine Fehlermeldung, falls das Kompilieren fehlschlug
#
def compile(texfile,files):
    
    # Dateiname der übergebenen tex-Datei
    tex_nme = ntpath.basename(texfile)
    # Verzeichnis der übergebenen tex-Datei
    tex_dir = ntpath.dirname(texfile)
    
    # erzeugt ein temporäres Verzeichnis im Verzeichnis der übergebenen tex-Datei
    out_dir = tempfile.mkdtemp('','',tex_dir)
    
    # kompiliert die tex-Datei
    # '-c' entfernt sämtliche Hilfsdateien (aux,log,...) nach dem Kompilieren
    # '-outdir=FOO' Verzeichnis für die Ausgabe-Dateien von pdflatex
    # '-pdf' erzeugt aus der angegebenen tex-Datei über pdflatex eine pdf-Datei
    rcode = os.system(str(latexmk_path())+" -outdir="+out_dir+" -pdf "+texfile)
    
    # wenn der Kompilier-Prozess erfolgreich beendet wurde
    if rcode==0 :
        # Name der erzeugten pdf-Datei
        pdf_nme = tex_nme[:-3]+"pdf"
        # neuer Pfad der erzeugten pdf-Datei
        pdffile = os.path.join(tex_dir,pdf_nme)
        
        # TEMP
        # verschiebt die erzeugte pdf-Datei in das Verzeichnis der übergebenen tex-Datei
        os.rename(os.path.join(out_dir,pdf_nme),pdffile)
        # entfernt das temporäre Verzeichnis
        shutil.rmtree(out_dir)
        
        return pdffile
    # wenn beim Kompilier-Prozess ein Fehler aufgetreten ist
    else :
        # gibt eine Fehlermeldung zurück
        return ERROR_MESSAGES['COMPILATIONERROR']
    
#
# Liefert den Dateipfad zum Latexmk-Script.
#
# @return den Dateipfad zum Latexmk-Script
#
def latexmk_path():
    return os.path.join(BASE_DIR,"app","common","latexmk.pl")