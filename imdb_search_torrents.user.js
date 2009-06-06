// ==UserScript==
// @name           IMDB: Search Torrents
// @author         Anonymous
// @namespace      http://userscripts.org/scripts/show/47385
// @description    Searches multiple torrent sites for the movie, videogame, etc
// @version        1.3
// @include        http://*.imdb.com/title/*
// ==/UserScript==

var itemTitle = document.title.substring(0,document.title.indexOf('(')-1);
if (itemTitle.search(/"/) != -1) {
 itemTitle = itemTitle.replace(/"/g, "");
}

//The Pirate Bay
var link1 = document.createElement("a");
link1.setAttribute("href", "http://thepiratebay.org/search/"+itemTitle+"/0/99/200");
link1.appendChild(document.createTextNode("Search TPB"));
link1.setAttribute("title", "Search The Pirate Bay");
document.getElementById("tn15title").appendChild(link1);
document.getElementById("tn15title").appendChild(document.createTextNode(" | "))

var link1 = document.createElement("a");
link1.setAttribute("href", "http://www.torrentz.com/search?q="+itemTitle);
link1.appendChild(document.createTextNode("Search Torrentz"));
link1.setAttribute("title", "Search Torrentz");
document.getElementById("tn15title").appendChild(link1);

