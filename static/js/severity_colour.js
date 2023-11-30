const countSol = document.getElementsByClassName("severity");
for(var i=0; i < countSol.length; i++){
  let strSol = countSol[i].textContent;
  let lastWordSol = strSol.slice(strSol.lastIndexOf(' ') + 1);
  switch (lastWordSol){
    case "Medium":
      countSol[i].style.background = "rgba(255, 205, 86, 0.2)";
      countSol[i].style.color = "#111";
      break;
    case "High":
      countSol[i].style.background = "rgba(255, 159, 64, 0.2)";
      countSol[i].style.color = "#111";
      break;
    case "Critical":
      countSol[i].style.background = "rgba(244, 67, 54, 0.2)";
      countSol[i].style.color = "#111";
  }
}

// const countHost = document.getElementsByClassName("severity_hosts");
// for(var x=0; x < countHost.length; x++){
//   let strHost = countHost[x].textContent;
//   switch(strHost){
//     case "Medium":
//       countHost[x].style.background = "#E69138";
//       countHost[x].style.color = "#FFF";
//       break;
//     case "High":
//       countHost[x].style.background = "#CC0000";
//       countHost[x].style.color = "#FFF";
//       break;
//     case "Critical":
//       countHost[x].style.background = "#990000";
//       countHost[x].style.color = "#FFF";
//   }
// }
