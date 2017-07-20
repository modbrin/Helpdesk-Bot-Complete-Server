function markUseful(id){
  var formData = new FormData();
  formData.append('id', id);
  $.ajax({
    url: '/public/like.py',
    type: 'post',
	data: formData,
    dataType: 'text',
    processData: false,
    contentType: false,
    success: function (data) {
	  console.log(data);
	  document.getElementById('likeButton').disabled = true;
    }
  });
}