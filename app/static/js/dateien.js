/*
@author: Timo Dümke
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 18.12.2014 - sprint-nr: 3
*/

var id;
var root_empty = "empty<>";
var filelistHandler;
$( document ).ready(function() {
	// ID aus URL ermitteln
	id = parseInt(location.hash.substr(1));
	if (isNaN(id)){
		backToProject();
	} else {
		filelistHandler = new ListSelector("dateien");
		filelistHandler.setCaptions([
			{'name': 'Ordner', 'element': 'foldername'},
			{'name': 'Name', 'element': 'name'},
			{'name': 'Dateityp', 'element': 'filetype'}
		]);
	
		showFilelist(id);
	}

	// Herunterladen von Dateien
	$('#download').attr('href', '#' + id);
	$('#download').click(function() {
		if (filelistHandler.getSelected() != null)
			downloadFile(getFileId());
		else
			$('#dialog_keine_auswahl').dialog();
	});

	/*
	* Fängt Doppelklicks auf eine Datei/einen Ordner ab.
	*/
	filelistHandler.setDClickHandler(openEditor);
});




function showFilelist(projectID){
//alert(projectID);
jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'listfiles',
			'id': projectID
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			//Anfrage Fehlerhaft
			console.log({
				'error': 'Fehlerhafte Anfrage: Fehler beim Abrufen der Dateiliste',
				'details': errorThrown,
				'id': projectID,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success'){
				// Fehler auf dem Server
				console.log({
					'error': 'Fehlerhafte Rückmeldung: Fehler beim Abrufen der Dateiliste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
				if (data.response == "Dieses Verzeichnis existiert nicht"){
					showPopup("no_folder");
				}
			}
			else {
			// vorhandene Dateiliste entfernen
			filelistHandler.clearData();
			// Ruft die Dateiliste über eine rekursive Funktion auf
			recursiveFileAnalysis(data.response,0,'0',null,false);
			console.log(data.response);
			
		}
		}
	});
}
/**
* Die Funktion ruft die Ordnerstruktur (Baumstruktur) der Dateien rekursiv auf und 
* stellt diese in einer Tabelle da.
* Durch die Datei root_empty werden alle Indizes um 1 verringert. (also path.push() und recursiveFileAnalysis() Aufrufe)
* response - Ordnerarray
* level - aktuelle Rekursionsebene
* path - bestehender Pfad zur Vertiefung der Rekursion
* parent - Ebene über dem Array von Response
*/
function recursiveFileAnalysis(response,level,path,parent){
// ermittelt vom aktuellen Response die Anzahl der Dateien.
var number_of_files = response.files.length;

// Erster Aufruf der Rekursion (Rekursionsebene 0)
if (level == 0){
// Gibt die Liste der Dateien aus.
for (var i = 0; i < number_of_files; i++){
	if (response.files[i].name == root_empty && number_of_files == 1){ // Wenn es keine Datei im Ordner gibt, wird ein leerer Ordner angezeigt
	filelistHandler.addData({'name':'','foldername':'Root','folderid':response.id,'fileid':response.files[i].id,'filetype':response.files[i].mimetype},false);
	}
	else if (response.files[i].name != root_empty){ // ansonsten der Dateiname
	filelistHandler.addData({'name':response.files[i].name,'foldername':'Root','folderid':response.id,'fileid':response.files[i].id,'filetype':response.files[i].mimetype},false);
	}
}
}
// Höhere Rekursionsebene - beinhaltet den aktuellen Pfad
else {
// Gibt die Dateien des Ordners der höheren Rekursionsebene aus
for (var i = 0; i < number_of_files; i++){
	if (response.files[i].name == root_empty && number_of_files == 1){ // Wenn es keine Datei im Ordner gibt, wird ein leerer Ordner angezeigt
		filelistHandler.addData({'name':'','foldername':response.name,'folderid':response.id,'fileid':response.files[i].id,'filetype':response.files[i].mimetype},path,false);
	}
	else if(response.files[i].name != root_empty){ // ansonsten der Dateiname
		filelistHandler.addData({'name':response.files[i].name,'foldername':response.name,'folderid':response.id,'fileid':response.files[i].id,'filetype':response.files[i].mimetype},path,false);
	}
	}
}
// Prüft, ob das aktuelle Array ein Array mit Unterordnern beinhaltet
if (response.folders.length != 0){ // es gibt Unterordner
// Durchläuft alle Unterordner vom aktuellen Ordner
for (var a=0;a < response.folders.length; a++){
if (level >  0){ // Wenn die Rekursionsebene nicht die Anfangsebene ist
// Prüfe,ob es weitere Unterordner vom aktuellen Unterordner gibt.
if (response.folders[a].folders.length != 0){  // es gibt weitere Unterordner
// repräsentiert die Summe der Dateien, die bisher in der Rekursion abgearbeitet wurde.
var sumOfFiles = 0;
// Summiert die Dateien solange auf (Summe der Dateien der Unterordner vom parent Ordner), bis der aktuelle Ordner erreicht ist.
for (var c=0;c<parent.folders.length;c++){ // durchläuft alle Unterordner von Parent
if (parent.folders[c] === response){ // Wenn ein Unterordner der aktuelle Ordner ist, brich ab
break; // Abbruch der Schleife
}
sumOfFiles += parent.folders[c].files.length; // Summiert die Anzahl der Dateien aus den Unterordnern vom parent Ordner auf.
}
// Wenn die Summe der Dateien 0 ist
if (sumOfFiles == 1){
// Wenn es keine Ordner über dem aktuellen gibt
if (response.folders[a].files.length > 1){ 
sumOfFiles =parent.files.length; // ermittelt die Anzahl der Dateien vom parent Ordner
}
}
// Wenn es mehr als eine Datei im untersten Ordner gibt
if (response.files.length > 2){
sumOfFiles += response.files.length-1; // setze Anzahl der Dateien auf die Anzahl der Dateien-1
}
path.push(sumOfFiles-1); // Fügt die Summe der Dateien zum Pfad hinzu
recursiveFileAnalysis(response.folders[a],level+1,path,response); // Rekursionsaufruf
}
// Wenn es keine Unterordner gibt, also in der Baumstruktur ein Blatt ist
else {
console.log("Dubbidai");
// repräsentiert die Summe der Dateien, die bisher in der Rekursion abgearbeitet wurde.
var sumOfFiles = 0;
// siehe oben
// Wenn es mehr als eine Datei im untersten Ordner gibt
if (response.files.length > 2){
sumOfFiles += response.files.length-1; // setze Anzahl der Dateien auf die Anzahl der Dateien-1
}
// Wenn es mehr als einen Unterordner gibt, also mehrere Unterordner Blätter sind
if (response.folders.length > 1){ // es gibt mehr als einen Unterordner
// Pfad wird nur beim ersten Element ergänzt
if (a == 0){
// Summiert die Dateien solange auf (Summe der Dateien der Unterordner vom parent Ordner), bis der aktuelle Ordner erreicht ist.
for (var c=0;c<parent.folders.length;c++){ // durchläuft alle Unterordner von Parent
if (parent.folders[c] === response){ // Wenn ein Unterordner der aktuelle Ordner ist, brich ab
break; // Abbruch der Schleife
}
sumOfFiles += parent.folders[c].files.length; // Summiert die Anzahl der Dateien aus den Unterordnern vom parent Ordner auf.
}
path.push(sumOfFiles);
}
}
else {
// Summiert die Dateien solange auf (Summe der Dateien der Unterordner vom parent Ordner), bis der aktuelle Ordner erreicht ist.
for (var c=0;c<parent.folders.length;c++){ // durchläuft alle Unterordner von Parent
if (parent.folders[c] === response){ // Wenn ein Unterordner der aktuelle Ordner ist, brich ab
break; // Abbruch der Schleife
}
sumOfFiles += parent.folders[c].files.length; // Summiert die Anzahl der Dateien aus den Unterordnern vom parent Ordner auf.
}
path.push(sumOfFiles);
console.log("only one subfolder");
}
// Gibt die Dateien des Ordners aus
for (var i = 0; i < response.folders[a].files.length; i++){
	if (response.folders[a].files[i].name == root_empty && number_of_files == 1){ // Wenn es keine Datei im Ordner gibt, wird ein leerer Ordner angezeigt
		filelistHandler.addData({'name':'','foldername':response.folders[a].name,'folderid':response.folders[a].id,'fileid':response.folders[a].files[i].id,'filetype':response.folders[a].files[i].mimetype},path,false);
	}
	else if (response.folders[a].files[i].name != root_empty){ // ansonsten der Dateiname
		filelistHandler.addData({'name':response.folders[a].files[i].name,'foldername':response.folders[a].name,'folderid':response.folders[a].id,'fileid':response.folders[a].files[i].id,'filetype':response.folders[a].files[i].mimetype},path,false);
	}
}
}
}
else { // Rekursiver Aufruf, wenn die Rekursionsebene 0 ist, also der erste Aufruf.
	recursiveFileAnalysis(response.folders[a],level+1,[(number_of_files-1)],response); // Rekursionsaufruf
}
}
}
}

