var fs = require("fs");
var webpage = fs.readFileSync("index.html", "utf8");
var app = function(request, response) {
  console.log("app got request");
  var body = "";
  /* try to prevent malicious users from fetching files out of webspace
   * such as /etc/passwd by making everything relative to "here" and
   * getting rid of '../'
   */
  var url = decodeURI(request.url)
    .replace(/^\/*/, "")
    .replace(/\/[.][.]\//g, "/");
  console.log("got " + request.method + " for \"" + url + "\"");
  if (request.method == "GET") {
    fs.readFile(url, function(error, data) {
      if (error) data = webpage;
      response.write(data);
      response.end();
    });
  } else if (request.method == "POST") {
    request.on("data", function(chunk) {body += chunk.toString();});
    request.on("end", function() {
      console.log("got POST: " + body);
      console.log("got POST: " + JSON.stringify(getargs(body)));
      response.statusCode = 304;  // document not modified
      response.end();
    });
  } else {
    console.error("unimplemented method: " + request.method);
    response.statusCode = 500;  // server error
    response.end();
  }
};
var server = require("http").createServer(app);
console.log("server: " + server);
var io = require("socket.io").listen(server);
var data = {"groups": []};
var getargs = function(string) {
  var list = decodeURIComponent(string.replace("+", "%20")).split("&");
  var args = {}, item, key, value;
  for (var index = 0; index < list.length; index++) {
    item = list[index].split("=", 1);
    args[item[0]] = item[1];
  }
  return args;
};
server.listen(7331);
// vim: tabstop=8 expandtab shiftwidth=2 softtabstop=2
