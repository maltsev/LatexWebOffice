"""

* Purpose : Kompilierer

* Creation Date : 27-11-2014

* Last Modified : Fr 05 Dec 2014 06:58:37 CET

* Author : ingo

* Coauthors :

* Sprintnumber : 2

* Backlog entry : TEK1

"""
import ntpath, os, re, shutil, subprocess, sys, tempfile, time
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
    p = subprocess.Popen(["perl",latexmk_path(),"-f","-interaction=nonstopmode","-outdir="+out_dir_pth,"-bibtex","-pdf",tex_pth],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    
    # ----------------------------------------------------------------------------------------------------
    #                                        RÜCKGABEWERT PDF-DATEN                                       
    # ----------------------------------------------------------------------------------------------------
    pdf_data = None
    
    # Name der Ziel-pdf-Datei
    pdf_nme = tex_nme[:-3]+"pdf"
    # Pfad der Ziel-pdf-Datei
    pdf_pth = os.path.join(out_dir_pth,pdf_nme)
    
    # wenn die Ziel-pdf-Datei erzeugt werden konnte
    if os.path.exists(pdf_pth) :
        
        # löscht die etwaig bestehende pdf-Version der tex-Datei aus der Datenbank
        pdf_src = PDF.objects.filter(name=pdf_nme,folder=tex_dir)
        if pdf_src!=[] :
            if len(pdf_src)==1 :
                PDF.objects.get(id=pdf_src[0].id).delete()
        
        pdf_file = open(pdf_pth,'r+b')
        try:
            # erzeugt das PDF-Model aus der pdf-Datei
            pdf = PDF.objects.createFromFile(name=pdf_nme,folder=tex_dir,file=pdf_file)
        finally:
            pdf_file.close()
        
        # Rückgabewert
        pdf_data = {'id':pdf.id,'name':pdf.name}
    
    # ----------------------------------------------------------------------------------------------------
    #                                     RÜCKGABEWERT FEHLERMELDUNGEN                                    
    # ----------------------------------------------------------------------------------------------------
    errors = None
    
    # wenn beim Kompilier-Prozess ein Fehler aufgetreten ist ...
    if p.returncode!=0 :
        
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
            errors.append(ERROR_MESSAGES['COMPILATIONERROR']+': return code '+str(p))
        
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
    
    log = open(log_path,"r+")
    
    try:
        # durchläuft sämtliche Zeilen der log-Datei
        for l in log :
            
            line = str.lower(l)
            
            # ----------------------------------------------------------------------------------------------------
            #                                         FILE NOT FOUND ERROR                                        
            # ----------------------------------------------------------------------------------------------------
            # bestimmt die Index-Position von 'file' in der aktuell betrachteten Zeile
            index_file = line.find('file')
            # falls 'file' in der aktuell betrachteten Zeile enthalten ist
            if 'latex' in line and index_file!=-1 :
                # bestimmt die Index-Position von 'not found' in der aktuell betrachteten Zeile
                index_notf = line.find('not found')
                # falls 'not found' in der aktuell betrachteten Zeile enthalten ist
                if index_notf!=-1 :
                    # extrahiert den Namen der fehlenden Datei aus der aktuell betrachteten Zeile
                    filename = line[index_file+len('file')+2 : index_notf-2]
                    error    = ERROR_MESSAGES['COMPILATIONERROR_FILENOTFOUND']+': Die Datei \''+filename+'\' konnte nicht gefunden werden.'
                    # bestimmt die Index-Position von 'line' in der aktuell betrachteten Zeile
                    index_line = line.find('line')
                    # falls 'line' in der aktuell betrachteten Zeile enthalten ist
                    if index_line!=-1 :
                        # extrahiert die Zeilennummer für die fehlende Datei aus der aktuell betrachteten Zeile
                        line_no = line[index_line+len('line')+1 : len(line)-2]
                        error  += ' (Zeile '+line_no+')'
                    # fügt die ermittelte Fehlermeldung hinzu
                    errors.append(error)
            
            # ----------------------------------------------------------------------------------------------------
            #                                             SYNTAX ERROR                                            
            # ----------------------------------------------------------------------------------------------------
            if 'job aborted' in line :
                if 'no legal \end found' in line :
                    errors.append(ERROR_MESSAGES['COMPILATIONERROR_SYNTAXERROR']+': Es konnte kein gültiges \end gefunden werden.')
            # undefiniertes Steuerzeichen
            if 'undefined control sequence' in line :
                error = ERROR_MESSAGES['COMPILATIONERROR_SYNTAXERROR']+': Undefiniertes Steuerzeichen.'
                # extrahiert die Zeilennummer für das undefinierte Steuerzeichen aus der nächsten log-Zeile
                nxt_line = str(log.readline())
                line_no = nxt_line[2:nxt_line.find(' ')]
                error  += ' (Zeile '+line_no+')'
                # fügt die ermittelte Fehlermeldung hinzu
                errors.append(error)
            
            # ----------------------------------------------------------------------------------------------------
            #                                          CITATION UNDEFINED                                         
            # ----------------------------------------------------------------------------------------------------
            if "citation" in line :
                errors.append(ERROR_MESSAGES['COMPILATIONERROR_CITATIONUNDEFINED'])
    finally:
        log.close()
    
    # bei unbehandelten Fehlern wird eine allgemeine Kompilierungsfehlermeldung zurückgegeben
    if len(errors)==0 :
        errors.append(ERROR_MESSAGES['COMPILATIONERROR'])
    
    return errors

#
# Liefert den Dateipfad zum Latexmk-Script.
#
# @return den Dateipfad zum Latexmk-Script
#
def latexmk_path():
    return os.path.join(BASE_DIR,"app","common","latexmk.pl")