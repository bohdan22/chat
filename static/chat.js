// Support TLS-specific URLs, when appropriate.
var ws_scheme = "ws://" + location.host + "/ws/" + window.location.pathname.split('/')[2]

console.log(window.location.pathname.split('/')[2])

var ws = new ReconnectingWebSocket(ws_scheme, null, {debug: true, reconnectInterval: 200, reconnectDecay: 1});

ws.onmessage = function (evt) {
    var data = JSON.parse(evt.data)
    var name = data['name']
    var msg = data['msg']
    var date = data['date']
    $('#message_media_id').append(
        '<li class="media message_media"> <div class="media-body"> <div class="media"> <div class="media-body"> <small class="text-muted"><strong>'+ name +'</strong> | '+date+'</small><br /> '+ msg +' </div> </div> </div> </li>'
    );
    var n = $(document).height();
    $('html, body').animate({ scrollTop: n });
};

ws.onclose = function(event) {
  if (event.wasClean) {
    console.log('Соединение закрыто чисто');
  } else {
    console.log('Обрыв соединения'); // например, "убит" процесс сервера
  }
  console.log('Код: ' + event.code + ' причина: ' + event.reason);
};

ws.onerror = function(error) {
  console.log("Ошибка " + error.message);
};

ws.onopen = function() {
  console.log("Соединение установлено.");
};


$('#msg_form').submit(function(){
    $message = $("input[name='msg']")
    room = window.location.pathname.split('/')[2];
    var msg = $message.val()
    if (msg.length < 1) {
        $("#message_form_id").addClass( "has-error" );
    }
    else{
        $message.val('');

        var msg = {
          msg: msg,
          room: room
        };

        var str = JSON.stringify(msg);
        console.log(str)
        ws.send(str);
        return false;
    }
});
