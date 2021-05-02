


document.getElementById("listbucketButton").onclick = function () {

	$.ajax({
		url: '/_list_bucket?bucket=' + $('#voiceSelected option:selected').val(),
		type: 'GET',
		success: function (data) {
			$('#posts tr').slice(1).remove();

			jQuery.each(data, function (i, d) {

				$("#posts").append("<tr id=" + Math.floor(Math.random() * 100) + ">\
								<td class=\"nr\">" + d['bucket_name'] + "</td> \
								<td class=\"nr\">" + d['object_name'] + "</td> \
								<td class=\"nr\">" + d['sync_status'] + "</td> \
								<td class=\"nr\">" + d['bucket_sync'] + "</td> \
								<td>  <button type=\"button\" id=\"fname\" name=\"fname\" value=\"Sync\" class=\"btn btn-warning\"  onclick=\"submit_by_id()\" > SYNC</button> </td > \
								<td class=\"nr\"> \
									<select id=\"bucket_dest\"> \
										<option value=\"bucket1\">Bucket 1 </option>  \
										<option value=\"bucket2\">Bucket 2 </option> \  </select>  \
										<option value=\"bucket3\">Bucket 3 </option > \  </select >  \
								</td > \
								</tr > ");
			});
		},
		error: function () {
			alert("error");
		}
	});
}


function submit_by_id() {

	var rowId = event.target.parentNode.parentNode.id;

	var data = document.getElementById(rowId).querySelectorAll(".nr");
	/*returns array of all elements with 
	"row-data" class within the row with given id*/

	var bucket_name = data[0].innerHTML;
	var object_name = data[1].innerHTML;
	var select_item = data[4].querySelector('#bucket_dest').selectedIndex;
	var bucket_dest = data[4].getElementsByTagName('option')[select_item].value;

	var inputData = {
		"bucket_name": bucket_name,
		"object_name": object_name,
		"bucket_dest": bucket_dest
	};
	console.log(bucket_dest);
	$.ajax({
		url: "/_request_sync",
		type: 'POST',
		data: JSON.stringify(inputData),
		contentType: 'application/json; charset=utf-8',
		success: function (response) {
			alert("teste" + response);
		},
		error: function () {
			alert("error");
		}
	});


}

// $("#posts tr").click(function () {
// 	var value = $(this).find('td:first').html();
// 	alert(value);
// });



// Submit form with id function.
// function submit_by_id() {

// 	$(".use-address").click(function () {
// 		var $row = $(this).closest("tr");    // Find the row
// 		var $text = $row.find(".nr").text(); // Find the text

// 		// Let's test it out
// 		alert($text);
// 	});
// 	// $.ajax({
// 	// 	url: '/',
// 	// 	type: 'POST',
// 	// 	success: function (data) {



// 	// 		// Let's test it out
// 	// 		alert("TESTE AJAX " + data);

// 	// 	},
// 	// 	error: function () {
// 	// 		alert("error");
// 	// 	}
// 	// });
// }

