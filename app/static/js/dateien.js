/*
@author: Timo Dümke, Ingolf Bracht, Kirill Maltsev
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 15.01.2015 - sprint-nr: 4
*/
$(function () {
	// ausgewählter Knoten
	var selectedNode = null;

	// ob der ausgewählte Knoten eine Datei ist
	var selectedIsFile;

    // ID zum vorliegenden Projekt
	var rootFolderId = parseInt(location.hash.substr(1), 10);
	if (!rootFolderId) {
	    backToProject();
	    return;
	}

    reloadProject();


	// -------------------------------------------------------------------------
	//                              MENÜ-EINTRÄGE
	// -------------------------------------------------------------------------

    // "Öffnen"-Schaltfläche
	$(".filestoolbar-open").click(function() {

	});

	// "Erstellen"-Schaltfläche
	$(".filestoolbar-new").click(function() {

	});

	// "Löschen"-Schaltfläche
	$(".filestoolbar-delete").click(function() {

	});

	// "Umbenennen"-Schaltfläche
	$(".filestoolbar-rename").click(function() {

	});

	// "Verschieben"-Schaltfläche
	$(".filestoolbar-move").click(function() {

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
            	selectedIsFile = selectedNode.class.indexOf("filesitem-file") >= 0;
            	updateMenuButtons();
            },

            // Auswahl-Entfernen-Listener
            "deselect_node.jstree": function (e, data) {
            	selectedNode = null;
            	updateMenuButtons();
            },

	        // Doppelklick-Listener
            "dblclick.jstree": function (e, data) {
            	if (selectedNode.class.indexOf("filesitem-file") >= 0) {
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




    function convertRawDataToJsTreeData(rawData) {
        var jsTreeData = [];

        $.each(rawData.folders || [], function (i, folder) {
            jsTreeData.push({
                id: "folder" + folder.id,
                text: folder.name,
                icon: "glyphicon glyphicon-folder-open",
                li_attr: {"class": "filesitem-folder", "data-folder-id": folder.id},
                children: convertRawDataToJsTreeData(folder)
            });
        });

        $.each(rawData.files || [], function (i, file) {
            jsTreeData.push({
                id: "file" + file.id,
                text: file.name,
                icon: "glyphicon glyphicon-file",
                li_attr: {"class": "filesitem-file", "data-file-id": file.id, "data-file-mime": file.mimetype}
            });
        });

        return jsTreeData;
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
        var file = selectedNode != null && selectedIsFile;
        var folder = selectedNode != null && !selectedIsFile;

        // setzt die Aktivierungen der einzelnen Menü-Schaltflächen
        $(".filestoolbar-open").prop("disabled", !file);
        $(".filestoolbar-new").prop("disabled", !basic);
        $(".filestoolbar-delete").prop("disabled", !(file || folder));
        $(".filestoolbar-rename").prop("disabled", !(file || folder));
        $(".filestoolbar-move").prop("disabled", !(file || folder));
        $(".filestoolbar-download").prop("disabled", !(file || folder));
        $(".filestoolbar-upload").prop("disabled", !basic);
    }
});