function getPath(number){
var path = "[";
for (var c=0;c<number;c++){
if (c> 0){
path += ",";
}
path += "0";
}
path += "]";
return path;
}

function getFolderId(){
var array = filelistHandler.getSelected();
return array["folderid"];
}

function getFolderName(){
var array = filelistHandler.getSelected();
return array["foldername"];
}

function getFileId(){
var array = filelistHandler.getSelected();
return array["fileid"];
}

function getFileName(){
var array = filelistHandler.getSelected();
return array["name"];
}

function removePopup(category){
  $(function() {
  if (category == "remove"){
    $( "#dialog_datei_ordner_loeschen" ).dialog("destroy");
  }
  if (category == "rename"){
      $( "#dialog_datei_ordner_umbenennen" ).dialog("destroy");
  }
  });
}

function checkSelection(){
if (filelistHandler.getSelected() == null){
showPopup("no_selection");
return false;
}
else {
return true;
}
}

function showPopup(category){
  $(function() {
  
  if (category == "folder_exists"){
		$( "#dialog_ordner_existiert" ).dialog();
  }
  if (category == "file_exists"){
		$( "#dialog_datei_existiert" ).dialog();
  }
  if (category == "empty_input"){
		$( "#dialog_leere_eingabe" ).dialog();
  }
  if (category == "illegal_sign"){
		$( "#dialog_ungueltige_eingabe" ).dialog();
  }
  if (category == "no_rights_delete"){
		$( "#dialog_keine_rechte_loeschen" ).dialog();
   }
   if (category == "no_folder"){
		$( "#dialog_ordner_existiert_nicht" ).dialog();
   }
   if (category == "no_selection"){
		$( "#dialog_keine_auswahl" ).dialog();
   }
  if (category == "remove"){
  if (checkSelection()){
    $( "#dialog_datei_ordner_loeschen" ).dialog();
	}
  }
  if (category == "rename"){
  if (checkSelection()){
      $( "#dialog_datei_ordner_umbenennen" ).dialog();
	  }
  }
  if (category == "new_name_file"){
  if (getFileName() != ""){
   $( "#dialog_datei_neuer_name" ).dialog();
   }
   else {
   	$( "#dialog_datei_existiert_nicht" ).dialog();
   }
   document.getElementById('file_name').value = getFileName();
  }
   if (category == "new_name_folder"){
   $( "#dialog_ordner_neuer_name" ).dialog();
    document.getElementById('folder_name').value = getFolderName();
  }
  });
}

