var fs = require("fs");
var jsdom = require("node-jsdom");
var webpage = fs.readFileSync("index.html", "utf8");
var document = jsdom.jsdom(webpage);
var window = document.parentWindow;
var app = function(request, response) {
  var body = "";
  /* try to prevent malicious users from fetching files out of webspace
   * such as /etc/passwd by making everything relative to "here" and
   * getting rid of '../'
   */
  var url = decodeURI(request.url)
    .replace(/^\/*/, "")
    .replace(/\/[.][.]\//g, "/");
  console.log("got " + request.method + " for " + url);
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
      response.statusCode = 304;
      response.end();
    });
  } else {
    console.error("unimplemented method: " + request.method);
  }
};
var server = require("http").createServer(app);
console.log("server: " + server);
var io = require("socket.io").listen(server);
var data = {"groups": []};
server.listen(7331);
// vim: tabstop=8 expandtab shiftwidth=2 softtabstop=2
