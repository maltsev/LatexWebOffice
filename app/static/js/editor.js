/*
@author: Thore Thießen, Timo Dümke, Franziska Everinghoff, Christian Lohmann
@creation: 21.11.2014 - sprint-nr: 2
@last-change: .02.03.2015 - sprint-nr: 6
*/

/// ID der im Editor geöffneten Datei
var id;

// ID des verwendeten Compilers
// 0 - pdflatex
// 1 - lualatex
// 2 - xelatex
var compilerid = 0;

var rootid = -1;

/// Editor
var editor;

/// Änderungen im Editor gespeichert?
var changesSaved = true;

// wurde der Compiler gewechselt?
var compilerChanged = false;

var file_locked = false;

var file_name = '';

// Timer zur automatischen Speicherung
var autosaveTimer;

// automatisches Speichern alle 5 Minuten
var autosaveInterval = 300000;

/// Grafikassistentdropdownmenue
var dropdownWindow = false;

/// Grafikassistent Selectionid
var selectionid = 0;

// notwendig für jquery-layout
var myLayout;

var eastIsOpen = true;
var southIsOpen = false;

// Zeit bis der Editor nach einer Änderung der Fenstergröße aktualisiert wird
var editorResizeTimeout = 50;

// Zeit bis die Buttons wieder aktiviert werden, falls keine Antwort vom Server kommt
var btnCompileExportTimeout = 15000;
var btnCompileExportTimeout_HTML = 60000;

/**
 * Lädt den Editor, sobald das Dokument vollständig geladen wurde.
 */
$(document).ready(function() {
    var width = $(window).width();
    var height = $(window).height();

    var mobile = window.mobilecheck();

    $('[data-toggle="tooltip"]').tooltip();

    // Funktion für SplitView, setzt die Breite der Trennlinie
    myLayout = $('#maincontainer').layout({
        enableCursorHotkey: false,
        center: {
            spacing_open: 14,
            spacing_closed: 14,
            slidable: false,
            size: (mobile?'100%':'60%'),
        },
        east: {
            spacing_open: 14,
            spacing_closed: 14,
            slidable: false,
            initClosed: (mobile?true:false),
            size: (mobile?'100%':'40%'),
        },
        south: {
            spacing_open: 14,
            spacing_closed: 14,
            slidable: false,
            initClosed: true,
            size: '35%',
        },
        // Editor automatisch an Fenstergröße anpassen
        onresize: function () {
            setTimeout(
                function() {
                    editor.refresh();
                },
                editorResizeTimeout
            );
        },
    });

	// Datei-ID abfragen
	id = parseInt(location.hash.substr(1));
	if (isNaN(id)) {
		// ungültige ID
		backToProject();
	} else {
	    // da das Dokument gerade geladen wird, gab es noch keine Änderungen an der tex Datei
	    changesSaved = true;

        loadFile();

        // Speichern und freigeben der tex Datei beim Schließen des Editors
		$(window).bind('beforeunload', function() {
			if (!changesSaved && !file_locked) {
				    documentsJsonRequest({
                        'command': 'updatefile',
                        'id': id,
                        'content': editor.getValue()
                    }, function(result, data) {
                        unlock();
                });
	        }
		});

        // automatisches Speichern, falls Fenster/Tab inaktiv (sofern es Änderungen gab)
		$(window).blur(function() {
			if (!changesSaved && !file_locked) {
				saveFile(true);
			}
		});
        
		// Button für das Speichern belegen
		$('#save').click(function() {
			saveFile(false);
		});
		// Button für das PDF Exportieren belegen
		$('#pdfExport').click(function() {
			exportFile(0);
		});
        // Button für das HTML Exportieren belegen
		$('#export_html').click(function() {
			exportFile(1);
		});
		// Button für das DVI Exportieren belegen
		$('#export_dvi').click(function() {
			exportFile(2);
		});
	    // Button für das PS Exportieren belegen
		$('#export_ps').click(function() {
			exportFile(3);
		});
	    // Button für das Kompilieren (aktualisieren der PDF Anzeige) belegen
		$('#compile').click(function() {
			compile(true);
		});
		$('#backtofileview').click(function() {
			backToFileView();
		});
        // Dropdowm Button Text je nach Auswahl des Compilers richtig setzen und die compilerID ändern
		$("#compiler-dropdown li a").click(function(){
            $(this).parents(".compiler-btn").find('.btn').html($(this).text()+" <span class=\"caret\"></span>");
            if (compilerid != $(this).attr('value')) {
                // Compiler wurde verändert, dadurch wird beim nächsten Kompilieren der forcecompile Parameter gesetzt,
                // so dass die Datei auf jeden Fall neu kompiliert wird, auch wenn es keine Änderungen an der tex Datei gab
                compilerChanged = true;
                compilerid = $(this).attr('value');
            }
        });
	};
});

