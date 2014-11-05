url=window.location;
p=/.+(http.+)$/
if(m=p.exec(url)) {
	newUrl=m[1]
	window.location=newUrl;
} else {
	alert("Problem in bypass_adpage extension");
}