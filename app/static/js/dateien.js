/*
@author: Timo Dümke
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 12.12.2014 - sprint-nr: 3
*/
var root_empty = "empty<>";
var filelistHandler;
$( document ).ready(function() {
// ID aus URL ermitteln
	id = parseInt(location.hash.substr(1));
	if (isNaN(id)){
		backToProject();
		}
	else {
filelistHandler = new ListSelector("dateien");
filelistHandler.setCaptions([
{'name': 'Ordner', 'element': 'foldername'},
{'name': 'Name', 'element': 'name'},
{'name': 'Dateityp', 'element': 'filetype'}
]);

	showFilelist(id);
}

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
			}
			else {
			// vorhandene Dateiliste entfernen
			filelistHandler.clearData();
			// Ruft die Dateiliste über eine rekursive Funktion auf
			recursiveFileAnalysis(data.response,0,'0',null,false);
			
			
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
	filelistHandler.addData({'name':'','foldername':response.name,'folderid':response.id,'fileid':response.files[i].id},false);
	}
	else if (response.files[i].name != root_empty){ // ansonsten der Dateiname
	filelistHandler.addData({'name':response.files[i].name,'foldername':response.name,'folderid':response.id,'fileid':response.files[i].id},false);
	}
}
}
// Höhere Rekursionsebene - beinhaltet den aktuellen Pfad
else {
// Gibt die Dateien des Ordners der höheren Rekursionsebene aus
for (var i = 0; i < number_of_files; i++){
	if (response.files[i].name == root_empty && number_of_files == 1){ // Wenn es keine Datei im Ordner gibt, wird ein leerer Ordner angezeigt
		filelistHandler.addData({'name':'','foldername':response.name,'folderid':response.id,'fileid':response.files[i].id},path,false);
	}
	else if(response.files[i].name != root_empty){ // ansonsten der Dateiname
		filelistHandler.addData({'name':response.files[i].name,'foldername':response.name,'folderid':response.id,'fileid':response.files[i].id},path,false);
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
if (sumOfFiles == 0){
// Wenn es keine Ordner über dem aktuellen gibt
if (response.folders[a].files.length != 0){ 
sumOfFiles =parent.files.length; // ermittelt die Anzahl der Dateien vom parent Ordner
}
}
// Wenn es mehr als eine Datei im untersten Ordner gibt
if (response.files.length > 1){
sumOfFiles += response.files.length-1; // setze Anzahl der Dateien auf die Anzahl der Dateien-1
}
path.push(sumOfFiles-1); // Fügt die Summe der Dateien zum Pfad hinzu
recursiveFileAnalysis(response.folders[a],level+1,path,response); // Rekursionsaufruf
}
// Wenn es keine Unterordner gibt, also in der Baumstruktur ein Blatt ist
else {
// repräsentiert die Summe der Dateien, die bisher in der Rekursion abgearbeitet wurde.
var sumOfFiles = 0;
// siehe oben
for (var c=0;c<parent.folders.length;c++){
if (parent.folders[c] === response){
break;
}
sumOfFiles += parent.folders[c].files.length;
}
// Wenn es mehr als eine Datei im untersten Ordner gibt
if (response.files.length > 1){
sumOfFiles += response.files.length-1; // setze Anzahl der Dateien auf die Anzahl der Dateien-1
}
// Wenn es mehr als einen Unterordner gibt, also mehrere Unterordner Blätter sind
if (response.folders.length > 1){ // es gibt mehr als einen Unterordner
// Pfad wird nur beim ersten Element ergänzt
if (a == 0){
path.push(sumOfFiles-1);
}
}
// Gibt die Dateien des Ordners aus
for (var i = 0; i < response.folders[a].files.length; i++){
	if (response.folders[a].files[i].name == root_empty && number_of_files == 1){ // Wenn es keine Datei im Ordner gibt, wird ein leerer Ordner angezeigt
		filelistHandler.addData({'name':'','foldername':response.folders[a].name,'folderid':response.folders[a].id,'fileid':response.folders[a].files[i].id},path,false);
	}
	else if (response.folders[a].files[i].name != root_empty){ // ansonsten der Dateiname
		filelistHandler.addData({'name':response.folders[a].files[i].name,'foldername':response.folders[a].name,'folderid':response.folders[a].id,'fileid':response.folders[a].files[i].id},path,false);
	}
}
}
}
else { // Rekursiver Aufruf, wenn die Rekursionsebene 0 ist, also der erste Aufruf.
	recursiveFileAnalysis(response.folders[a],level+1,[(number_of_files-1)-1],response); // Rekursionsaufruf
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
   $( "#dialog_datei_neuer_name" ).dialog();
   document.getElementById('file_name').value = getFileName();
  }
   if (category == "new_name_folder"){
   $( "#dialog_ordner_neuer_name" ).dialog();
    document.getElementById('folder_name').value = getFolderName();
  }
  });
}

function checkRemoveFile(id,type){
var r = confirm("Möchten Sie die Datei "+getFileName()+" wirklich löschen?");
if (r == true) {
    removeFolderAndFiles(id,type);
} else {
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

