//Стандартный запрос AJAX, используется в простых запросах
function basic_ajax_send(path, _data_) {
  $.ajax({
    url: path,
    type: 'post',
    data: _data_,
    dataType: 'text',
    processData: false,
    contentType: false,
    success: function(data) {
      //Результат запроса приходит в форме Html страницы в этом варианте, нужно его запарсить
      var result = /<body.*?>([\s\S]*)<\/body>/.exec(data.toString())[1];
      alert(result);
    },
    error: function(xhr, ajaxOptions, thrownError) {
			//Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
			console.log("ajax feed failed: " + xhr + " with " + thrownError);
      alert("Server Error")
    }
  });
}
//Запрос на получение массива токенов из предложения
function tokens_ajax_send(path, _data_) {
  $.ajax({
    url: path,
    type: 'post',
    data: _data_,
    dataType: 'text',
    processData: false,
    contentType: false,
    success: function(data) {
			//После получения токенов, нужно вывести их на страницу
			handleTokens(data);
    },
    error: function(xhr, ajaxOptions, thrownError) {
			//Если же возникла проблема с соединенем или сбой в работе сервера
      //и ответ получен быть не может, предупреждаем о проблеме
			console.log("Cannot tokenize: " + xhr + " with " + thrownError);
    }
  });
}
// Получаем токены с токенизатора (с применением средств обработки языка)
function getTokens_nlp(text) {
  var formdata = new FormData();
  formdata.append('text', text)
  var result = tokens_ajax_send('/py_scripts/tokenizer.py', formdata);
}

// Вывод токенов на страницу
function handleTokens(text) {
	//Преобразуем ответ от сервера в объект
	var tokens = JSON.parse(text);
	//добавляем в контейнер токенов элементы
	for (var o in tokens) {
    document.getElementById('token_pool').appendChild(constructToken(tokens[o]));
  }
	//очищаем поле ввода токенов
  document.getElementById('token_field').value = "";
	//убираем повторяющиеся токены
	refactor();

}
