// Переменные для хранения
var id_list;
var email_list;
var alias_list;

var list_data;
var current_id;
var current_email;
var current_alias;

function addRow(id, left, right, listID) {
	var leftCell = document.createElement('div');
	leftCell.setAttribute("class", "row_tile_cell");
	leftCell.setAttribute("style", "float:left;overflow:hidden;");
	leftCell.innerHTML = left;
	var rightCell = document.createElement('div');
	rightCell.setAttribute("class", "row_tile_cell");
	rightCell.setAttribute("style", "float:right");
	rightCell.innerHTML = right;
	var newRow = document.createElement('li');
	if(id==current_id){
		newRow.setAttribute("style","background-color:#a0fffd");
	}
	newRow.setAttribute("class", "row_tile");
	newRow.appendChild(leftCell);

	newRow.appendChild(rightCell);
	newRow.setAttribute("id",id);
	newRow.setAttribute("onclick", "select(this)");
	document.getElementById(listID).appendChild(newRow);
};
function select(item) {
setDisabledUserPanel(false);
	document.getElementById('email_field').style.borderColor = "";
	document.getElementById('alias_field').style.borderColor = "";
	current_id = item.id;
	current_email = item.children[0].innerHTML.trim();
	current_email = current_email.substring("&nbsp;".length,current_email.length-"@innopolis.ru".length)
	current_alias = item.children[1].innerHTML.trim();
	document.getElementById('email_field').value = current_email;
	document.getElementById('alias_field').value = current_alias;
	document.getElementById('e_show').innerHTML = current_email;
	document.getElementById('a_show').innerHTML = current_alias;
	construct_list();
}
//Проверяем наличие пробелов в строке
function hasWhiteSpace(s) {
	return /\s/g.test(s);
}
//
function check_email(email) {
	if(!email){
		alert("Empty email not allowed.");
	}
	if(hasWhiteSpace(email)){
		alert("No whitespaces allowed.");
	}
	return !hasWhiteSpace(email) && email;
};
function check_alias(alias) {
	if(hasWhiteSpace(alias)){
		alert("No whitespaces allowed.");
	}
	return !hasWhiteSpace(alias);
};

function make_search(){
	reset_list();
	var text = document.getElementById('search_field').value;
	if(text.trim()){
		for (var element in list_data) {
			if(list_data[element][0].toLowerCase().trim().indexOf(text.toLowerCase().trim())>-1||list_data[element][1].toLowerCase().trim().indexOf(text.toLowerCase().trim())>-1){
				addRow(element, "&nbsp"+list_data[element][0]+"@innopolis.ru", list_data[element][1], 'main_list');
			}

		}
	}else{
		construct_list(email_list,alias_list);
	}
}

function construct_list() {
	reset_list();
	for (var element in list_data) {
		addRow(element, "&nbsp"+list_data[element][0]+"@innopolis.ru", list_data[element][1], 'main_list');
	}
	if(!document.getElementById('main_list').innerHTML){
		var element = document.createElement('div');
		element.setAttribute("class", "row_tile_article");
		var newRow = document.createElement('li');
		newRow.setAttribute("style","color:red;text-align:center")
		newRow.innerHTML = "  No elements";
		document.getElementById('main_list').appendChild(newRow);
	}
}

function reset_list() {
	document.getElementById('main_list').innerHTML = "";
}
window.onload = function () {
	get_user_list();
	setDisabledUserPanel(true);
}

function clear_fields(){
	document.getElementById('email_field').value = "";
	document.getElementById('alias_field').value = "";
	document.getElementById('e_show').innerHTML = "";
	document.getElementById('a_show').innerHTML = "";
	document.getElementById('email_field').style.borderColor = "";
	document.getElementById('alias_field').style.borderColor = "";
}
function get_user_list(){
	$.ajax({
			url: '/py_scripts/get_users.py',
			type: 'post',
			dataType: 'text',
			processData: false,
			contentType: false,
			success: function (data) {
				list_data = JSON.parse(data);
				if(list_data["detail"]){
					console.log(data["detail"]);
				}
				construct_list();
			},
			error: function (xhr, ajaxOptions, thrownError) {
				console.log("article list request failed: " + xhr + " with " + thrownError);
				alert("Server Error")
			}
		});
}

function createUser(){
	$.ajax({
			url: '/py_scripts/new_user.py',
			type: 'post',
			dataType: 'text',
			processData: false,
			contentType: false,
			success: function (data) {
				data = JSON.parse(data);
				if(data["detail"]){
					console.log(data["detail"]);
				}
				if(data["id"]){
					setDisabledUserPanel(false);
					current_id = data["id"];
					get_user_list();
					clear_fields();
					document.getElementById("a_show").innerHTML = "USER";
					document.getElementById("e_show").innerHTML = "NEW";
				}else{
					alert("Empty user (\"new_user\") already exists")
				}
			},
			error: function (xhr, ajaxOptions, thrownError) {
				console.log("article list request failed: " + xhr + " with " + thrownError);
				alert("Server Error")
			}
		});
}
function deleteUser(){
	var data = new FormData();
	data.append("id", current_id);
	$.ajax({
			url: '/py_scripts/delete_user.py',
			type: 'post',
			dataType: 'text',
			data: data,
			processData: false,
			contentType: false,
			success: function (data) {
				data = JSON.parse(data);
				if(data["detail"]){
					console.log(data["detail"]);
				}
				clear_fields();
				get_user_list();
				setDisabledUserPanel(true);
				document.getElementById('email_field').style.borderColor = "";
				document.getElementById('alias_field').style.borderColor = "";
			},
			error: function (xhr, ajaxOptions, thrownError) {
				console.log("article list request failed: " + xhr + " with " + thrownError);
				alert("Server Error")
			}
		});
}
function setDisabledUserPanel(state){
	document.getElementById("email_field").disabled = state;
	document.getElementById("alias_field").disabled = state;
	document.getElementById("update_button").disabled = state;
	document.getElementById("delete_button").disabled = state;
}
function updateUser(){
	var data = new FormData();
	document.getElementById('email_field').style.borderColor = "";
	document.getElementById('alias_field').style.borderColor = "";
	if(!check_email(document.getElementById('email_field').value.trim())){
		document.getElementById('email_field').style.borderColor = "red";
		return;
	} else if(!check_alias(document.getElementById('alias_field').value.trim())) {
		document.getElementById('alias_field').style.borderColor = "red";
		return;
	}
	data.append("id", current_id);
	var temp_email = document.getElementById('email_field').value.trim();
	var temp_alias = document.getElementById('alias_field').value.trim();
	data.append("email", temp_email);
	data.append("userID", temp_alias);

	$.ajax({
			url: '/py_scripts/update_user.py',
			type: 'post',
			dataType: 'text',
			data: data,
			processData: false,
			contentType: false,
			success: function (data) {
				data = JSON.parse(data);
				if(data["detail"]){
					console.log(data["detail"]);
				}
				current_email = temp_email;
				current_alias = temp_alias;
				document.getElementById('e_show').innerHTML = current_email;
				document.getElementById('a_show').innerHTML = current_alias;

				get_user_list();
			},
			error: function (xhr, ajaxOptions, thrownError) {
				console.log("article list request failed: " + xhr + " with " + thrownError);
				alert("Server Error")
			}
		});
}
