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
 * @param contentType Content-Type
 * @param processData param als Objekt mit den Parmetern behandeln
 */
function documentsJsonRequest(param, handler, contentType, processData) {
	contentType = typeof contentType !== 'undefined' ?
			contentType : 'application/x-www-form-urlencoded; charset=UTF-8';
	processData = typeof processData !== 'undefined' ?
			processData : true;
	jQuery.ajax(getUrl('/documents/'), {
		'type': 'POST',
		'data': param,
		'cache': false,
		'contentType': contentType,
		'processData': processData,
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
 * @param contentType Content-Type
 * @param processData param als Objekt mit den Parmetern behandeln
 */
function documentsDataRequest(param, handler, contentType, processData) {
	contentType = typeof contentType !== 'undefined' ?
			contentType : 'application/x-www-form-urlencoded; charset=UTF-8';
	processData = typeof processData !== 'undefined' ?
			processData : true;
	jQuery.ajax(getUrl('/documents/'), {
		'type': 'POST',
		'data': param,
		'cache': false,
		'contentType': contentType,
		'processData': processData,
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
	var form = $('<form></form>').attr('action', getUrl('/documents/')).attr('method', 'post');
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
    var dateTime = moment(rawDateTime),
        now = moment();

    // Kein Zukunftsdatum
    if (now.diff(dateTime) <= 0) {
        dateTime = now;
    }

    return dateTime.fromNow();
}

/*
 * Setzt den Inhalt des Alert Dialogs.
 *
 * @param title Titel für diesen Dialog
 * @param message Informationstext für diesen Dialog
 * @param redirection Pfad zur Weiterleitung bei Betätigung der Ok-Schaltfläche (optional)
 */
function showAlertDialog(title, message, redirection){
	$('#modal_alertDialog').modal('show');
	document.getElementById('modal_alertDialog_title').innerHTML = title;
	document.getElementById('modal_alertDialog_message').innerHTML = message;

	$('.modal_alertDialogConfirm').on("click", function() {
		if (redirection!=undefined) {
			document.location.assign(redirection);
        }
	})
}


/**
 * Gibt den absoluten URL zurück
 * @param String relativ URL
 * @return String absolut URL
 */
function getUrl(relativeUrl) {
    return BASE_URL.replace(/\/+$/, "") + relativeUrl;
}

/**
 * Gibt den absoluten URL der statischen Datei zurück
 * @param String relativ URL
 * @return String absolut URL
 */
function getStaticUrl(relativeUrl) {
    return STATIC_URL.replace(/\/+$/, "") + relativeUrl;
}


/**
 * Liefert true, falls ein mobiler Browser oder eine niedrige Auflösung verwendet wird, sonst false
 * http://detectmobilebrowsers.com
 * @returns {boolean}
 */
window.mobilecheck = function() {
    // ab dieser Breite der Auflösung des Clients wird die mobile Ansicht verwendet
    var mobileLayoutWidth = 1366;
    var check = false;

    (function(a,b){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))check = true})(navigator.userAgent||navigator.vendor||window.opera);

    return check || $(window).width() < mobileLayoutWidth;
}