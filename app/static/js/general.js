/*
@author: Thore Thießen
@creation: 01.12.2014 - sprint-nr: 2
@last-change: 18.12.2014 - sprint-nr: 3
*/

/**
 * Gibt eine Dateigröße in Bytes in für Menschen besser lesbaren Format aus.
 * @param bytes Dateigröße in Bytes
 * @return String mit der Größenangabe
 */
function prettySize(bytes) {
	var units = ['B', 'KB', 'MB', 'GB', 'TB'];
	for (i = 0; bytes > 1000 && i < units.length; ++i)
		bytes = Math.floor(bytes / 1000);
	return('' + bytes + units[i]);
}

/**
 * Setzt eine AJAX-Anfrage für eine JSON-Antwort an /documents/ ab.
 * @param param Paramter für die Anfrage (command, id, …)
 * @param handler Handler für die Antwort als function(bool result, object data)
 */
function documentsJsonRequest(param, handler) {
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': param,
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'json',
		'error': function(response, textStatus, errorThrown) {
			// Fehler bei der Anfrage
			var result = {
				'status': 'failure',
				'response': errorThrown + ': ' + response.status + '; ' + response.statusText
			};
			console.log(result);
			handler(false, result);
		},
		'success': function(data, textStatus, response) {
			if (data.status != 'success') {
				// Server-seitiger Fehler
				console.log(data);
				handler(false, data);
			} else
				handler(true, data);
		}
	});
}

/**
 * Setzt eine AJAX-Anfrage für eine Binär-Antwort an /documents/ ab.
 * @param param Paramter für die Anfrage (command, id, …)
 * @param handler Handler für die Antwort als function(bool result, data)
 */
function documentsDataRequest(param, handler) {
	jQuery.ajax('/documents/', {
		'type': 'POST',
		'data': param,
		'headers': {
			'X-CSRFToken': $.cookie('csrftoken')
		},
		'dataType': 'text',
		'error': function(response, textStatus, errorThrown) {
			// Fehler bei der Anfrage
			console.log({
				'status': 'failure',
				'response': errorThrown + ': ' + response.status + '; ' + response.statusText
			});
			handler(false, null);
		},
		'success': function(data, textStatus, response) {
			handler(true, data);
		}
	});
}

/**
 * Leitet den Benutzer auf /documents/ weiter, wobei zusätzlich POST-Daten gesendet werden.
 * @param param Paramter für die Anfrage (command, id, …)
 */
function documentsRedirect(param) {
	var form = $('<form></form>').attr('action',  '/documents/').attr('method', 'post');
	$('body').append(form);

	// CSRF Token
	form.append($('<input />')
		.attr('type', 'hidden')
		.attr('name', 'csrfmiddlewaretoken')
		.attr('value', $.cookie('csrftoken')));

	// Daten
	$.each(param, function(name, value) {
		form.append($('<input />')
			.attr('type', 'hidden')
			.attr('name', name)
			.attr('value', value));
	});

	form.submit();
}

/**
 * Formatiert absolutes Datum als relatives
 * @param {string} rawDateTime - absolutes Datum
 * @example Jetzt ist 16-01-2015 17:32. getRelativeTime("16-01-2015 17:56") => "24 minutes ago"
 * @returns {string} - relatives Datum
 */
function getRelativeTime(rawDateTime) {
    return moment(rawDateTime).fromNow();
}