function checkRemoveFile(id,type){
if (getFileName() != ""){
var r = confirm("Möchten Sie die Datei "+getFileName()+" wirklich löschen?");
if (r == true) {
    removeFolderAndFiles(id,type);
}
 else {
}
}
else {
   	$( "#dialog_datei_existiert_nicht" ).dialog();
}
}

function checkRemoveFolder(id,type){
var r = confirm("Möchten Sie den Ordner "+getFolderName()+" wirklich löschen?");
if (r == true) {
    removeFolderAndFiles(id,type);
} else {
}
}

/**
 * Lädt eine Datei herunter.
 * @param id ID der Datei
 */
function downloadFile(id) {
	documentsRedirect({
		'command': 'downloadfile',
		'id': id
	});
}

/**
 * Löscht den ausgewählten Ordner/die Datei
 * @param id - ID der Datei/des Ordners aus der Datenbank
 * @param type - "file" oder "folder", ist es eine Datei oder ein Ordner
 */
function removeFolderAndFiles(id,type) {
if (type == "folder"){
jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'rmdir',
			'id': id
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			//Anfrage Fehlerhaft
			console.log({
				'error': 'Fehlerhafte Anfrage: Fehler beim Abrufen der Dateiliste',
				'details': errorThrown,
				'id': projectID,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success'){
				// Fehler auf dem Server
				console.log({
					'error': 'Fehlerhafte Rückmeldung: Fehler beim Abrufen der Dateiliste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			/**
			* Fehlermeldungen anzeigen
			*/
			if (data.response == "Nutzer hat für diese Aktion nicht ausreichend Rechte"){
				showPopup("no_rights_delete");
			}
			}
			else {
			// Seite neu laden
			location.reload();
			
			
		}
		}
	});
}
if (type == "file"){
jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'deletefile',
			'id': id
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			//Anfrage Fehlerhaft
			console.log({
				'error': 'Fehlerhafte Anfrage: Fehler beim Abrufen der Dateiliste',
				'details': errorThrown,
				'id': projectID,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success'){
				// Fehler auf dem Server
				console.log({
					'error': 'Fehlerhafte Rückmeldung: Fehler beim Abrufen der Dateiliste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
			}
			else {
			// Seite neu laden
			location.reload();
			
			
		}
		}
	});

}
}

