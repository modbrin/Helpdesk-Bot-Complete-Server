//Доп. функция для chrome и firefox
$(document).keydown(function(event) {
    //ctrl+s для chrome и firefox
    if (!( String.fromCharCode(event.which).toLowerCase() == 's' && event.ctrlKey) && !(event.which == 19)) return true;
    event.preventDefault();
    if(!document.getElementById('btn_save').disabled){
        make_update();
    }
    return false;
});
//Переменная-буфер для хранения списка всех заголовков статей и их ID
var titles = {};
//Функция для добавления нового заголовка статьи с список
function addRow(id, text, listID) {
  //Создаем элемент списка
  var newRow = document.createElement('li');
  //Если элемент соответствующий данному в данныый момент выбран, то выделить его цветом
  if (id == article_id) {
    newRow.setAttribute("style", "background-color:#a0fffd");
  }
  //Назначем элементу списка нужные параметры
  newRow.setAttribute("class", "row_tile");
  newRow.innerHTML = text;
  newRow.setAttribute('id', id)
  newRow.setAttribute("onclick", "openArticle(this.id)");
  //Прикрепляем его к списку
  document.getElementById(listID).appendChild(newRow);
};
//Функция очистки списка
function reset_list() {
  document.getElementById('main_list').innerHTML = "";
}
//При загрузке страницы блокируем панель ввода, тк ни одна статья еще не выбрана
//После этого запрашиваем список статей
window.onload = function() {
  setDisabledPanel(true);
  getArticleList();
}
//функция блокировки\разблокировки панели справа
function setDisabledPanel(state) {
  document.getElementById('title').disabled = state;
  quill.enable(!state);
  document.getElementById('token_field').disabled = state;
  document.getElementById('btn_sw_1').disabled = state;
  document.getElementById('btn_sw_2').disabled = state;
  document.getElementById('btn_sw_3').disabled = state;
  document.getElementById('btn_save').disabled = state;
  document.getElementById('btn_delete').disabled = state;
  document.getElementById('browser_button').disabled = state;
}
//Составление списка, использует таблицу заголовков списка, сохраненную при обработке ответа от сервера
function constructList() {
  document.getElementById('main_list').innerHTML = "";
  //Итерируемся по списку и добавляем статьи, они хранятся в формате
  //{id:title,...}
  for (var element in titles) {
    addRow(element, titles[element], 'main_list');
  }
  // Проверяем, если после составления списка страница осталась пустой, выводим сообщение "No elements"
  if (!document.getElementById('main_list').innerHTML) {
		//Составляем элемент сообщения
    var newRow = document.createElement('li');
		//цвет шрифта - красный
    newRow.setAttribute("style", "color:red;text-align:center")
    newRow.innerHTML = "  No elements";
		//Добавляем сообщение в список
    document.getElementById('main_list').appendChild(newRow);
  }
}
//Добавление элемента токена в Token Pool (далее Контейнер токенов) без применеия средств обработки языка
function addToken() {
	//Получаем данные из поля ввода токенов
	var token_name = document.getElementById('token_field').value;
  document.getElementById('token_field').value = "";
	//разделяем токены по пробелам
	var tokens = token_name.toLowerCase().split(" ");
	//добавляем их в контейнер токенов
	for (var o in tokens) {
    token_ready = tokens[o].trim();
		// проверяем пустые токены
		if (token_ready) {
      document.getElementById('token_pool').appendChild(constructToken(token_ready));
    }
  }
	//убираем повторяющиеся токены
  refactor();
}
// Конструктор токенов
function constructToken(text) {
	//создаем текст
	var textNode = document.createElement('span');
  textNode.innerHTML = text
	//создаем маркер удаления
	var cross = document.createElement('span');
  cross.setAttribute('onclick', "this.parentNode.parentNode.removeChild(this.parentNode)");
  cross.innerHTML = " X";
	//создаем сам элемент токена и присоединяем к нему текст и маркер удаления
  var wrap = document.createElement('div');
  wrap.setAttribute('class', 'token-wrap');
  wrap.appendChild(textNode);
  wrap.appendChild(cross);
	//возвращаем готовый элемент токена
	return wrap;
}
//передаем токены из поля ввода в токенизатор
function addTokens_nlp() {
  var token_name = document.getElementById('token_field').value;
  var tokens = getTokens_nlp(token_name);
}
//передаем название статьи в токенизатор
function addTokens_nlp_title() {
  var token_name = document.getElementById('title').value;
  var tokens = getTokens_nlp(token_name);
}
//удаляем все токены
function clear_tokens() {
  if (confirm("Remove all tokens?")) {
    document.getElementById('token_pool').innerHTML = "";
    document.getElementById('token_field').value = "";
  }
}
//функция преобразования контерйнера токенов в массив строк
function parse_pool() {
  var pool = document.getElementById('token_pool').children;
  var out = [];
  for (i = 0; i < pool.length; i++) {
    out.push(pool[i].children[0].innerHTML);
  }
  return out;
}
//удаление повторяющихся токенов
function refactor() {
	//загружаем токены в массив
	var names = parse_pool();
	//переносим уникальные в новый массив
  var uniqueNames = [];
  $.each(names, function(i, el) {
    if ($.inArray(el, uniqueNames) === -1)
      uniqueNames.push(el);
  });
	//преобразуем массив обратно в контейнер токенов
  document.getElementById('token_pool').innerHTML = "";
  tPool_from_arr(uniqueNames);
}
//преобразование массива токенов в контейнер токенов
function tPool_from_arr(array) {
  for (var token in array) {
    document.getElementById('token_pool').appendChild(constructToken(array[token]));
  }
}
// Загружаем список статей
function getArticleList() {
  $.ajax({
    url: '/py_scripts/load_article_list.py',
    type: 'post',
    dataType: 'text',
    processData: false,
    contentType: false,
    success: function(data) {
			//получаем ответ от сервера, преобразуем его в объект
      titles = JSON.parse(data);
      if(titles["details"]){
        console.log(data["details"]);
      }
			//составляем список
			constructList();
    },
    error: function(xhr, ajaxOptions, thrownError) {
			//Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
			console.log("Article list request failed: " + xhr + " with " + thrownError);
      alert("Server Error")
    }
  });
}

