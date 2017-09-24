// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
// no need to use `window.` anything; it is implied
addEventListener("load", function() {
    console.log("onload routine started");
    var cjm = com.jcomeau.myturn;
    var path = location.pathname.replace(/\/+/, "/");
    console.log("location: " + JSON.stringify(location));
    console.log("location.pathname: " + path);
    if (path != "/noscript") {
        // save this redirect for last, only reached if all other tests pass
        if (path == "/") {
            location.replace(location.href + "app");
        }
    }
});
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