// Dialogfenster Tabellenassistent
function createTable() {
	$('#dialog_tabelle_erstellen').dialog({
	width:'auto'});
}

// Dialogfenster Grafikassistent
function openInsertImageDialog() {
	$('#dialog_grafik_einfuegen').dialog({
	width:'auto'});
}

function hidePanes() {
    eastIsOpen = !myLayout.state.east.isClosed;
    southIsOpen = !myLayout.state.south.isClosed;
    if (eastIsOpen) {
        myLayout.close("east");
    }
    if (southIsOpen) {
        myLayout.close("south");
    }

}

function resetPanes() {
    if (eastIsOpen) {
        myLayout.open("east");
    }
    if (southIsOpen) {
        myLayout.open("south");
    }

}

/**
 * Leitet den Benutzer zurück zur Projektverwaltung.
 */
function backToProject() {
	window.location.replace('/projekt/');
}

/**
 * Leitet den Benutzer zurück zur Dateiansicht des aktuellen Projektes.
 */
function backToFileView() {
    if (!file_locked) {
	    documentsJsonRequest({
            'command': 'unlockfile',
            'id': id
        }, function(result, data) {
            file_locked = false;
            if (! result) {
                showAlertDialog("Datei entsperren", data.response);
            }
            if (rootid != -1) {
                window.location.replace('/dateien/#' + rootid);
            }
            else {
                backToProject();
            }
	    });
	} else {
        if (rootid != -1) {
            window.location.replace('/dateien/#' + rootid);
        }
        else {
            backToProject();
        }
	}
}

/**
 * Lädt die Tex Datei in den Editor.
 */
function loadFile() {
	return documentsJsonRequest({
			'command': 'gettext',
			'id': id
		}, function(result, data) {
			if (result) {
			    // setze die rootid, um zur Dateiübersicht zurückgelangen zu können
			    rootid = data.response.rootid;
			    file_name = data.response.filename;

			    // Einstellungen des Editors
                editor = CodeMirror(document.getElementById('codemirror'), {
                mode: "stex",                                // LaTeX Modus
                theme: "default",                            // Standard Theme
                keyMap: "default",                           // Standard Tastaturbelegung
                autofocus: true,                             // automatisch das Textfeld fokussieren
                value: data.response.content,                // Inhalt des Editors setzen
                lineNumbers: true,                           // Zeilennummern anzeigen
                lineWrapping: true,                          // automatischer Zeilenumbruch bei Änderung der Fenstergröße
                matchBrackets: true,                         // zeigt zusammengehörige Klammern an
                autoCloseBrackets: true,                     // automatisches Hinzufügen von schließenden Klammern
                styleActiveLine: true,                       // die ausgewählte Zeile wird farblich markiert
                tabSize: 4,                                  // Tab entspricht 4 Leerzeichen
                extraKeys: {                                 // zusätzliche Tastaturbelegungen
                    "Ctrl-Space": "autocomplete",
                    "Ctrl-S": function() { saveFile(false); },
                    "Ctrl-K": function() {
                        (editor.getOption("autoCloseBrackets")?editor.setOption("autoCloseBrackets", false):
                        editor.setOption("autoCloseBrackets", true));
                        },
                    },
                });

                if (data.response.isallowedit) {
                    compile();
                } else {
                    file_locked = true;
                    disableEditor();
                    if (data.response.lasteditor) {
                        $("#pdfviewer_msg").html('<p class="text-danger"><span class="glyphicon glyphicon-lock"></span> ' + data.response.lasteditor + '</p>');
                    }
                }

                // Editor Event, wenn es Änderungen im Textfeld gibt
                editor.on("change", function () {
                    changesSaved = false;
                    if (autosaveInterval != 0 && !autosaveTimer) {
                        autosaveTimer = setInterval(function() {
                            if (changesSaved) {
                                return;
                            }
                            saveFile(true);
                        }, autosaveInterval);
                    }
                });
                // Editor automatisch an Fenstergröße anpassen
                $(window).bind('resize', function () {
                    setTimeout(function(){editor.refresh();}, editorResizeTimeout);
                });
            } else {
                backToProject();
            }
	    }
	);
}

