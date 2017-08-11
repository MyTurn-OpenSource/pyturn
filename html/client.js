// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
// no need to use `window.` anything, it is implied
addEventListener("load", function() {
    console.log("onload routine started");
    var cjm = com.jcomeau.myturn;
    console.log("location.path: " + location.path);
    if (location.path != "/noscript") {
        cjm.websocket = new WebSocket("ws:" + location.host + "/socket.io");
        // save this redirect for last, only reached if all other tests pass
        if (location.path == "/") {
            location.replace(location.href + "app");
        }
    }
});
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
