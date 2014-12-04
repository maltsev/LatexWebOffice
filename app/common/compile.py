"""

* Purpose : Kompilierer

* Creation Date : 27-11-2014

* Last Modified : Do 04 Dec 2014 12:25:31 CET

* Author : ingo

* Coauthors :

* Sprintnumber : 2

* Backlog entry : TEK1

"""
import ntpath, os, re, shutil, subprocess, tempfile, time
from app.common.constants import ERROR_MESSAGES
from app.models.file.file import File
from app.models.file.pdf import PDF
from app.models.file.texfile import TexFile
from app.models.folder import Folder
from app.models.project import Project
from core.settings import BASE_DIR

#
# Kompiliert die, der übergebenen ID entsprechende, tex-Datei unter Einbindung der zugehörigen Dateien in eine pdf-Datei und gibt deren ID und Name zurück.
# Sofern ein Kompilieren erfolgen konnte, werden die ID und der Name der erzeugten pdf-Datei zurückgegeben - andernfalls None.
# Falls beim Kompilieren Fehler auftraten, werden zudem die entsprechenden Fehlermeldungen als Zeichenketten zurückgegeben - andernfalls ist dieser Wert None.
# Hierbei wird zum Kompilieren das Perl-Script latexmk.pl verwendet.
#
# @param texid Id der tex-Datei, welche kompiliert werden soll
#
# @return ein Tupel aus folgenden Komponenten:
#         1. Liste der Fehlermeldungen, welche beim Kompilieren geworfen wurden oder None, falls keine Fehler auftraten
#         2. Array der ID und des Namens der erzeugten pdf-Datei oder None, sofern keine pdf-Datei erzeugt werden konnte
#
def compile(texid):
    
    # tex-File der übergebenen ID
    tex_fle  = TexFile.objects.get(id=texid)
    # Verzeichnis der tex-Datei
    tex_dir  = tex_fle.folder
    # root-Verzeichnis der tex-Datei
    root     = tex_dir.getRoot()
    # Pfad des root-Verzeichnisses
    root_pth = root.getTempPath()
    
    # Dateien und Verzeichnisse des root-Verzeichnisses
    fs = root.getFilesAndFoldersRecursively()
    # legt die Verzeichnisstruktur temporär an
    for f in fs :
        f.getTempPath()
        
    # temporärer Pfad der, der übergebenen tex-ID entsprechenden, tex-Datei
    tex_pth     = tex_fle.getTempPath()
    # Datei-Name der übergebenen tex-Datei
    tex_nme     = ntpath.basename(tex_pth)
    # Verzeichnis-Pfad der übergebenen tex-Datei
    tex_dir_pth = ntpath.dirname(tex_pth)
    
    # erzeugt ein temporäres Ausgabe-Verzeichnis im Verzeichnis der übergebenen tex-Datei
    out_dir_pth = tempfile.mkdtemp('','',tex_dir_pth)
    
    # ----------------------------------------------------------------------------------------------------
    #                                             KOMPILIERUNG                                            
    # ----------------------------------------------------------------------------------------------------
    # wechselt in das Verzeichnis der tex-Datei
    os.chdir(root_pth)
    # kompiliert die tex-Datei gemäß der gesetzten Argumente:
    # '-f' führt die Kompilieren auch unter auftretenden Fehlern so möglich durch
    # '-interaction=nonstopmode' unterbindet die Unterbrechung des Kompiliervorgangs für eine manuelle Eingabeaufforderung (falls eines der ausführenden Programm einen Fehler festgestellt hat)
    # '-outdir=FOO' Verzeichnis für die Ausgabe-Dateien
    # '-bibtex' bbl-Dateien werden über bibtex erzeugt, sofern notwendig
    # '-pdf' pdf-Datei wird über pdflatex aus der angegebenen tex-Datei erzeugt
    rc = subprocess.Popen(["latexmk","-f","-interaction=nonstopmode","-outdir="+out_dir_pth,"-bibtex","-pdf",tex_pth],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    rc.wait()
    
    # ----------------------------------------------------------------------------------------------------
    #                                        RÜCKGABEWERT PDF-DATEN                                       
    # ----------------------------------------------------------------------------------------------------
    pdf_data = None
    
    # Name der Ziel-pdf-Datei
    pdf_nme  = tex_nme[:-3]+"pdf"
    # Pfad der Ziel-pdf-Datei
    pdf_pth = os.path.join(out_dir_pth,pdf_nme)
    
    # wenn die Ziel-pdf-Datei erzeugt werden konnte
    if os.path.exists(pdf_pth) :
        
        # löscht die etwaig bestehende pdf-Version der tex-Datei aus der Datenbank
        pdf_src = PDF.objects.filter(name=pdf_nme,folder=tex_dir)
        if pdf_src!=None :
            if len(pdf_src)==1 :
                PDF.objects.get(id=pdf_src[0].id).delete()
        
        pdf_file = open(pdf_pth,'rb')
        # erzeugt das PDF-Model aus der pdf-Datei
        pdf = PDF.objects.createFromFile(name=pdf_nme,folder=tex_dir,file=pdf_file)
        
        # Rückgabewert
        pdf_data = {'id':pdf.id,'name':pdf.name}
    
    # ----------------------------------------------------------------------------------------------------
    #                                     RÜCKGABEWERT FEHLERMELDUNGEN                                    
    # ----------------------------------------------------------------------------------------------------
    errors = None
    
    # wenn beim Kompilier-Prozess ein Fehler aufgetreten ist ...
    if rc.returncode!=0 :
        
        # Fehlermeldungen
        errors = []
        
        # log-Datei
        log_path = os.path.join(out_dir_pth,tex_nme[:-3]+"log")
        
        # ... und eine log-Datei erzeugt wurde
        if os.path.exists(log_path) :
            # durchsucht die erzeugte log-Datei und gibt deren entsprechende Fehlermeldungen zurück
            errors = get_Errors(log_path)
            
        # ... und keine log-Datei erzeugt wurde
        else :
            # gibt eine allgemeine Fehlermeldung mit dem return code des Kompilierprozesses zurück
            errors.append(ERROR_MESSAGES['COMPILATIONERROR']+': return code '+str(rc))
        
    # ----------------------------------------------------------------------------------------------------
    
    # entfernt das temporäre root-Verzeichnis und sämtliche Unterordner
    shutil.rmtree(root_pth)
    
    # Rückgabe
    # 1. Liste mit während des Kompilieren aufgetretenen Fehlermeldungen oder None, falls keine Fehler aufgetreten
    # 2. Array mit ID und Name der erzeugten pdf-Datei oder None, falls keine pdf-Datei erzeugt werden konnte
    return (errors,pdf_data)

#
# Liefert eine Liste der Fehlermeldungen der log-Datei des übergebenen Datei-Pfades.
#
# @param log_path Pfad der log-Datei deren Fehlermeldungen zurückgegeben werden sollen
#
# @return eine Liste der Fehlermeldungen der übergebenen log-Datei
#
def get_Errors(log_path):
    
    errors = []
    
    log = open(log_path,"r")
    # durchläuft sämtliche Zeilen der log-Datei
    for l in log :
        
        line = str.lower(l)
        
        # Emergency Stop
        if "! emergency stop" in line :
            # TODO
            errors.append(ERROR_MESSAGES['COMPILATIONERROR_SYNTAXERROR'])
        # FileNotFound-Error
        if "file" in line and "not found" in line :
            errors.append(ERROR_MESSAGES['COMPILATIONERROR_FILENOTFOUND'])
        if "warning" in line :
            errors.append(ERROR_MESSAGES['COMPILATIONERROR_CITATIONUNDEFINED'])
            
    log.close()
    
    if len(errors)==0 :
        errors.append(ERROR_MESSAGES['COMPILATIONERROR'])
    
    return errors