/**
 * Speichert den Inhalt aus dem Editor in eine Datei.
 * @param autosave boolean, gibt an ob die Autsave Nachricht angezeigt werden soll
 */
function saveFile(autosave) {
    documentsJsonRequest({
            'command': 'updatefile',
            'id': id,
            'content': editor.getValue()
        }, function(result, data) {
            if (result) {
                changesSaved = true;
                if (file_name != data.response.name) {
                    showAlertDialog("Datei speichern",
                                    "Diese Datei wird gerade bearbeitet von:<br>"+
                                    data.response.lasteditor + ".<br>"+
                                    "Die Datei wurde gespeichert als: <br>" +
                                    "<b>"+data.response.name+"</b>");
                    file_locked = true;
                    disableEditor();
                }
                else {
                    if (autosave) {
                        setMsg('Automatisches Speichern...');
                    } else {
                        setMsg('Datei gespeichert');
                    }
                }

            } else {
                if(data.response == ERROR_MESSAGES['FILELOCKED']) {
                    file_locked = true;
                    disableEditor();
                }
                showAlertDialog("Datei speichern", data.response);
            }
    });
}

/*
 * Sperrt die Datei
 */
function lock() {
	documentsJsonRequest({
            'command': 'lockfile',
            'id': id
        }, function(result, data) {
            file_locked = true;
            if (! result) {
                showAlertDialog("Datei sperren", data.response);
            }
	});
}

/*
 * Entsperrt die Datei
 */
function unlock() {
	documentsJsonRequest({
            'command': 'unlockfile',
            'id': id
        }, function(result, data) {
            if (! result) {
                showAlertDialog("Datei entsperren", data.response);
            }
	});
}

function compile() {
    // setze den Inhalt des Log Containers zurück
    setLogText('');

    // Kompiliere nur wenn der Text im Editor nicht leer ist
    if (editor.getValue() != '') {
        // wenn keine Änderung an der tex Datei vorgenommen wurden, kompiliere die tex Datei direkt
        if (changesSaved) {
            compileTex();
        }
        // sonst speichere die tex Datei zunächst und kompiliere danach
        else {
            // speichere die tex Datei
            documentsJsonRequest({
                'command': 'updatefile',
                'id': id,
                'content': editor.getValue()
            }, function(result, data) {
                if (result) {
                    changesSaved = true;
                    setMsg('Datei gespeichert');
                    compileTex();
                }
            })
        }
    }
}


/**
 * Kompiliert eine Datei und zeigt die PDF an.
 */
