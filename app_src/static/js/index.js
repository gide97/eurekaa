let futures = {
  Config: {
    Header: "System Configuration",
    Description:
      "Configure node, and Forwarder node, Stop and Run Service, Monitor Application status in realtime",
    Progress: "80",
    Link: `/appconfig`,
  },
  MqttWatcher: {
    Header: "Mqtt Watcher",
    Description: "Watch realtime data from MQTT broker and data plotting",
    Progress: "99%",
    Link: `/checkmqtt`,
  },
  Database: {
    Header: "Database Management",
    Description: "Control databases",
    Progress: "30%",
    Link: `/dbmanagement`,
  },
  Documentations: {
    Header: "Documentation of the project",
    Description: "Documenting API",
    Progress: "80%",
    Link: `/docs`,
  },
};

$(document).ready(() => {
  let cardWrapper = $("#card-wrapper");
  let _keys = Object.keys(futures);
  let cards = "";
  _keys.map((_k, idx) => {
    cards += `
      <div class='card'>
          <h2>${futures[_k]["Header"]}</h1>
          <h4>Progress ${futures[_k]["Progress"]}/100%</h4>
          <p>${futures[_k]["Description"]}</p>
          <a href= ${futures[_k]["Link"]}>__ Go to page __ </a>
      </div>
    `;
  });
  cardWrapper.html(cards);
});
