let clock = document.getElementById("content");
let alerted = false;

function hello_there() {
  fetch("/feed")
    .then((response) => {
      response.text().then((t) => {
        document.getElementById("content").innerHTML = t;
      });
    })
    .catch(() => {
      console.log("Ejecución terminada");
      document.title = "Ejecución terminada";
      clearInterval(interval);
      if (alerted == false) {
        alerted = true;
        //alert("VCM ha terminado la ejecución");
      }
    });
}

let interval = setInterval(hello_there, 200);
// hello_there();
