console.debug("client.js starting");
// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
com.jcomeau.myturn.state = null;
com.jcomeau.myturn.pages = null;
com.jcomeau.myturn.page = null;
com.jcomeau.myturn.pagename = null;
com.jcomeau.myturn.poller = null;
com.jcomeau.myturn.username = null;
com.jcomeau.myturn.groupname = null;
com.jcomeau.myturn.groupdata = {talksession: {}, participants: {}};
// no need to use `window.` anything; it is implied
com.jcomeau.myturn.icon = "url('images/myturn-logo.png')";
com.jcomeau.myturn.debugging = [];
com.jcomeau.myturn.backgroundColor = null;
com.jcomeau.myturn.buttonBackground = null;
com.jcomeau.myturn.beat = [30, 100, 30];  // heartbeat vibration
com.jcomeau.myturn.phantom = {};
com.jcomeau.myturn.pollcount = -1;  // determines when to heartbeat
com.jcomeau.myturn.lastPulse = -1;  // updates on every heartbeat

// patch PhantomJS browser

if (typeof Element.prototype.replaceWith == "undefined") {
    Element.prototype.replaceWith = function(otherElement) {
        this.style.display = "none";
        this.parentNode.insertBefore(otherElement, this);
        this.parentNode.removeChild(this);
    };
}

// initialize vibration API for older browsers
com.jcomeau.myturn.initializeVibration = function() {
    var cjm = com.jcomeau.myturn;
    navigator.vibrate = navigator.vibrate || 
        navigator.webkitVibrate || 
        navigator.mozVibrate || 
        navigator.msVibrate ||
        (navigator.notification ? navigator.notification.vibrate : false);
    // but get rid of false desktop Chrome support -- it can't really vibrate
    if (!navigator.userAgent.match(/(Mobi|iP|Android|SCH-I800)/)) {
        console.debug("desktop browser " + navigator.userAgent +
                      ": disabling vibration");
        navigator.vibrate = false;
    }
};

com.jcomeau.myturn.getFormData = function(event, additional) {
    var formElement = event.target;
    while (formElement.tagName != "FORM") {
        console.debug("looking for FORM upstream of " + formElement.tagName);
        formElement = formElement.parentNode;
    }
    var formData = new FormData(formElement);
    for (var index = 0; index < additional.length; index++) {
        formData.append(additional[index][0], additional[index][1]);
    }
    return formData;
};

com.jcomeau.myturn.myTurn = function(event) {
    console.debug("My Turn mousedown");
    var request = new XMLHttpRequest();  // not supporting IE
    var cjm = com.jcomeau.myturn;
    var newColor = cjm.rgb(cjm.toggle(cjm.buttonBackground));
    console.debug("changing 'My Turn' background color to " + newColor);
    event.target.style.backgroundColor = newColor;
    request.open("POST", "/groups/" + cjm.groupname);
    request.responseType = "json";  // returns object
    request.onreadystatechange = function() {
        console.debug("response code " + request.readyState + ": " +
                    JSON.stringify(request.response || {}));
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var groupdata = cjm.phantom.parse(request.response);
            if (groupdata.groupname !== cjm.groupname) {
                cjm.phantom.log("groupdata: " + groupdata);
                console.debug("groupname now " + groupdata.groupname +
                            ", was: " + cjm.groupname);
                console.debug("MyTurn mousedown redirecting to report page");
                return cjm.showReport();
            }
        }
    };
    request.send(cjm.getFormData(event, [["submit", "My Turn"]]));
};

com.jcomeau.myturn.rgb = function(colorArray) {
    return "rgb(" + colorArray.join(", ") + ")";
};

com.jcomeau.myturn.toggle = function(colorArray) {
    // switch color to something significantly darker or lighter
    var newColors = colorArray.slice();  // makes a copy
    for (var index = 0; index < newColors.length; index++) {
        // can't use division here without Math.floor()
        if (newColors[index] < 128) newColors[index] <<= 1;
        else newColors[index] >>>= 1;
    }
    return newColors;
};

com.jcomeau.myturn.flash = function() {
    // ignore any args, it will get the same args as navigator.vibrate()
    var cjm = com.jcomeau.myturn;
    var newColor = cjm.rgb(cjm.toggle(cjm.backgroundColor));
    console.debug("flashing background color to " + newColor);
    cjm.page.style.backgroundColor = newColor;
    setTimeout(function() {
        newColor = cjm.rgb(cjm.backgroundColor);
        console.debug("restoring background color to " + newColor);
        cjm.page.style.backgroundColor = newColor;
    }, 50);
};

