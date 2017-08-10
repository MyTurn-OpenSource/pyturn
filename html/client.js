// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
window.addEventListener("load", function() {
    var cjm = com.jcomeau.myturn;
    console.log("location.path: " + location.path);
    if (location.path != "/noscript") {
        cjm.websocket = new WebSocket("ws:" + location.host + "/socket.io");
        if (location.path == "/") {
            location.replace(location.href + "app");
        }
    }
});
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