function compileTex() {
    // Buttons deaktivieren
    disableCompileExportBtn();

    // timer starten, so dass Buttons nach einiger Zeit auf jeden Fall wieder aktiviert werden
    timeout = setTimeout('enableCompileExportBtn()', btnCompileExportTimeout);
    documentsJsonRequest({
            'command': 'compile',
            'id': id,
            'formatid': 0,
            'compilerid': compilerid,
            'forcecompile': (compilerChanged?1:0)
        }, function(result, data) {
            var pdfid = data.response.id;
            var pdf_url = null;

            if (isNaN(pdfid)) {
                pdf_url = "/static/default.pdf";
                setErrorMsg("Fehler beim Kompilierem");
            }
            else {
                // URL der PDF Datei
                // schickt einen GET Request an den Server
                // dieser liefert die PDF Datei, falls vorhanden
                // sonst wird eine default PDF geschickt
                pdf_url = "/documents/?command=getpdf&id=" + pdfid +"&t=" + Math.random();

                if (result) {
                    compilerChanged = false;
                    setMsg("Kompilieren erfolgreich");
                    setLogText('Kompilieren erfolgreich, keine Log Datei vorhanden.');
                }
                else {
                    setErrorMsg("Fehler beim Kompilieren");
                    setCompileLog();
                }
                // timer abbrechen
                clearTimeout(timeout);
                // aktiviere die Buttons wieder
                enableCompileExportBtn();
            }

            // Anzeige der PDF Datei
            renderPDF(pdf_url, document.getElementById('pdf-viewer'));
        }
    );
}

/**
 * Deaktiviert die Kompilier und Export Buttons
 */
function disableCompileExportBtn() {
    document.getElementById("compile").disabled = true;
    document.getElementById("export").disabled = true;
}

/**
 * Aktiviert die Kompilier und Export Buttons
 */
function enableCompileExportBtn() {
    document.getElementById("compile").disabled = false;
    document.getElementById("export").disabled = false;
}

/**
 * Lädt die Log Datei vom LatexCompiler herunter und zeigt diese im Log Bereich an
 */
function setCompileLog() {    
    documentsJsonRequest({
        'command': 'getlog',
        'id': id
    }, function(result, data) { 
        if (result) {
            setLogText(data.response.log.replace(/(\r\n|\n|\r)/gm, "<br>"));
        }
        else {
            setLogText(ERROR_MESSAGES.NOLOGFILE);
        }
    });
    //$("#compile_log").scrollTop($("#compile_log")[0].scrollHeight);
}

/**
 * Kompiliert eine tex Datei und lädt die entsprechende Datei runter.
 * @param id ID der Datei
 */
function exportFile(formatid) {
    // Buttons deaktivieren
    disableCompileExportBtn();
    if (timeout) {
        timeout = clearTimeout(timeout);
    }
    // timer starten, so dass Buttons nach einiger Zeit auf jeden Fall wieder aktiviert werden
    timeout = setTimeout('enableCompileExportBtn()', (formatid==1?btnCompileExportTimeout_HTML:btnCompileExportTimeout));
    documentsJsonRequest({
			'command': 'compile',
			'id': id,
            'formatid': formatid,
            'compilerid': compilerid,
            'forcecompile': (compilerChanged?1:0)
		}, function(result, data) {
			if (result) {
			    compilerChanged = false;
				documentsRedirect({
					'command': 'downloadfile', 
					'id': data.response.id
                });
            } else {
                setErrorMsg('Fehler beim Kompilieren');
                setCompileLog();
            }
            // timer abbrechen
            clearTimeout(timeout);
            // aktiviere die Buttons wieder
            enableCompileExportBtn();
	});
}

/**
 * liest die Tabelle aus und fügt sie in das Textfeld des Editors ein
 */

function table_readout_input() {
    var header = "";
    for (var i = 0; i < hot.countCols(); i++)
        header += "l";

    var fulltable = "";
    for (var j = 0; j < hot.countRows() - 1; j++) {
        var rowcontent = "";
        for (var i = 0; i < hot.countCols(); i++) {
            if (hot.getDataAtCell(j, i) !== null && typeof hot.getDataAtCell(j, i) !== "undefined") {
                rowcontent += hot.getDataAtCell(j, i);
            }
            if (i!=hot.countCols()-1)
            {
                rowcontent+='&';
            }

        }
        rowcontent += "\\\\";
        fulltable += rowcontent + "\n";
    }
    var caption = document.getElementById('table-description').value;
    if (caption == "") {
        editor.replaceSelection("\\begin{table}[h]\n" + "\\begin{tabular}{" + header + "}\n " + fulltable + "\\end{tabular}\n" + "\\end{table}\n", "end");
    } else {
        editor.replaceSelection("\\begin{table}[h]\n" + "\\begin{tabular}{" + header + "}\n " + fulltable + "\\end{tabular}\n" + "\\caption{" + caption + "}\n" + "\\end{table}\n", "end");
    }

    var data = [
        [, , ],
        [, , ],
        [, , ],
    ];
    hot.loadData(data);
    document.getElementById('table-description').value = "";
}

