var getargs = function(string) {
  var list = decodeURIComponent(string.replace("+", "%20")).split("&");
  var args = {}, item, key, value;
  for (var index = 0; index < list.length; index++) {
    item = list[index].split("=", 1);
    args[item[0]] = item[1];
  }
  return args;
};
// vim: tabstop=8 expandtab shiftwidth=2 softtabstop=2
