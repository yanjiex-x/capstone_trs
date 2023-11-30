function openSidetab(evt, sidetabId){
  var i, sidetabcontent, sidetablinks;
  sidetabcontent = document.getElementsByClassName("sidetabcontent");
  for(i = 0; i < sidetabcontent.length; i++){
    sidetabcontent[i].style.display = "none";
  }
  sidetablinks = document.getElementsByClassName("sidetablinks");
  for(i = 0; i < sidetablinks.length; i++){
    sidetablinks[i].className = sidetablinks[i].className.replace(" active", "");
  }
  document.getElementById(sidetabId).style.display = "block";
  evt.currentTarget.className += " active";
}

document.getElementById("defaultOpen").click();
