//Специальный флаг для вариации цветов сообшений
var variator = true;
//Переменная для хранения списка
feedback_container = null;
//Функция переключения флага
function switchColor() {
  if (variator) {
    variator = false;
  } else {
    variator = true;
  }
}
//При загрузке страницы обращаемся к серверу, получаем список отзывов
window.onload = function(){
  get_feedback();
}
//Добавить сообщение на страницу
function addRow(id,name, email, grade, feedback) {
  var cell = document.createElement('div');
  //Если флаг в положении True, создать стиль для сообщения с коричневым фоном, если False - с синим
  if (variator) {
    cell.setAttribute("style", "padding:10px;background-color:#d7ccc8;border-bottom: 1px solid black")
  } else {
    cell.setAttribute("style", "padding:10px;background-color:#cfd8dc;border-bottom: 1px solid black")
  }
  //Переключить цвет
  switchColor();
  //Создаем новую строку, к ней привязываем параграф с отзывом и заголовок с данными пользователя
  cell.setAttribute("class", "row");
  var text = document.createElement('p');
  text.innerHTML = feedback;
  var header = document.createElement('h4');
  header.innerHTML = "Name: " + name + ", Rating: " + grade + "/5, Email: " + email;
  var delete_button = document.createElement('input');
  delete_button.setAttribute("type","button");
  delete_button.setAttribute("value","X");
  delete_button.setAttribute("onclick","delete_feedback('"+id+"');");
  delete_button.setAttribute("style","float:right;")
  cell.appendChild(delete_button);
  cell.appendChild(header);
  cell.appendChild(text);
  document.getElementById('container').appendChild(cell);
}
//Добавляем полуенные данные на страницу
//{id:[name,email,grade,feedback],...}
function construct_feedback_list(data) {
  document.getElementById('container').innerHTML = "";
  for (var element in data) {
    addRow(element, data[element][0], data[element][1], data[element][2],data[element][3]);
  }
  checkEmpty();
}
function checkEmpty(){
	//Если данных с сервера нет, добавляем ячейку "NO ELEMENTS"
  if(!document.getElementById('container').innerHTML.trim()){
    var cell = document.createElement('div');
    cell.setAttribute("style", "padding:10px;text-align:center;background-color:#d7ccc8")
    var paragraph = document.createElement('p');
    paragraph.innerHTML = "NO ELEMENTS";
    paragraph.setAttribute("style","color:red");
    cell.appendChild(paragraph);
    document.getElementById("container").appendChild(cell);
  }
}
function filterRating(value){
  if(value=="any"){
    construct_feedback_list(feedback_container);
  }else{
    search_feedback_list(feedback_container,value);
  }
}
// поиск по рейтингу
function search_feedback_list(data, rating_search) {
  document.getElementById('container').innerHTML = "";
  for (var element in data) {
	  if(data[element][2] == rating_search){
		    addRow(element, data[element][0], data[element][1], data[element][2], data[element][3]);
	  }
  }
  checkEmpty();
}
//Вызов AJAX для получения полного списка отзывов
function get_feedback() {
  $.ajax({
    url: '/py_scripts/load_feedback_list.py',
    type: 'post',
    dataType: 'text',
    processData: false,
    contentType: false,
    success: function(data) {
      data = JSON.parse(data);
      //При возникновении ошибки, предупреждаем пользователя о сбое в работе ошибка пишется в лог браузера
      if (data["error"]) {
        alert("Something went wrong");
        console.log(data["error"]);
      } else {
        //Когда данные получены успешно, передаем их в функцию вывода
        feedback_container = data;
        filterRating(document.getElementById('rating_selector').value);
      }
    },
    error: function(xhr, ajaxOptions, thrownError) {
      //Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
      console.log("Feedback list request failed: " + xhr + " with " + thrownError);
      alert("Server Error");
    }
  });
}
function delete_feedback(id) {
  if(!confirm("Want to delete this feedback?")){
    return;
  }
  var data = new FormData();
  data.append("id",id)
  $.ajax({
    url: '/py_scripts/delete_feedback.py',
    type: 'post',
    dataType: 'text',
    data: data,
    processData: false,
    contentType: false,
    success: function(data) {
      //При возникновении ошибки, предупреждаем пользователя о сбое в работе ошибка пишется в лог браузера
      if (data["error"]) {
        alert("Something went wrong");
        console.log(data["error"]);
      } else {
        //Когда данные получены успешно, передаем их в функцию вывода
        get_feedback();
      }
    },
    error: function(xhr, ajaxOptions, thrownError) {
      //Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
      console.log("Feedback list request failed: " + xhr + " with " + thrownError);
      alert("Server Error");
    }
  });
}
