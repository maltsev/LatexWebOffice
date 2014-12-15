﻿/*
@author: Timo Dümke
@creation: 12.12.2014 - sprint-nr: 3
@last-change: 12.12.2014 - sprint-nr: 3
*/
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
	filelistHandler.addData({'name':response.files[i].name,'foldername':response.name},false);
}
}
// Höhere Rekursionsebene - beinhaltet den aktuellen Pfad
else {
// Gibt die Dateien des Ordners der höheren Rekursionsebene aus
for (var i = 0; i < number_of_files; i++){
	filelistHandler.addData({'name':response.files[i].name,'foldername':response.name},path,false);
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
path.push(sumOfFiles); // Fügt die Summe der Dateien zum Pfad hinzu
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
path.push(sumOfFiles);
}
}
// Gibt die Dateien des Ordners aus
for (var i = 0; i < response.folders[a].files.length; i++){
	filelistHandler.addData({'name':response.folders[a].files[i].name,'foldername':response.folders[a].name},path,false);
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






/**
 * Leitet den Benutzer zurück zur Projektverwaltung.
 */
function backToProject() {
	// TODO: auf das richtige Projekt verweisen?
	window.location.replace('/projekt/');
}

