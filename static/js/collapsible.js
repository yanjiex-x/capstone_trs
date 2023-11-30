let noOfCharacters = 120;
let contents = document.querySelectorAll(".contents");
// console.log(contents);
contents.forEach(content => {
  var value = content.textContent.replace(/\s{2,}/g,' ');
  let actualCount = value.length;
  console.log(actualCount);
  if(actualCount < noOfCharacters){
    content.nextElementSibling.style.display = "none";
  }
  else{
    let displayText = value.slice(0, noOfCharacters);
    let moreText = value.slice(noOfCharacters);
    content.innerHTML = `${displayText}<span class="dots">...</span><span class="hide more">${moreText}</span>`
  }
});

function showMore(btn){
  let subsection = btn.parentElement;
  subsection.querySelector(".dots").classList.toggle("hide");
  subsection.querySelector(".more").classList.toggle("hide");
  btn.textContent == "Show More" ? btn.textContent = "Show Less" : btn.textContent = "Show More";
}
