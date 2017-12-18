console.log("client.js starting");
// initialize vibration API for older browsers
navigator.vibrate = navigator.vibrate || 
    navigator.webkitVibrate || 
    navigator.mozVibrate || 
    navigator.msVibrate ||
    (navigator.notification ? navigator.notification.vibrate : function() {
        return false
    });
// but get rid of false desktop Chrome support -- it can't really vibrate
if (!navigator.userAgent.match(/(Mobi|iP|Android|SCH-I800)/)) {
    console.log("desktop browser " + navigator.userAgent +
                ": disabling vibration");
    navigator.vibrate = function() {return false};
}
console.log("vibration enabled: " + navigator.vibrate);
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
com.jcomeau.myturn.beat = [30, 100, 30];  // heartbeat vibration

com.jcomeau.myturn.myTurn = function() {
    var request = new XMLHttpRequest();  // not supporting IE
    var cjm = com.jcomeau.myturn;
    console.log("My Turn mousedown");
    request.open("POST", "/groups/" + cjm.groupname);
    request.setRequestHeader("Content-type",
                             "application/x-www-form-urlencoded");
    request.responseType = "json";  // returns object
    request.onreadystatechange = function() {
        console.log("response code " + request.readyState + ": " +
                    JSON.stringify(request.response || {}));
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var groupdata = request.response;
            if (groupdata.groupname !== cjm.groupname) {
                console.log("groupdata: " + groupdata);
                console.log("groupname now " + groupdata.groupname +
                            ", was: " + cjm.groupname);
                console.log("MyTurn mousedown redirecting to report page");
                return cjm.showReport();
            }
        }
    };
    request.send("submit=My+Turn&username=" + cjm.username + "&groupname=" +
                 cjm.groupname);
};

com.jcomeau.myturn.flash = function() {
    var cjm = com.jcomeau.myturn;
    var newColor, newColors = cjm.backgroundColor.slice();
    if (cjm.backgroundColor && cjm.backgroundColor.length == 3) {
        for (var index = 0; index < newColors.length; index++) {
            // can't use division here without Math.floor()
            if (newColors[index] < 128) newColors[index] <<= 1;
            else newColors[index] >>>= 1;
        }
        newColor = "rgb(" + newColors.join(", ") + ")";
        console.log("flashing background color to " + newColor);
        document.body.style.backgroundColor = newColor;
        setTimeout(function() {
            newColor = "rgb(" + cjm.backgroundColor.join(", ") + ")";
            console.log("restoring background color to " + newColor);
            document.body.style.backgroundColor = newColor;
        }, 10);
    }
};

com.jcomeau.myturn.cancelRequest = function() {
    var request = new XMLHttpRequest();  // not supporting IE
    var cjm = com.jcomeau.myturn;
    console.log("My Turn mouseup");
    request.open("POST", "/groups/" + cjm.groupname);
    request.setRequestHeader("Content-type",
                             "application/x-www-form-urlencoded");
    request.responseType = "json";  // returns object
    request.onreadystatechange = function() {
        console.log("response code " + request.readyState + ": " +
                    JSON.stringify(request.response || {}));
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var groupdata = request.response;
            if (groupdata.groupname !== cjm.groupname) {
                console.log("groupdata: " + groupdata);
                console.log("groupname now " + groupdata.groupname +
                            ", was: " + cjm.groupname);
                console.log("MyTurn mouseup redirecting to report page");
                return cjm.showReport();
            }
        }
    };
    request.send("submit=Cancel+request&username=" + cjm.username +
                 "&groupname=" + cjm.groupname);
};

