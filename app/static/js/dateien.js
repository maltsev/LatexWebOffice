/*
@author: Timo Dümke, Ingolf Bracht, Kirill Maltsev
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 15.01.2015 - sprint-nr: 4
*/
$(function () {
	// ausgewählter Knoten
	var selectedNode = null;

    // ID zum vorliegenden Projekt
	var rootFolderId = parseInt(location.hash.substr(1), 10);
	if (! rootFolderId) {
	    backToProject();
	    return;
	}

    reloadProject();


	// -------------------------------------------------------------------------
	//                              MENÜ-EINTRÄGE
	// -------------------------------------------------------------------------

    // "Öffnen"-Schaltfläche
	$(".filestoolbar-open").click(function() {
		window.location.replace("/editor/#" + selectedNode["data-file-id"]);
	});

	// "Datei Erstellen"-Schaltfläche
	$(".filestoolbar-newfile").click(function() {
        var name = prompt("Geben Sie den Tex-Dateiname ein:");
        if (! name) {
            return;
        }

        // Vermeiden "filename.tex.tex" Namen
        name = name.replace(/\.tex/i, "") + ".tex";

        var selectedFolderId = getSelectedFolderId();

        documentsJsonRequest({command: "createtex", id: selectedFolderId, name: name}, function(result, data) {
            if (! result) {
                alert(data.response);
                return;
            }

            reloadProject();
        });
	});

	// "Verzeichnis Erstellen"-Schaltfläche
	$(".filestoolbar-newfolder").click(function() {
        var name = prompt("Geben Sie den Verzeichnisname ein:");
        if (! name) {
            return;
        }

        var selectedFolderId = getSelectedFolderId();

        documentsJsonRequest({command: "createdir", id: selectedFolderId, name: name}, function(result, data) {
            if (! result) {
                alert(data.response);
                return;
            }

            reloadProject();
        });
	});

	// "Löschen"-Schaltfläche
	$(".filestoolbar-delete").click(function() {
		if (confirm('Wollen Sie die Auswahl wirklich löschen?')) {
			if (selectedNode['class'].indexOf('filesitem-file') >= 0) {
				documentsJsonRequest({
					'command': 'deletefile',
					'id': selectedNode['data-file-id']
				}, function(result, data) {
					if (result)
						reloadProject();
				});
			} else if (selectedNode['class'].indexOf('filesitem-folder') >= 0) {
				documentsJsonRequest({
					'command': 'rmdir',
					'id': selectedNode['data-folder-id']
				}, function(result, data) {
					if (result)
						reloadProject();
				});
			}
		}
	});

	// "Umbenennen"-Schaltfläche
	$(".filestoolbar-rename").click(function() {
        var newName = prompt("Geben Sie den neuen Name ein:");
        if (! newName) {
            return;
        }

        var selectedNode = getSelectedNode(),
            commandName = selectedNode['class'].indexOf('filesitem-folder') >= 0 ? "renamedir" : "renamefile",
            itemId = selectedNode.data("file-id") || selectedNode.data("folder-id");

        documentsJsonRequest({command: commandName, id: itemId, name: newName}, function(result, data) {
            if (! result) {
                alert(data.response);
                return;
            }

            $(".filesitem-nameWrapper", selectedNode).text(newName);
        });
	});

	// "Herunterladen"-Schaltfläche
	$(".filestoolbar-download").click(function() {

	});

	// "Hochladen"-Schaltfläche
	$(".filestoolbar-upload").click(function() {

	});



    function reloadProject() {
        documentsJsonRequest({command: "listfiles", id: rootFolderId}, function(result, data) {
            if (! result) {
                alert(ERROR_MESSAGES.PROJECTNOTEXIST);
                return;
            }

            renderProject(data.response);
        });
    }


    // folder: {icon: "glyphicon glyphicon-folder-open"},
    // emptyFolder: {icon: "glyphicon glyphicon-folder-close"},
    // file: {icon: "glyphicon glyphicon-file"},
    // pdf: {icon: "glyphicon glyphicon-book"}

    var tree = null;
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
                multiple: false,
                data: jsTreeData
            },

            plugins: ["types", "dnd", "state"]
        });


        tree.on({
        	// Auswahl-Listener
            "select_node.jstree": function (e, data) {
            	selectedNode = data.node.li_attr;
            	updateMenuButtons();
            },

            // Auswahl-Entfernen-Listener
            "deselect_node.jstree": function (e, data) {
            	selectedNode = null;
            	updateMenuButtons();
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
                li_attr: {"class": "filesitem-folder", "data-folder-id": folder.id},
                children: convertRawDataToJsTreeData(folder)
            });
        });

        $.each(rawData.files || [], function (i, file) {
            file.createTime = getRelativeTime(file.createTime);
            file.lastModifiedTime = getRelativeTime(file.lastModifiedTime);
            file.size = Math.round(file.size / 1024); // in KB

            jsTreeData.push({
                id: "file" + file.id,
                text: fileTemplate(file),
                icon: "glyphicon glyphicon-file",
                li_attr: {"class": "filesitem-file", "data-file-id": file.id, "data-file-mime": file.mimetype}
            });
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


    /*
     * Leitet den Benutzer zurück zur Projektverwaltung.
     */
    function backToProject() {
        // TODO: auf das richtige Projekt verweisen?
        window.location.replace("/projekt/");
    }

    /*
     * Aktualisiert die Aktivierungen der Menü-Schaltflächen.
     */
    function updateMenuButtons() {
        // flag für die Aktivierung der nicht-selektionsabhängigen Schaltflächen ("Erstellen" und "Hochladen")
        var basic = true;

        // flag für die Aktivierung der selektionsabhängigen Schaltflächen
        var selected = selectedNode != null;
        var folder = selected && selectedNode['class'].indexOf('filesitem-folder') >= 0;
        var file = selected && selectedNode['class'].indexOf('filesitem-file') >= 0;
        var texFile = file && selectedNode["data-file-mime"] == "text/x-tex";

        // setzt die Aktivierungen der einzelnen Menü-Schaltflächen
        $(".filestoolbar-open").prop("disabled", !texFile);
        $(".filestoolbar-new").prop("disabled", !basic);
        $(".filestoolbar-delete").prop("disabled", !selected);
        $(".filestoolbar-rename").prop("disabled", !selected);
        $(".filestoolbar-move").prop("disabled", !selected);
        $(".filestoolbar-download").prop("disabled", !selected);
        $(".filestoolbar-upload").prop("disabled", !basic);
    }
});