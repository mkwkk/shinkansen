function like(postId) {
  const likeCount = document.getElementById(`likes-count-${postId}`);
  const likeButton = document.getElementById(`like-button-${postId}`);
  fetch(`/like-post/${postId}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      likeCount.innerHTML = data["likes"];
      if (data["liked"] === true) {
        likeButton.className = "fas fa-thumbs-up";
      } else {
        likeButton.className = "far fa-thumbs-up";
      }
    })
    .catch((e) => alert("Could not like post."));
}
<<<<<<< HEAD
=======

$(document).ready(function() {
  var readURL = function(input) {
    if (input.files && input.files[0]) {
        new Promise(function(resolve, reject) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#avatar').attr('src', e.target.result);
            resolve(e.target.result);
        };
        reader.readAsDataURL(input.files[0]);
        reader.onerror = reject;
        })
        .then(processFileContent)
        .catch(function(err) {
        console.log(err)
        });
    }
}

function processFileContent(data) {
    var list = data.split('\n');
    $('#image').val(list);
}
  $(".file-upload").on('change', function(){
      readURL(this);
  });

  $("#avatar").on('click', function() {
     $(".file-upload").click();
  });
});
>>>>>>> minhthu
