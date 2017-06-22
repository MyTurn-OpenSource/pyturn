// namespace this module.
if (typeof(com) == "undefined") var com = {};
if (typeof(com.jcomeau) == "undefined") com.jcomeau = {};
com.jcomeau.myturn = {};
com.jcomeau.myturn.join = function(click) {
    console.log("handling Join on client side");
    click = click || window.event;  // for older MSIE versions
    if (click) click.preventDefault();
    var name = document.querySelector("input[name=name]");
    var newGroupName = document.querySelector("input[name=newgroup]");
    var groupName = document.querySelector("select[name=group]");
    console.log("name: " + name.value +
                ", newGroupName: " + newGroupName.value +
                ", groupName: " + groupName.value);
    if (groupName.value == "") {
        if (newGroupName.value == "") {
            selectgroup.style.display = "none";
            newgroup.style.display = "table-row";
            newGroupName.setAttribute("required", "");
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
    groupform.onsubmit = cjm.join;
    wrapper.style.display = "table-cell";
});
/*
   vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
*/
