var mqtt;
let host = "10.23.16.33";
let port = 9001;
let log = [];
let topicWantToDraw = "sensor_0";

function onConnect() {
  console.log("connected to broker");
  mqtt.subscribe("#", {
    qos: 0,
    onSuccess: () => {
      console.log("OK");
    },
  });
  publish("coba", "hello world");
}

function publish(topic, payload) {
  let message = new Paho.MQTT.Message(topic);
  message.destinationName = payload;
  mqtt.send(message);
}

function onFailure(message) {
  console.log("fail");
  console.log(message);
  setTimeout(MQTTConnect, 3000);
}

function onMessageArrived(message) {
  let topic = message.destinationName;
  let payload = message.payloadString;
  const newLog = document.createElement("div");
  const textNode = document.createTextNode(
    `TOPIC: ${topic} MESSAGE: ${payload}`
  );

  if (topic == `"${topicWantToDraw}"`) {
    drawChart(JSON.parse(payload));
  }

  newLog.appendChild(textNode);
  document.getElementById("info-panel").appendChild(newLog);
}

function onConnectionLost() {
  console.log("connection loss");
}

function MQTTConnect() {
  let host_address = document.getElementById("form_hostaddress").value;
  let port_address = parseInt(
    document.getElementById("form_portaddress").value
  );

  // VALIDATE BEFORE CONTINUE

  console.log("connecting to " + host_address + " port " + port_address);
  mqtt = new Paho.MQTT.Client(
    host_address,
    port_address,
    "client_" + Math.random() * 10
  );
  let options = {
    timeout: 3,
    onSuccess: onConnect,
    onFailure: onFailure,
  };
  mqtt.onConnectionLost = onConnectionLost;
  mqtt.onMessageArrived = onMessageArrived;
  mqtt.connect(options);
}

/*
  DRAWING CHART
*/
function changeDrawTopic() {
  topicWantToDraw = document.getElementById("topic_to_draw").value;
}
function drawChart(sensorData) {
  let xValues = [];
  let yValues = [];
  var barColors = ["red", "green", "blue", "orange", "brown"];

  Object.keys(sensorData).map((key, idx) => {
    xValues.push(key);
    yValues.push(sensorData[key]);
  });

  new Chart("myChart", {
    type: "bar",
    data: {
      labels: xValues,
      datasets: [
        {
          backgroundColor: barColors,
          data: yValues,
        },
      ],
    },
    options: {
      legend: { display: false },
      tilte: {
        display: true,
        text: "Sensor Mapping",
      },
    },
  });
}

function clearPanelView() {
  $("#info-panel").empty();
}
