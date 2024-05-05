var lx = 0;
var ly = 0;
var cx = 0;
var cy = 0;
var data = [];

const blobToBase64 = blob => {
  const reader = new FileReader();
  reader.readAsDataURL(blob);
  return new Promise(resolve => {
    reader.onloadend = () => {
      resolve(reader.result);
    };
  });
};


mediaSocket.onopen = function() {
  console.log("Соединение установлено");
  mediaSocket.send("00");
};


mediaSocket.onclose = function(event) {
  if (event.wasClean) {
    alert('Соединение закрыто чисто');
  } else {
    alert('Обрыв соединения'); // например, "убит" процесс сервера
  }
  alert('Код: ' + event.code + ' причина: ' + event.reason);
};


mediaSocket.onmessage = function(event) {
  blobToBase64(event.data).then(res => {
    display.src =res;

  });
  mediaSocket.send("00");
};


mediaSocket.onerror = function(error) {
  alert("Ошибка " + error.message);
};

document.addEventListener('mousemove', onMousePosUpdate, false);
document.addEventListener('mouseenter', onMousePosUpdate, false);

document.addEventListener('keydown', onKeyDown, false);
function onKeyDown(e) {
    console.log(event.keyCode+" "+event.code);
    //socket.send("4"+event.keyCode)
  data.push("4"+event.keyCode)
}

document.addEventListener('keyup', onKeyUp, false);
function onKeyUp(e) {
    console.log(event.keyCode+" "+event.code);
    //socket.send("4"+event.keyCode)
  data.push("7"+event.keyCode);
}

function onMousePosUpdate(e) {
  cx = e.pageX - display.offsetLeft;
  cy = e.pageY - display.offsetTop;
}

document.addEventListener('mousedown', onMouseDown, false);
function onMouseDown(e) {
    //socket.send("3"+e.which)
    data.push("3"+e.which);
}

document.addEventListener('mouseup', onMouseUp, false);
function onMouseUp(e) {
    //socket.send("5"+e.which)
    data.push("5"+e.which);
}

document.addEventListener('wheel', onWheel, false);
function onWheel(e) {
  var delta = (e.deltaY) | 0;
  //socket.send("6"+delta)
  data.push("6"+delta);
}


let timerId = setInterval(sendEvents, 25);
function sendEvents() {
  if (inputSocket.readyState === WebSocket.OPEN) {
    if ((cx != lx) || (cy != ly)) {
      if (useJoinedPos) {
        data.push("8"+lx+"\t"+ly)
      } else {
        data.push("1"+lx)
        data.push("2"+lx)
      }
      lx = cx;
      ly = cy;
    }
    if (data.length > 0) {
      inputSocket.send(data[0]);
      //console.log(data);
      data.shift();
    }
  }
}