/**
 * liest die Tabelle aus und fügt sie in das Textfeld des Editors ein
 */

function clear_table() {
			var data = [
									[,,],
									[,,],
									[,,],
									];
	hot.loadData(data);
	document.getElementById('table-description').value ="";
}

/**
* Baumstruktur mittels JSTree erstellen
*/
var tree = null;
var projectRootFolderId = (window.top.name).split("/")[0];

function createImageTree() {
	// ausgewählter Knoten
	var selectedNode = null;

    // ID zum vorliegenden Projekt
	var rootFolderId = parseInt(location.hash.substr(1), 10);
	//createJSTree();
	reloadProject();
	function createJSTree(){
		//get folder id
		documentsJsonRequest({
				'command': 'fileinfo',
				'id': rootFolderId,
			}, function(result, data) {
				if (result) {
					rootFolderId = data.response.folderid;
					reloadProject();
				}
		});
	}
	
    function reloadProject() {
        documentsJsonRequest({command: "listfiles", id: projectRootFolderId}, function(result, data) {
            if (! result) {
                alert(ERROR_MESSAGES.PROJECTNOTEXIST);
                return;
            }
            renderProject(data.response);
			$('#graphik-assistent').modal('show');
        });
    }


    // folder: {icon: "glyphicon glyphicon-folder-open"},
    // emptyFolder: {icon: "glyphicon glyphicon-folder-close"},
    // file: {icon: "glyphicon glyphicon-file"},
    // pdf: {icon: "glyphicon glyphicon-book"}

    
    function renderProject(data) {
        var jsTreeData = convertRawDataToJsTreeData(data);

        if (tree) {
            tree.jstree(true).settings.core.data = jsTreeData;
            tree.jstree(true).refresh();
            return;
        }

        tree = $(".fileswrapper").jstree({
            core: {
                check_callback: true,
                multiple: true,
                data: jsTreeData
            },

            plugins: ["types", "dnd", "state"]
        });


        tree.on({
        	// Auswahl-Listener
            "select_node.jstree": function (e, data) {
            	selectedNode = data.node.li_attr;

            },

            // Auswahl-Entfernen-Listener
            "deselect_node.jstree": function (e, data) {
            	selectedNode = null;
            },

	        // Doppelklick-Listener
            "dblclick.jstree": function (e, data) {
            	if (selectedNode['class'].indexOf('filesitem-file') >= 0) {
            		if (selectedNode["data-file-mime"] == "text/x-tex") {
            			// bei Doppelklick auf TEX-Datei zum Editor gehen
            			window.location.replace("/editor/#" + selectedNode["data-file-id"]);
            		}
            	}
            },

	        // Tasten-Listener
            "keydown": function (e, data) {
            },
        });
    }


    var fileTemplate = doT.template($("#template_filesitem-file").text()),
        folderTemplate = doT.template($("#template_filesitem-folder").text());

    function convertRawDataToJsTreeData(rawData) {
        var jsTreeData = [];
		
        $.each(rawData.folders || [], function (i, folder) {
            jsTreeData.push({
                id: "folder" + folder.id,
                text: folderTemplate(folder),
                icon: "glyphicon glyphicon-folder-open",
                li_attr: {"class": "filesitem-folder", "data-folder-id": folder.id, "folder-name": folder.name},
                children: convertRawDataToJsTreeData(folder)
            });
        });

        $.each(rawData.files || [], function (i, file) {
            file.createTime = getRelativeTime(file.createTime);
            file.lastModifiedTime = getRelativeTime(file.lastModifiedTime);
            file.size = Math.round(file.size / 1024); // in KB
			if(file.mimetype.indexOf("image") > -1){
				jsTreeData.push({
                id: "file" + file.id,
                text: fileTemplate(file),
                icon: "glyphicon glyphicon-file",
                li_attr: {"class": "filesitem-file", "data-file-id": file.id, "data-file-mime": file.mimetype}
            });
			}
 
        });

        return jsTreeData;
    }

    /*
     * Gibt das ID des ausgewähltes Verzeichnisses zurück (auch für ausgewählte Dateien)
     */
    function getSelectedFolderId() {
        var selectedNode = getSelectedNode();

        if (selectedNode['class'].indexOf('filesitem-folder') >= 0) {
            var selectedFolder = selectedNode;
        } else {
            selectedFolder = selectedNode.closest(".filesitem-folder");
        }

        return selectedFolder.data("folder-id") || rootFolderId;
    }


    function getSelectedNode() {
        return $("#" + tree.jstree().get_selected());
    }
}