// Переменные для хранения текущей статьи
var article_id, article_title, article_text, article_tokens, article_views, article_likes;

//Открываем статью в новой вкладке
function showInBrowser() {
  if (checkMove()) {
    window.open("/public/view.py?id=" + document.getElementById("id").innerHTML);
  }
}
//Проверяем, есть ли изменения статьи у пользователя,
//в этом случае предупреждаем его о возможности потерять данные
function checkMove() {
  if (article_id) {
    if (hasChanged()) {
      return confirm("Unsaved changes will be lost. Want to continue?");
    } else return true;
  } else return true;
}
// Отобразить выбранную статью
function openArticle(id) {
  if (checkMove()) {
    setDisabledPanel(false);
    getArticleById(id);
  }
}
// Выводим полученные данные статьи в панель радктирования
function setArticleView() {
  document.getElementById('id').innerHTML = article_id;
  document.getElementById('title').value = article_title;
	quill.setContents([{
    insert: ''
  }]);
	//данные на сервере хранятся в виде готовой Html страницы
	//чтобы отобразить ее в редакторе, преобразуем html обратно в формат quill
  quill.clipboard.dangerouslyPasteHTML(article_text);
  document.getElementById('views').innerHTML = article_views;
  document.getElementById('likes').innerHTML = article_likes;
  document.getElementById('token_pool').innerHTML = "";
  tPool_from_arr(article_tokens.split(" "));
}
//сверяем сохраненные в переменных данные и текущие значения полей
//если изменений, нет то предупреждать пользователя о потере данных не нужно
function hasChanged() {
  // проверяем несоответсвия с последней загруженной версией из бд
  // заголовка
  var titleCheck = document.getElementById('title').value.trim() == article_title.trim();
  // текста
  var textCheck = quillGetHTML(quill.getContents()).trim() == article_text.trim();
  // токенов
  var tokenCheck = arr_to_str(parse_pool()).trim() == article_tokens.trim();
  // суммарно
  var checker = titleCheck&&textCheck&&tokenCheck;
  return !checker;
}
//Получаем данные конкретной статьи по ID
function getArticleById(id) {
  var data = new FormData();
  data.append("id", id);
  $.ajax({
    url: '/py_scripts/get_article.py',
    type: 'post',
    dataType: 'text',
    data: data,
    processData: false,
    contentType: false,
    success: function(data) {
      data = JSON.parse(data);
      if(data["details"]){
        console.log(data["details"]);
      }
			//обновляем данные в переменных
			if (!data["error"]) {
        article_id = data["id"];
        article_title = data["title"];
        article_text = data["text"];
        article_tokens = data["keywords"];
        article_views = data["viewCount"];
        article_likes = data["likeCount"];
        setArticleView();
        constructList();
      } else {
        alert(data["error"]);
      }

    },
    error: function(xhr, ajaxOptions, thrownError) {
			//Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
			console.log("article by id request failed: " + xhr + " with " + thrownError);
      alert("Server Error")
    }
  });
}
// Преобразование массива в строку
function arr_to_str(arr) {
  var result = "";
  for (i = 0; i < arr.length; i++) {
    result += arr[i] + " ";
  }
  result = result.trim();
  return result;
}
// Обновить страницу
function make_update() {
  var id = article_id;
	//Получаем данные со страницы
  var title = document.getElementById('title').value;
  var text = quillGetHTML(quill.getContents());
  var tokens = arr_to_str(parse_pool());
	//Передаем их в запрос серверу
  updateArticle(id, title, text, tokens);
}
//вызываем создание статьи
function create_article() {
  createArticle();
}
// Удаляем статью, предварительно уточнив это у пользователя
function delete_article() {
  if (confirm("Do you really want to delete this article?")) {
    deleteArticle(article_id);
  }

}
// Преобразуем формат quill (Delta) в HTML
function quillGetHTML(inputDelta) {
  var tempCont = document.createElement("div");
  (new Quill(tempCont)).setContents(inputDelta);
  return tempCont.getElementsByClassName("ql-editor")[0].innerHTML;
}
// Обновляем статью
function updateArticle(id, title, text, tokens) {
	//Создаем форму запроса
	var data = new FormData();
  data.append("id", id);
  data.append("title", title);
  data.append("text", text);
  data.append("keywords", tokens);
  document.getElementById("btn_save").disabled = true;
  $.ajax({
    url: '/py_scripts/update_article.py',
    type: 'post',
    dataType: 'text',
    data: data,
    processData: false,
    contentType: false,
    success: function(data) {
      data = JSON.parse(data);
      if(data["details"]){
        console.log(data["details"]);
      }
      //Получаем данные, при наличии ошибки сообщаем о ней
			if (data["error"]) {
        alert("Something went wrong");
      } else {
        alert("Saved");
      }
			//открываем статью заново
      getArticleById(id);
      document.getElementById("btn_save").disabled = false;
			//обновляем список статей
			getArticleList();
    },
    error: function(xhr, ajaxOptions, thrownError) {
			//Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
			console.log("article update request failed: " + xhr + " with " + thrownError);
      alert("Server Error")
      document.getElementById("btn_save").disabled = true;
    }
  });
}
//Очищаем редактор статьи
function clear_article_view() {
  document.getElementById('title').value = "";
  quill.setContents([{
    insert: ''
  }]);
  document.getElementById('token_pool').innerHTML = "";
  document.getElementById('id').innerHTML = "";
  document.getElementById('views').innerHTML = "";
  document.getElementById('likes').innerHTML = "";
	//обнуляем переменные
	article_id = null;
  article_title = null;
  article_text = null;
  article_tokens = null;
  article_views = null;
  article_likes = null;
	//отключаем панель редактора
	setDisabledPanel(true);
}
// Запрос на удаление статьи
function deleteArticle(id) {
  var data = new FormData();
  data.append("id", id);
  document.getElementById("btn_delete").disabled = true;
  $.ajax({
    url: '/py_scripts/delete_article.py',
    type: 'post',
    dataType: 'text',
    data: data,
    processData: false,
    contentType: false,
    success: function(data) {
      data = JSON.parse(data);
      if(data["details"]){
        console.log(data["details"]);
      }
      // Получаем ответ от сервера, если нет ошибки очищаем редактор и обновляем список статей
			if (data["error"]) {
        alert("Something went wrong")
      } else {
      	getArticleList();
      	clear_article_view();
			}
    },
    error: function(xhr, ajaxOptions, thrownError) {
			//Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
			console.log("article list request failed: " + xhr + " with " + thrownError);
      alert("Server Error")
    }
  });
}
// Создаем новую статью
function createArticle() {
  document.getElementById("btn_new").disabled = true;
  $.ajax({
    url: '/py_scripts/new_article.py',
    type: 'post',
    dataType: 'text',
    processData: false,
    contentType: false,
    success: function(data) {
      data = JSON.parse(data);
      if(data["details"]){
        console.log(data["details"]);
      }
      if(data['id']){
        openArticle(data['id']);
      }
			//Обновляем список статей
			getArticleList();
      document.getElementById("btn_new").disabled = false;
    },
    error: function(xhr, ajaxOptions, thrownError) {
			//Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
			console.log("article list request failed: " + xhr + " with " + thrownError);
      alert("Server Error")
      document.getElementById("btn_new").disabled = false;
    }
  });
}
