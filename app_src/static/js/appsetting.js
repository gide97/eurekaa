function req_serverstatus() {
  $.ajax("/serverstatus", {
    success: (data, xhr, status) => {
      let dataKeys = Object.keys(data);
      let el_statusList = document.getElementById("service_status");

      let _t_element = "";
      dataKeys.map((_key, index) => {
        _t_element += `<li>${_key}: ${data[_key]}</li>`;
        console.log(data[_key]);
      });

      _t_element +=
        data["Service status"] == "STOPPED"
          ? '<button id="startService" onClick="req_startService(true)"> Start Service </button>'
          : '<button id="startService" onClick="req_startService(false)"> Stop Service </button>';
      el_statusList.innerHTML = _t_element;
    },
  });
}

function req_startService(flag) {
  $.ajax(flag ? "/startservice" : "/stopservice", {
    success: (data, xhr, status) => {
      console.log(data);
      if (data["response"] == "OK") {
        window.alert(flag ? "Service started" : "Service stopped");
      }
    },
  });
}

setInterval(req_serverstatus, 2000);
