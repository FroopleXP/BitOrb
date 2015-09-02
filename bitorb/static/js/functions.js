function login_user(data, onSuccess, onFailed, onError) {
    $.ajax({
        url: '/api/v1/user/login',
        method: 'POST',
        data: data,
        success: function(data, stat, xhr) {
            // Cookies.set("auth_token", data.auth_token);
            switch (data.status) {
                case "failed":
                    noti(data.message, 0);
                    if (onFailed){
                        onFailed(data);
                    }
                    break;
                case "success":
                    noti(data.message, 1);
                    Cookies.set("auth_token", data.auth_token);
                    console.dir(data);
                    if (onSuccess){
                        onSuccess(data);
                    }
                    break;
            }
        },  
        error: function(xhr, stat, err) {
            noti(xhr.responseJSON.message, 0);
            if (onError){
                onError(xhr.resposeJson)
            }
        }
    });
}

function noti(msg, stat) {
    var noti_box = $('#err_hand');
    switch (stat) {
        case 1:
            noti_box.hide();
            noti_box.addClass("alert-success").text(msg).slideDown();
            break;
        case 0:
            noti_box.hide();
            noti_box.addClass("alert-danger").text(msg).slideDown();
            break;
    }
}

var QueryString = function () {
  // This function is anonymous, is executed immediately and
  // the return value is assigned to QueryString!
  var query_string = {};
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("=");
        // If first entry with this name
    if (typeof query_string[pair[0]] === "undefined") {
      query_string[pair[0]] = decodeURIComponent(pair[1]);
        // If second entry with this name
    } else if (typeof query_string[pair[0]] === "string") {
      var arr = [ query_string[pair[0]],decodeURIComponent(pair[1]) ];
      query_string[pair[0]] = arr;
        // If third or later entry with this name
    } else {
      query_string[pair[0]].push(decodeURIComponent(pair[1]));
    }
  }
    return query_string;
}();