/**
* Einfügen des Dateipfades in die tex Datei
*/
var imageWidth;
function insertImageWithID(fileID, filePath){
	documentsJsonRequest({
			'command': 'fileinfo',
			'id': fileID,
		}, function(result, data) {
			if (result)
			{
				if(data.response.mimetype.indexOf("image") > -1){
					imageWidth = document.getElementById("imageWidth").value;
					if( imageWidth == ""){
						imageWidth = "1.0";
						} else {
						imageWidth = document.getElementById("imageWidth").value;
					}
					
					editor.replaceSelection("\\includegraphics[width="+imageWidth+"\\textwidth]{"+filePath+data.response.filename+"}"+"\n", "end");
				};				
			}
	});

}

/*
 * Deaktiviert den Editor
 */
function disableEditor() {
    // Editor Buttons bis auf "Zurück" deaktivieren
    $("#editorsymbols button:not(#backtofileview)").prop("disabled", true);

    // CodeMirror Hintergrund Farbe auf grau setzen
    $(".CodeMirror").css('background', "#cfcfcf");
    $(".CodeMirror-linenumbers").css('background', "#cfcfcf");
    editor.setOption("readOnly", true);
    editor.setOption("extraKeys", {});
    myLayout.hide("east");
    myLayout.hide("south");
}


/**
* Aufruf durch dialog_grafik_einfuegen
* iteriert durch die im HTML Quellcode aufgebaute JSTree Struktur im 
* fileswrapper div element
*/
function insertGraphics(){
	
	var selectedArray = tree.jstree("get_selected");
	var substringID = null;
	var selectedFile;
	var filePath;
	var currElement;
	
	//für alle selektierten items
	for (var i = 0; i < selectedArray.length; i++) {
		filePath = "";
		selectedFile = selectedArray[i]; //eg. file10
		substringID = selectedFile.substr(4); //eg. 10
		if(isInt(substringID) == true){

			//suche im fileswrapper div nach allen li elementen
			$('#fileswrapper li').each(function(i)
			{
				//wenn die id des elements mit dem selektierten element übereinstimmt
			   if(selectedFile == $(this).attr('id')){
					//setze als aktuelles element, das hierarchisch in der DOM Struktur nächstgelegende ul element
					currElement = $(this).closest("ul");

					//iteriere durch die schleife solange bis das oberste ul element erreicht wurde
					//currElement.closest("li").attr('class') ist in dem fall nicht mehr definiert
					//da es über dem obersten ul element kein li element mehr gibt
					while(true){
					
						if (typeof currElement.closest("li").attr('class') !== 'undefined') {
							//prüfe ob aktuell übergeordnetes li element ein ordner ist
							//wenn ja füge den ordner namen zum dateipfad hinzu
							if(currElement.closest("li").attr('class').indexOf("filesitem-folder") > -1){
								currElement = currElement.closest("li");
								filePath = currElement.attr('folder-name')+ "/" + filePath;
								currElement = currElement.closest("ul");
							}
						} else{
							break;
						}

					}
					for(var x = 0; x < (window.top.name).split("/")[1]; x++){
						filePath = "../"+filePath;
					}
					//wenn die schleife beendet wurde rufe die methode mit der file id auf und dem entsprechenden pfad
					insertImageWithID(substringID, filePath);
			   }
			});
		}
		
	}
	//deselektiere alle items und schließe den dialog
	tree.jstree("deselect_all");
	$( '#dialog_grafik_einfuegen' ).dialog('destroy');
}