com.jcomeau.myturn.updateTalkSession = function() {
    var cjm = com.jcomeau.myturn;
    var request = new XMLHttpRequest();  // not supporting IE
    request.open("GET", "/groups/" + cjm.groupname);
    request.responseType = "json";  // returns object
    request.onreadystatechange = function() {
        console.log("response code " + request.readyState + ": " +
                    JSON.stringify(request.response || {}));
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var groupdata = request.response;
            if (groupdata.groupname !== cjm.groupname) {
                console.log("groupdata: " + groupdata);
                console.log("groupname now " + groupdata.groupname +
                            ", was: " + cjm.groupname);
                cjm.poller = clearInterval(cjm.poller);
                console.log("discussion over, redirecting to report page");
                return cjm.showReport();
            }
            var speaker = groupdata.talksession.speaker;
            var remaining = groupdata.talksession.remaining;
            var tick = groupdata.talksession.tick;
            var speakerStatus = document.getElementById("talksession-speaker");
            speakerStatus.textContent = speaker ?
                "Current speaker is " + speaker:
                "Waiting for next speaker";
            var timeStatus = document.getElementById("talksession-time");
            // only update time at start of new quantum
            if (speaker) {
                var previousData = cjm.groupdata;
                console.log("previous data: " + JSON.stringify(previousData));
                console.log("participants: " + previousData.participants);
                var previousTime = 1000000;  // arbitrarily high number
                var previousSpeaker = previousData.talksession.speaker;
                if (previousSpeaker == speaker &&
                        previousData.participants[speaker]) {
                    console.log("same speaker, checking if new quantum");
                    previousTime = previousData.participants[speaker].speaking;
                }
                var currentTime = groupdata.participants[speaker].speaking;
                console.log("will update time field if " + currentTime +
                            " < " + previousTime);
                if (currentTime < previousTime)
                    timeStatus.textContent = new Date(
                        null, 0, 1, 0, 0, remaining).toString().split(" ")[4];
            }
            cjm.groupdata = groupdata;
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
        console.log("response code " + request.readyState + ": " +
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

com.jcomeau.myturn.updateGroups = function() {
    var request = new XMLHttpRequest();  // not supporting IE
    request.open("GET", "/groups");
    request.responseType = "document";
    request.onreadystatechange = function() {
        console.log("response code " + request.readyState + ": " +
                    request.response);
        if (request.readyState == XMLHttpRequest.DONE &&
                request.status == 200) {
            var selector = document.getElementById("group-select");
            var previous = selector.value;
            var replacement = request.response.getElementById("group-select");
            console.log("selector: " + selector);
            console.log("replacement: " + replacement);
            /* if there are any non-default options, and default is selected,
             * don't change to the newest group */
            if (previous || previous.length > 1) {
                console.log("keeping already selected \""+ previous + "\"");
                /* setting selected value to what it was before...
                 * in the case that the previous selected group is no longer
                 * active, the Chrome browser will show a blank selection */
                replacement.value = previous;
            }
            if (replacement.dataset.contents != selector.dataset.contents) {
                console.log("replacing group-select with new copy from server");
                selector.replaceWith(replacement);
            } else {
                console.log("leaving group-select as it was, nothing changed");
            }
        }
    };
    request.send();
};

addEventListener("load", function() {
    console.log("onload routine started");
    var cjm = com.jcomeau.myturn;
    console.log("location: " + JSON.stringify(location));
    var path = location ? location.pathname.replace(/\/+/, "/") : "/phantom";
    console.log("location.pathname: " + path);
    if (typeof URLSearchParams != "undefined" && location.search)
        cjm.debugging = (new URLSearchParams(location.search)).getAll("debug");
    if (typeof getComputedStyle != "undefined") {
        cjm.backgroundColor = getComputedStyle(document.body)
            .lightingColor.split(/rgb\(|, |\)/)
            .filter(function(datum) {return datum})
            .map(function(datum) {return parseInt(datum)});
    }
    // test vibration and set flasher if none enabled
    navigator.vibrate(0) || (navigator.vibrate = cjm.flash);
    if (path != "/noscript") {
        cjm.state = "loading";
        cjm.pages = document ? document.querySelectorAll("div.body") : [];
        console.log("pages: " + cjm.pages);
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
                console.log("page loaded: " + cjm.pagename);
            }
        }
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
            myturnButton.style.color = "transparent";
            myturnButton.style.height = "33vmin";
            myturnButton.style.width = "33vmin";
            myturnButton.style.backgroundImage = cjm.icon;
            myturnButton.style.backgroundSize = "cover";
            myturnButton.addEventListener("mousedown", cjm.myTurn);
            myturnButton.addEventListener("touchstart", cjm.myTurn);
            myturnButton.addEventListener("mouseup", cjm.cancelRequest);
            myturnButton.addEventListener("touchend", cjm.cancelRequest);
            myturnButton.onclick = function(event) {  // disable click event
                console.log("trying to prevent click event from functioning");
                event.preventDefault();
                event.stopPropagation();
                return false;
            };
            var checkStatus = document.getElementById("check-status");
            checkStatus.parentNode.removeChild(checkStatus);
            cjm.poller = setInterval(cjm.updateTalkSession, 500);
        }
        // save this redirect for last, only reached if all other tests pass
        if (location && path == "/") location.pathname = "/app";
        cjm.state = "loaded";
    }
});
if (typeof phantom != "undefined") {  // for phantomjs command-line testing
    console.log("phantom exiting now");
    phantom.exit();
}
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
