function login_user(data) {
    $.ajax({
        url: '/api/v1/user/login',
        method: 'POST',
        data: data,
        success: function(data, stat, xhr) {
            // Cookies.set("auth_token", data.auth_token);
            switch (data.status) {
                case "failed":
                    noti(data.message, 0);
                    break;
                case "success":
                    noti(data.message, 1);
                    break;
            }
        },  
        error: function(xhr, stat, err) {
            noti(xhr.responseJSON.message, 0);
        }
    });
}

function noti(msg, stat) {
    var noti_box = $('#err_hand');
    switch (stat) {
        case 1:
            noti_box.html('<div class="alert alert-success" role="alert">'  + msg + '</div>');
            break;
        case 0:
            noti_box.html('<div class="alert alert-danger" role="alert">'  + msg + '</div>');
            break;
    }
}