function isInt(n) {
    return n % 1 === 0;
}

function setMsg(text) {
    $("#pdfviewer_msg").fadeOut(50);
    $("#pdfviewer_msg").empty();
    $("#pdfviewer_msg").fadeIn(0)
    $("#pdfviewer_msg").html('<p class="text-primary">' + text + '</p>').fadeOut(5000);
}

function setErrorMsg(text) {
    $("#pdfviewer_msg").fadeOut(50);
    $("#pdfviewer_msg").empty();
    $("#pdfviewer_msg").fadeIn(0)
    $("#pdfviewer_msg").html('<p class="text-danger">' + text + '</p>');
}

function setLogText(text) {
    $("#compile_log").empty();
    $("#compile_log").html(text)
}

/**
* Funktion zur Anzeige der PDF Datei mit PDSJS
*/
function renderPDF(url, canvasContainer, options) {

    var pdfscale = 1.5;

    function renderPage(page) {
        var viewport = page.getViewport(pdfscale);
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');

        canvas.style.cssText = 'border:1px solid #000000;';
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        canvas.style.height = '100%';
        canvas.style.width = '100%';

        canvasContainer.appendChild(canvas);

        var renderContext = {
          canvasContext: ctx,
          viewport: viewport
        };

        page.render(renderContext);
    }
    
    function renderPages(pdfDoc) {
        $("#pdf-viewer").html('');
        for(var num = 1; num <= pdfDoc.numPages; num++)
            pdfDoc.getPage(num).then(renderPage);
    }

    //PDFJS.disableWorker = true;
    PDFJS.workerSrc = '/static/pdfjs//build/pdf.worker.js';
    PDFJS.getDocument(url).then(renderPages);
}

/**
* Lädt das Editor Theme mit dem entsprechenden Namen.
* die passende CSS Datei wird dabei automatisch mitgeladen
*/
function loadEditorTheme(theme) {
    // in diesem Ordner befinden sich die CodeMirror Themes
    var cmthemeurl = '/static/codemirror/theme/'

    // Lade die zugehörige css Datei, falls diese noch nicht geladen wurde
    if (!document.getElementById(theme))
    {
        var head  = document.getElementsByTagName('head')[0];
        var link  = document.createElement('link');
        link.id   = theme;
        link.rel  = 'stylesheet';
        link.type = 'text/css';
        link.href = cmthemeurl + theme + ".css";
        link.media = 'all';
        head.appendChild(link);
    }

    // Setze das neue Theme im Editor
    editor.setOption("theme", theme);
}

/**
* Lädt die Editor KeyMap mit dem entsprechenden Namen.
* die passende JS Datei wird dabei automatisch mitgeladen
*/
function loadKeyMap(keymap) {
    // in diesem Ordner befinden sich die CodeMirror KeyMaps
    var cmkeymapurl = '/static/codemirror/keymap/';
    // Lädt die zugehörige js Datei, falls diese noch nicht geladen wurde
    if (!document.getElementById(keymap))
    {
        var head  = document.getElementsByTagName('head')[0];
        var link  = document.createElement('script');
        link.id   = keymap;
        link.type = 'text/javascript';
        link.src = cmkeymapurl + keymap + ".js";
        head.appendChild(link);
    }

    // setze die entsprechende KeyMap im Editor
    if (keymap == 'emacs' || keymap == 'sublime') {
        editor.setOption("keyMap", keymap);
    } else if (keymap == 'vim') {
        editor.setOption("keyMap", keymap);
        editor.setOption("vimMode", true);
    }
}

function setFontSize(fontsize, refresh) {
    $(".CodeMirror").css('font-size', fontsize + "pt");
    if (refresh) {
        editor.refresh();
    }
}

function setFontFamily(fontfamily, refresh) {
    $(".CodeMirror").css('font-family', fontfamily);
    if (refresh) {
        editor.refresh();
    }
}
