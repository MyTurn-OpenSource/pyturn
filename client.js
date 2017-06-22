// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
com.jcomeau.myturn.join = function(click) {
    click = click || window.event;  // for older MSIE versions
    if ("bubbles" in click) click.stopPropagation();
    else click.cancelBubble = true;  // MSIE < 9
    var target = click.target || click.srcElement;  // also for MSIE
    console.log("event: " + JSON.stringify(click));
    console.log("target: " + JSON.stringify(target));
};
window.addEventListener("load", function() {
    var cjm = com.jcomeau.myturn;
    document.body.className = "";
    loadindicator.style.display = "none";
    wrapper.style.display = "table-cell";
    document.querySelector("input[name=Join]").addEventListener(
        "click", cjm.join);
});
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
