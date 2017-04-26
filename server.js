var fs = require("fs");
var app = function(request, response) {
  var body = "";
  var url = decodeURI(request.url)
    .replace(/^\/*/, "")
    .replace(/\/[.][.]\//g, "/") || "index.html";
  console.log("got " + request.method + " for " + url);
  if (request.method == "GET") {
    fs.readFile(url, function(error, data) {
      if (error) return console.error(error);
      response.write(data);
      response.end();
    });
  } else if (request.method == "POST") {
    request.on("data", function(chunk) {body += chunk.toString();});
    req.on("end", function() {
      console.log("got POST: " + body);
      res.redirect("back");
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
