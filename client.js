// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
com.jcomeau.myturn.join = function(click) {
    console.log("handling Join on client side");
    click = click || window.event;  // for older MSIE versions
    click.preventDefault();  // don't send formdata to server
    var name = document.querySelector("input[name=name]").value;
    var newGroupName = document.querySelector("input[name=newgroup]").value;
    var groupName = document.querySelector("select[name=group]").value;
    console.log("name: " + name + ", newGroupName: " + newGroupName +
                "groupName: " + groupName);
    if (groupName == "") {
        if (newGroupName == "") {
            selectgroup.style.display = "none";
            newgroup.style.display = "table-row";
        } else {
            console.log("now populate the select with new group name");
        }
    }
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
