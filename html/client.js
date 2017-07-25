// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
window.addEventListener("load", function() {
    var cjm = com.jcomeau.myturn;
    // leave the following 4 lines for last...
    // they turn off the load indicator and show the input form
    document.body.className = "";
    loadindicator.style.display = "none";
    groupform.onsubmit = cjm.join;
    wrapper.style.display = "table-cell";
});
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
