/*
@author: Timo Dümke, Ingolf Bracht, Kirill Maltsev
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 15.01.2015 - sprint-nr: 4
*/
$(function () {
    // ID des vorliegenden Projektes
	var projectId = parseInt(location.hash.substr(1), 10);
	if (! projectId) {
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
        documentsJsonRequest({command: "listfiles", id: projectId}, function(result, data) {
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

            },

	        // Doppelklick-Listener
            "dblclick.jstree": function (e, data) {

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
                li_attr: {"class": "filesitem-file", "data-file-id": file.id}
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
        var basic;
        // flag für die Aktivierung der selektionsabhängigen Schaltflächen
        var remain;

        // Editierungsmodus
        if(creatingNodeID!=null) {
            // keine Aktivierungen
            basic  = false;
            remain = false;
        }
        // Selektion
        else if(selectedNodeID!="") {
            // vollständig Aktivierung
            basic  = true;
            remain = true;
        }
        else {
            // Aktivierung der nicht-selektionsabhängigen Schaltflächen
            basic  = true;
            remain = false;
        }

        // setzt die Aktivierungen der einzelnen Menü-Schaltflächen
        $(".filestoolbar-open").prop("disabled", !remain);
        $(".filestoolbar-new").prop("disabled", !basic);
        $(".filestoolbar-delete").prop("disabled", !remain);
        $(".filestoolbar-rename").prop("disabled", !remain);
        $(".filestoolbar-move").prop("disabled", !remain);
        $(".filestoolbar-download").prop("disabled", !remain);
        $(".filestoolbar-upload").prop("disabled", !basic);
    }
});