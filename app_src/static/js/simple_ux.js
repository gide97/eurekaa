function showMenuHandler() {
  let navmenu = document.getElementById("nav-menu");
  navmenu.classList.toggle("slide");
}

window.onscroll = () => {
  let navbar = document.getElementById("navbar");
  let headerHeight = document.getElementById("header-page").offsetHeight;
  let y_ref = headerHeight - navbar.offsetHeight;
  let burger = document.querySelectorAll(".ham-bt span");

  var index = 0;
  var length = burger.length;
  if (window.scrollY > y_ref) {
    navbar.style.backgroundColor = "#333333";
    navbar.style.color = "white";

    for (index; index < length; index++) {
      burger[index].style.backgroundColor = "white";
    }
  } else {
    navbar.style.backgroundColor = "white";
    navbar.style.color = "#333333";
    for (index; index < length; index++) {
      burger[index].style.backgroundColor = "#333333";
    }
  }
};

function printMousePos(event) {
  if (document.getElementById("show-menu").checked) {
    //   console.log("clientX: " + event.clientX + " - clientY: " + event.clientY);
    let navmenu = document.getElementById("nav-menu");
    if (event.clientX < navmenu.offsetWidth) {
      console.log("Hide menu cause external click");
      document.getElementById("show-menu").checked = false;
      showMenuHandler();
    }
  }
}

document.addEventListener("click", printMousePos);
