//Функция смены типа поля для нового пароля, при выполнении пароль показывается полностью
function show(id) {
  document.getElementById(id).setAttribute('type', 'text');
}
//Функция смены типа поля для нового пароля, при выполнении пароль отображается в виде точек
function hide(id) {
  document.getElementById(id).setAttribute('type', 'password');
}
//При попадании на страницу выгружаем с сервера сохраненные контактные данные
window.onload = function() {
  getContactInfo();
}
//Ожидаем окончания загрузки страницы, после чего назначаем фунцию
//привязки для обработки нажатий на кнопку отображения/скрытия нового пароля
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById("toggle").addEventListener("click", function(e) {
    var pwd = document.getElementById("f_new");
    var butn = document.getElementById("icon")
    if (pwd.getAttribute("type") == "password") {
      pwd.setAttribute("type", "text");
      butn.setAttribute("class", "glyphicon glyphicon-eye-open");
    } else {
      pwd.setAttribute("type", "password");
      butn.setAttribute("class", "glyphicon glyphicon-eye-close");
    }
  });
});
//Получаем введенные данные и отправляем на сервер
function changePassword() {
  old_pass = document.getElementById('f_old').value;
  new_pass = document.getElementById('f_new').value;
  var form = new FormData();
  form.append('old_pass', old_pass);
  form.append('new_pass', new_pass);
  //Очищаем поля паролей
  document.getElementById('f_old').value = "";
  document.getElementById('f_new').value = "";
  basic_ajax_send('/py_scripts/passw_change.py', form);

}
//Получить контактные данные с сервера через AJAX
function getContactInfo() {
  $.ajax({
    url: '/py_scripts/get_contact_info.py',
    type: 'post',
    dataType: 'text',
    processData: false,
    contentType: false,
    success: function(data) {
			//Парсим данные в JS Object
			data = JSON.parse(data);
      if(data["details"]){
        console.log(data["details"]);
      }
      //Проверяем наличие ошибки, если ее нет показываем пользователю сохраненные данные
			if (data["error"]) {
        alert("Something went wrong");
      } else {
        document.getElementById('contact_field').value = data["info"];
      }
    },
    error: function(xhr, ajaxOptions, thrownError) {
			//Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
			console.log("ajax feed failed: " + xhr + " with " + thrownError);
      alert("Server Error")
    }
  });
}
//Обновить контактные данные
function updateContactInfo() {
	//Создаем форму
	var form = new FormData();
	//Получаем введенные пользователем данные
	var text = document.getElementById("contact_field").value.trim();
	//Проверяем, является ли текст пустым
	if (!text) {
		//сообщаем пользователю что нельзя сохранить пустые данные
		alert("Empty field not accepted");
		document.getElementById("contact_field").style.borderColor = "red";
    return;
  } else {
    document.getElementById("contact_field").style.borderColor = "";
  }
	//Прикрепляем к форме данные
  form.append("text", text);
	//Передаем запрос на сервер
  $.ajax({
    url: '/py_scripts/update_contact_info.py',
    type: 'post',
    data: form,
    dataType: 'text',
    processData: false,
    contentType: false,
    success: function(data) {
			//Ответ от сервера парсим
			data = JSON.parse(data);
      if(data["details"]){
        console.log(data["details"]);
      }
      //Проверяем наличие ошибок
			if (data["error"]) {
        alert("something went wrong");
      } else {
				//Если все прошло успешно, сообщаем что данные успешно сохранены
        alert("Saved");
      }
    },

    error: function(xhr, ajaxOptions, thrownError) {
			//Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
			console.log("Contact info failed: " + xhr + " with " + thrownError);
      alert("Server Error")
    }
  });

}