com.jcomeau.myturn.cancelRequest = function(event) {
    var request = new XMLHttpRequest();  // not supporting IE
    var cjm = com.jcomeau.myturn;
    var newColor = cjm.rgb(cjm.buttonBackground);
    console.debug("restoring 'My Turn' background color to " + newColor);
    event.target.style.backgroundColor = newColor;
    console.debug("My Turn mouseup");
    request.open("POST", "/groups/" + cjm.groupname);
    request.setRequestHeader("Content-type",
                             "application/x-www-form-urlencoded");
    request.responseType = "json";  // returns object
    request.onreadystatechange = function() {
        console.debug("response code " + request.readyState + ": " +
                    JSON.stringify(request.response || {}));
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var groupdata = cjm.phantom.parse(request.response);
            if (groupdata.groupname !== cjm.groupname) {
                cjm.phantom.log("groupdata: " + groupdata);
                console.debug("groupname now " + groupdata.groupname +
                            ", was: " + cjm.groupname);
                console.debug("MyTurn mouseup redirecting to report page");
                return cjm.showReport();
            }
        }
    };
    request.send("submit=Cancel+request&username=" + cjm.username +
                 "&groupname=" + cjm.groupname);
};

com.jcomeau.myturn.joinGroup = function(event) {
    var cjm = com.jcomeau.myturn;
    var request = new XMLHttpRequest();  // not supporting IE
    var form = event.target.parentNode;
    request.open("POST", "/groups/" + groupname);
    request.onreadystatechange = function() {
        console.debug("response code " + request.readyState + ": " +
                    JSON.stringify(request.response || {}));
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var groupdata = cjm.phantom.parse(request.response);
        }
    };
    request.send("submit=Join&username=" + username + "&group=" + groupname);
};

com.jcomeau.myturn.updateTalkSession = function() {
    var cjm = com.jcomeau.myturn;
    var request = new XMLHttpRequest();  // not supporting IE
    request.open("GET", "/groups/" + cjm.groupname);
    request.responseType = "json";  // returns object
    request.onreadystatechange = function() {
        console.debug("response code " + request.readyState + ": " +
                    JSON.stringify(request.response || {}));
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var groupdata = cjm.phantom.parse(request.response);
            if (groupdata.groupname !== cjm.groupname) {
                cjm.phantom.log("groupdata: " + groupdata);
                console.debug("groupname now " + groupdata.groupname +
                            ", was: " + cjm.groupname);
                cjm.poller = clearInterval(cjm.poller);
                console.debug("discussion over, redirecting to report page");
                return cjm.showReport();
            }
            var speaker = groupdata.talksession.speaker;
            var remaining = groupdata.talksession.remaining;
            var tick = groupdata.talksession.tick;
            var speakerStatus = document.getElementById("talksession-speaker");
            var beatHeart = false;
            speakerStatus.textContent = speaker ?
                "Current speaker is " + speaker:
                "Waiting for next speaker";
            var timeStatus = document.getElementById("talksession-time");
            // only update time at start of new quantum
            if (speaker) {
                var previousData = cjm.groupdata;
                console.debug("previous data: " + JSON.stringify(previousData));
                console.debug("participants: " + previousData.participants);
                var previousTime = 1000000;  // arbitrarily high number
                var previousSpeaker = previousData.talksession.speaker;
                if (previousSpeaker == speaker &&
                        previousData.participants[speaker]) {
                    console.debug("same speaker, checking if new quantum");
                    previousTime = previousData.participants[speaker].speaking;
                }
                var currentTime = groupdata.participants[speaker].speaking;
                console.debug("will update time field if " + currentTime +
                            " < " + previousTime);
                if (currentTime < previousTime)
                    timeStatus.textContent = new Date(
                        null, 0, 1, 0, 0, remaining).toString().split(" ")[4];
            }
            // heartbeat affected by dropped/delayed packets on purpose
            // it helps participants gauge network speed
            cjm.pollcount += 1;  // update count
            // active speaker, vibrate every query (every half second)
            if (speaker === cjm.username) beatHeart = true;
            // waiting to speak, vibrate every second
            else if (groupdata.participants[cjm.username].request)
                beatHeart = (cjm.pollcount - cjm.lastPulse >= 2) ? true : false;
            // otherwise beat every 2 seconds
            else if (cjm.pollcount - cjm.lastPulse >= 4) beatHeart = true;
            // save actual call to navigator.vibrate() to very end
            // otherwise groupdata and pollcount won't get updated
            cjm.groupdata = groupdata;
            if (beatHeart) {
                cjm.lastPulse = cjm.pollcount;
                console.debug("beating heart with vibrate or flash");
                navigator.vibrate ? navigator.vibrate(cjm.beat) : cjm.flash();
            }
        }
    };
    request.send();
};

com.jcomeau.myturn.showReport = function() {
    var cjm = com.jcomeau.myturn;
    var request = new XMLHttpRequest();  // not supporting IE
    request.open("GET", "/report/" + cjm.groupname);
    request.responseType = "document";  // returns object
    request.onreadystatechange = function() {
        console.debug("response code " + request.readyState + ": " +
                    request.response);
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var report = request.response.getElementById("report-table");
            for (var index = 0; index < cjm.pages.length; index++) {
                var page = cjm.pages[index];
                var pagename = page.getAttribute("id");
                if (pagename == "report-body") {
                    cjm.page = page;
                    cjm.pagename = pagename;
                    break;
                }
            }
            // unfortunately, elements do not have getElementById method
            cjm.page.getElementsByTagName("table")[0].replaceWith(report);
            document.querySelector("div.body").replaceWith(cjm.page);
        }
    };
    request.send();
};

