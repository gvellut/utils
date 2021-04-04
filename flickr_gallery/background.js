var flickrAPIKey = "3a06bcc6bd84bcc9622902f8baa8b55f";
var getSizesUrl = "https://api.flickr.com/services/rest/?api_key=" + flickrAPIKey +
    "&nojsoncallback=1&method=flickr.photos.getSizes&format=json&photo_id=";
var getInfoUrl = "https://api.flickr.com/services/rest/?api_key=" + flickrAPIKey +
    "&nojsoncallback=1&method=flickr.photos.getInfo&format=json&photo_id=";


function checkForValidUrl(tabId, changeInfo, tab) {
    if (tab.url.indexOf('gvlt.wordpress.com/wp-admin') > -1 
        || tab.url.indexOf('wordpress.com/posts/gvlt.wordpress.com') > -1) {
        chrome.pageAction.show(tabId);
    } else {
        chrome.pageAction.hide(tabId);
    }
};

function createFlickrGallery(tab) {
  chrome.tabs.query({windowId : chrome.windows.WINDOW_ID_CURRENT, url: "*://*.flickr.com/photos/*" },
	async function(tabs) {
        if(tabs.length > 0) {
            let flickrGalleryHtml = "";
            for(let i = 0; i < tabs.length; i++) {
                let tabUrl = tabs[i].url;
                let photoId = getPhotoId(tabUrl);
                console.log("PhotoId " + photoId);
                
                if(photoId && !isNaN(parseInt(photoId))) {
                    fragment = await getFlickrGalleryFragment(photoId, tabUrl);
                    if(!fragment) {
                        // keep the rest of the tabs
                        break;
                    }

                    if(flickrGalleryHtml) {
                        flickrGalleryHtml += "\n\n";
                    }
                    flickrGalleryHtml += fragment

                    // copy after each photo
                    copyToClipboard(flickrGalleryHtml);

                    chrome.tabs.remove(tabs[i].id);
                }
            }

            notifyUser();
        } else {
            console.log("No Flickr tabs found");
        }
	});
    
    var opt = {
    type: "basic",
    title: "Flickr gallery ready",
    message: "The HTML has been copied to the clipboard.",
    iconUrl: "icon128.png"
    };
    
}

function getPhotoId(url) {
    var paths = url.split("://")[1].split("/");
    if(paths.length >= 3) {
        var photoId = paths[3];
        return photoId;
    }
    return null;
}

async function getFlickrGalleryFragment(photoId, linkUrl) {
    try {
        let response = null;
        
        response = await makeRequest("GET", getInfoUrl + photoId);
        response = JSON.parse(response);

        if(response.stat != "ok") {
            console.log("Info not OK");
            return false;
        }

        let title = response.photo.title._content

        response = await makeRequest("GET", getSizesUrl + photoId);
        response = JSON.parse(response);

        if(response.stat != "ok") {
            console.log("Size not OK");
            return false;
        }

        let sizes = response.sizes.size;

        let url = null;
        let width = null;
        let height = null;
        for(let i = 0 ; i < sizes.length ; i++) {
            if(sizes[i].label == "Medium") {
                url = sizes[i].source;
                width = sizes[i].width;
                height = sizes[i].height;
    
                console.log("URL :" + url);
            }
        }

        if(url) {
            flickrGalleryHtml_fragment = "<a href=\"" + linkUrl +
                "\"><img src=\"" + url + "\" width=\"" + width + "\" height=\"" + height +
                "\" title=\"" + escapeAttribute(title)  + "\" class=\"alignnone\" /></a>";
            return flickrGalleryHtml_fragment;
        }

        console.log("Medium size not found");
        return false;
        
    } catch(error) {
        console.log(error);
        return false;
    }

}

function makeRequest(method, url, timeout = 5) {
    return new Promise(function (resolve, reject) {
        let xhr = new XMLHttpRequest();
        xhr.timeout = timeout * 1000;
        xhr.open(method, url);
        xhr.onload = function () {
            if (this.status >= 200 && this.status < 300) {
                resolve(xhr.response);
            } else {
                reject({
                    status: this.status,
                    statusText: xhr.statusText
                });
            }
        };
        xhr.onerror = function () {
            reject({
                status: this.status,
                statusText: xhr.statusText
            });
        };
        xhr.send();
    });
}


function escapeAttribute(string) {
    return string.replace(/&/g,"&amp;").replace(/"/g, "&quot;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/'/g,"&apos;");
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

function notifyUser() {
    
    let opt = {
        type: "basic",
        title: "Flickr gallery ready",
        message: "The HTML has been copied to the clipboard.",
        iconUrl: "icon128.png"
    };
    
    chrome.notifications.create("", opt, function(notificationId){});

}


chrome.tabs.onUpdated.addListener(checkForValidUrl);

chrome.pageAction.onClicked.addListener(createFlickrGallery);