/**
 * Nennt den ausgewählten Ordner/die Datei um
 * @param id - ID der Datei/des Ordners aus der Datenbank
 * @param type - "file" oder "folder", ist es eine Datei oder ein Ordner
 */
function renameFolderAndFiles(id,type,newname) {
if (type == "folder"){
jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'renamedir',
			'id': id,
			'name': document.getElementById('folder_name').value
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			//Anfrage Fehlerhaft
			console.log({
				'error': 'Fehlerhafte Anfrage: Fehler beim Abrufen der Dateiliste',
				'details': errorThrown,
				'id': projectID,
				'statusCode': response.status,
				'statusText': response.statusText
			});
			/**
			* Fehlermeldungen anzeigen
			*/
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success'){
				// Fehler auf dem Server
				console.log({
					'error': 'Fehlerhafte Rückmeldung: Fehler beim Abrufen der Dateiliste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
				if (data.response == "Unerlaubtes Zeichen verwendet"){
					showPopup("illegal_sign");
				}
				else if (data.response == "Leere Namen sind nicht erlaubt"){
					showPopup("empty_input");
				}
				else if (data.response == "Dieses Verzeichnis existiert schon"){
					showPopup("folder_exists");
				}
			}
			else {
			// Seite neu laden
			location.reload();
			
			
		}
		}
	});
}
if (type == "file"){
jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': {
			'command': 'renamefile',
			'id': id,
			'name': document.getElementById('file_name').value
		},
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			//Anfrage Fehlerhaft
			console.log({
				'error': 'Fehlerhafte Anfrage: Fehler beim Abrufen der Dateiliste',
				'details': errorThrown,
				'id': projectID,
				'statusCode': response.status,
				'statusText': response.statusText
			});
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success'){
				// Fehler auf dem Server
				console.log({
					'error': 'Fehlerhafte Rückmeldung: Fehler beim Abrufen der Dateiliste',
					'details': data.response,
					'statusCode': response.status,
					'statusText': response.statusText
				});
				if (data.response == "Unerlaubtes Zeichen verwendet"){
					showPopup("illegal_sign");
				}
				else if (data.response == "Leere Namen sind nicht erlaubt"){
					showPopup("empty_input");
				}
				else if (data.response == "Diese Datei existiert schon"){
					showPopup("file_exists");
				}
			}
			else {
			// Seite neu laden
			location.reload();
			
			
		}
		}
	});

}
}

/**
 * Leitet den Benutzer zurück zur Projektverwaltung.
 */
function backToProject() {
	// TODO: auf das richtige Projekt verweisen?
	window.location.replace('/projekt/');
}

/**
 * Öffnet die Datei im Editor.
 * @param fileid - ID der Datei
 * @param filename - Name der Datei
 */
function openEditor() {
var fileid = "";
var filename = "";
try{
fileid = getFileId();
filename = getFileName();
}
catch(err){

}
	if (filename != ""){
	document.location.assign('/editor/#' + fileid);
	}
}

