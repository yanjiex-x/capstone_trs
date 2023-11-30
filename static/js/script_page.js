function search(){
  var input, filter, ul, li, button, i, textValue;
  input = document.getElementById("search_list");
  filter = input.value.toUpperCase();
  ul = document.getElementById("app_list");
  li = ul.getElementsByTagName("li");
  for(i = 0; i < li.length; i++){
    button = li[i].getElementsByTagName("button")[0];
    textValue = button.textContent || button.innerText;
    if(textValue.toUpperCase().indexOf(filter) > -1){
      li[i].style.display = "";
    }
    else {
      li[i].style.display = "none";
    }
  }
}

function openDiv(evt, divName) {
  var i, listcontent, listlinks;
  listcontent = document.getElementsByClassName("listcontent");
  for (i = 0; i < listcontent.length; i++) {
    listcontent[i].style.display = "none";
  }
  listlinks = document.getElementsByClassName("listlinks");
  document.getElementById(divName).style.display = "block";
}