com.jcomeau.myturn.getRGB = function(element) {
    if (typeof getComputedStyle != "undefined") {
        return getComputedStyle(element)
            .backgroundColor.split(/rgb\(|, |\)/)
            .slice(1, 4)  // filter out empty strings on each end
            .map(function(datum) {return parseInt(datum)});
    }
};

com.jcomeau.myturn.updateGroups = function() {
    var cjm = com.jcomeau.myturn;
    var request = new XMLHttpRequest();  // not supporting IE
    request.open("GET", "/groups");
    request.responseType = "document";
    request.onreadystatechange = function() {
        console.debug("response code " + request.readyState + ": " +
                    request.response);
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var selector = document.getElementById("group-select");
            var previous = selector.value;
            var replacement = request.response.getElementById("group-select");
            console.debug("selector: " + selector);
            console.debug("replacement: " + replacement);
            /* if there are any non-default options, and default is selected,
             * don't change to the newest group */
            if (previous || previous.length > 1) {
                console.debug("keeping already selected \""+ previous + "\"");
                /* setting selected value to what it was before...
                 * in the case that the previous selected group is no longer
                 * active, the Chrome browser will show a blank selection */
                replacement.value = previous;
            }
            if (replacement.dataset.contents != selector.dataset.contents) {
                console.debug("replacing group-select with new copy from server");
                selector.replaceWith(replacement);
            } else {
                console.debug("leaving group-select as it was, nothing changed");
            }
        }
    };
    request.send();
};

addEventListener("load", function() {
    console.debug("onload routine started");
    var cjm = com.jcomeau.myturn;
    if (navigator.userAgent.match(/PhantomJS/)) {
        // hacks to work with PhantomJS for unit testing
        cjm.phantom.log = function(message) {console.debug(message)};
        cjm.phantom.parse = JSON.parse;
    } else {
        cjm.phantom.log = function() {};
        cjm.phantom.parse = function(arg) {return arg};
    }
    cjm.phantom.log("browser is PhantomJS");
    console.debug("location: " + JSON.stringify(location));
    var path = location ? location.pathname.replace(/\/+/, "/") : "/phantom";
    console.debug("location.pathname: " + path);
    if (typeof URLSearchParams != "undefined" && location.search)
        cjm.debugging = (new URLSearchParams(location.search)).getAll("debug");
    cjm.state = "loading";
    cjm.pages = document ? document.querySelectorAll("div.body") : [];
    console.debug("pages: " + cjm.pages);
    // neither phantomjs nor htmlunit support for...of statements
    for (var index = 0; index < cjm.pages.length; index++) {
        var page = cjm.pages[index];
        if (page.style.display == "none") {
            page.parentNode.removeChild(page);
            // OK to set it visible now, it's no longer part of document
            page.style.display = "";
        } else {
            cjm.page = page;
            cjm.pagename = page.getAttribute("id");
            console.debug("page loaded: " + cjm.pagename);
        }
    }
    // save background color of active div.body element for flasher to work
    cjm.backgroundColor = cjm.getRGB(cjm.page);
    // page-specific setup
    if (cjm.pagename == "joinform-body") {
        cjm.updateGroups();  // do it once now to make sure it works
        cjm.poller = setInterval(cjm.updateGroups, 500);
    } else if (cjm.pagename == "talksession-body") {
        /* get rid of "Check status" button, and make "My turn"
         * button activate on button-down and button-up */
        cjm.username = document.querySelector(
            "input[name=username][type=hidden]").value;
        cjm.groupname = document.querySelector(
            "input[name=groupname][type=hidden]").value;
        cjm.updateTalkSession(); // do it once now to make sure it works
        var myturnButton = document.getElementById("myturn-button");
        cjm.buttonBackground = cjm.getRGB(myturnButton);
        myturnButton.style.color = "transparent";
        myturnButton.style.height = "33vmin";
        myturnButton.style.width = "33vmin";
        myturnButton.style.backgroundImage = cjm.icon;
        myturnButton.style.backgroundSize = "cover";
        myturnButton.style.outline = "none";
        myturnButton.addEventListener("mousedown", cjm.myTurn);
        myturnButton.addEventListener("touchstart", cjm.myTurn);
        myturnButton.addEventListener("mouseup", cjm.cancelRequest);
        myturnButton.addEventListener("touchend", cjm.cancelRequest);
        myturnButton.onclick = function(event) {  // disable click event
            console.debug("trying to prevent click event from functioning");
            event.preventDefault();
            event.stopPropagation();
            return false;
        };
        var checkStatus = document.getElementById("check-status");
        checkStatus.parentNode.removeChild(checkStatus);
        cjm.poller = setInterval(cjm.updateTalkSession, 500);
        cjm.initializeVibration();
    }
    // save this redirect for last, only reached if all other tests pass
    if (location && path == "/") location.pathname = "/app";
    cjm.state = "loaded";
});
if (typeof phantom != "undefined") {  // for phantomjs command-line testing
    console.debug("phantom exiting now");
    phantom.exit();
}
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
