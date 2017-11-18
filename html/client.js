// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
com.jcomeau.myturn.state = null;
com.jcomeau.myturn.pages = null;
com.jcomeau.myturn.page = null;
com.jcomeau.myturn.pagename = null;
com.jcomeau.myturn.storedPages = [];
com.jcomeau.myturn.poller = null;
com.jcomeau.myturn.username = null;
com.jcomeau.myturn.groupname = null;
// no need to use `window.` anything; it is implied
com.jcomeau.myturn.updateTalkSession = function() {
    var request = new XMLHttpRequest();  // not supporting IE
    request.open("GET", "/groups/" + com.jcomeau.myturn.groupname);
    request.responseType = "json";  // returns object
    request.onreadystatechange = function() {
        console.log("response code " + request.readyState + ": " +
                    request.response);
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
    var path = location.pathname.replace(/\/+/, "/");
    console.log("location: " + JSON.stringify(location));
    console.log("location.pathname: " + path);
    if (path != "/noscript") {
        cjm.state = "loading";
        cjm.pages = document.querySelectorAll("div.body");
        console.log("pages: " + cjm.pages);
        for (var page of cjm.pages) {
            if (page.style.display == "none") {
                cjm.storedPages.push(page);
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
            cjm.poller = setInterval(cjm.updateTalkSession, 500);
        }
        // save this redirect for last, only reached if all other tests pass
        if (path == "/") location.replace(location.href + "app");
        cjm.state = "loaded";
    }
});
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
