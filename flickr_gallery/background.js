var flickrAPIKey = "3a06bcc6bd84bcc9622902f8baa8b55f";
var getSizesUrl = "http://api.flickr.com/services/rest/?api_key=" + flickrAPIKey +
    "&nojsoncallback=1&method=flickr.photos.getSizes&format=json&photo_id=";
var flickrTabIndex = 0;
var flickrTabs = [];
var flickrGalleryHtml = "";

function checkForValidUrl(tabId, changeInfo, tab) {
    if (tab.url.indexOf('gvlt.wordpress.com/wp-admin') > -1) {
        chrome.pageAction.show(tabId);
    } else {
        chrome.pageAction.hide(tabId);
    }
};

function createFlickrGallery(tab) {
  chrome.tabs.query({windowId : chrome.windows.WINDOW_ID_CURRENT, url: "*://*.flickr.com/photos/*" },
	function(tabs) {
        if(tabs.length > 0) {
            flickrGalleryHtml = "";
            flickrTabIndex = 0;
            flickrTabs = tabs;

            nextFlickrTab();
        } else {
            console.log("No Flickr tabs found");
        }
	});
}



function nextFlickrTab() {
    var photoId = getPhotoId(flickrTabs[flickrTabIndex].url);
    console.log("PhotoId " + photoId);
    
    if(photoId && !isNaN(parseInt(photoId))) {
        getFlickrPhotoSizes(photoId);
    } else {
        checkConditionForNextFlickrTab(false);
    }
}

function getPhotoId(url) {
    var paths = url.split("://")[1].split("/");
    if(paths.length >= 3) {
        var photoId = paths[3];
        return photoId;
    }
    return null;
}

function getFlickrPhotoSizes(photoId) {
    var req = new XMLHttpRequest();
    req.open("GET", getSizesUrl + photoId, true);
    req.onload = addToFlickrGallery;
    req.send(null);
}

function addToFlickrGallery(e) {
    var sResponse = e.target.responseText;
    var response = JSON.parse(sResponse);
    if(response.stat == "ok") {
        console.log("FlickAPI call returned");
        var sizes = response.sizes.size;
        var url = null;
        var width = null;
        var height = null;
        for(var i = 0 ; i < sizes.length ; i++) {
            if(sizes[i].label == "Medium") {
                url = sizes[i].source;
                width = sizes[i].width;
                height = sizes[i].height;
                console.log("URL :" + url);
            }
        }
        if(url) {
            flickrGalleryHtml += "<a href=\"" + flickrTabs[flickrTabIndex].url +
                "\"><img src=\"" + url + "\" width=\"" + width + "\" height=\"" + height +
                "\" class=\"alignnone\" /></a>";
            chrome.tabs.remove(flickrTabs[flickrTabIndex].id);
            checkConditionForNextFlickrTab(true);
            return;
        }
    }
    
    checkConditionForNextFlickrTab(false);
}

function checkConditionForNextFlickrTab(newAdded) {
    flickrTabIndex++;
    if(flickrTabIndex < flickrTabs.length) {
        if(newAdded) {
            flickrGalleryHtml += "\n\n";
        }
        nextFlickrTab();
    } else {
        copyToClipboard(flickrGalleryHtml);
    }
}


function copyToClipboard(str) {
    document.oncopy = function(event) {
        console.log("Copy done!");
        event.clipboardData.setData("text/plain", str);
        event.preventDefault();
        document.oncopy = null;
    };
    document.execCommand("Copy", false, null);
}


chrome.tabs.onUpdated.addListener(checkForValidUrl);

chrome.pageAction.onClicked.addListener(createFlickrGallery);