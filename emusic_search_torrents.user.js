// ==UserScript==
// @name           Emusic : Search Torrents
// @namespace      http://vellut.com/greasemonkey
// @include        http://*.emusic.com/album/*
// ==/UserScript==
//

var itemTitle = null;
var itemTitles= document.getElementsByTagName('a');
for(var i = 0; i < itemTitles.length ; i++) {
  if(itemTitles[i].href.indexOf("/artist/") >= 0) {
    itemTitle = itemTitles[i].innerHTML;
    break;
  }
}

if(!itemTitle)
  return;

if (itemTitle.search(/"/) != -1) {
 itemTitle = itemTitle.replace(/"/g, "");
}

//The Pirate Bay
var link1 = document.createElement("a");
link1.setAttribute("href", "http://thepiratebay.org/search/"+itemTitle+"/0/99/200");
link1.appendChild(document.createTextNode("Search TPB"));
link1.setAttribute("title", "Search The Pirate Bay");
document.getElementsByClassName("contentHead")[0].appendChild(link1);
document.getElementsByClassName("contentHead")[0].appendChild(document.createTextNode(" | "))

var link1 = document.createElement("a");
link1.setAttribute("href", "http://www.torrentz.com/search?q="+itemTitle);
link1.appendChild(document.createTextNode("Search Torrentz"));
link1.setAttribute("title", "Search Torrentz");
document.getElementsByClassName("contentHead")[0].appendChild(link1);
