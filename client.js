// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
com.jcomeau.myturn.join = function(click) {
    console.log("handling Join on client side");
    click = click || window.event;  // for older MSIE versions
    click.preventDefault();  // don't send formdata to server
    console.log("click: " + JSON.stringify(click));
    var target = click.target || click.srcElement;  // also for MSIE
    console.log("target: " + JSON.stringify(target));
    return false;  // works even on very old browsers to prevent default action
};
window.addEventListener("load", function() {
    var cjm = com.jcomeau.myturn;
    document.body.className = "";
    loadindicator.style.display = "none";
    wrapper.style.display = "table-cell";
    document.querySelector("input[value=Join]").onclick = cjm.join;
});
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
