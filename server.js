var fs = require("fs");
var webpage = fs.readFileSync("index.html", "utf8");
var data = {"groups": []};
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
  var args, group;
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
      if ((args = getargs(body))["submit"] == "Join") {
        console.error("client-side js for " + request.headers["user-agent"] +
          " should have trapped this");
        response.statusCode = 500;
        response.write("We have logged this error where our developers" +
          " will be able to see it. Hopefully it will be resolved soon." +
          " Data received: " + JSON.stringify(getargs(body)));
        response.end();
      }
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
io.sockets.on("connection", function(socket) {
  console.log("received a connection")
  socket.on("join", function(packet) {
    console.log("got 'join' packet: " + JSON.stringify(packet));
    socket.join(packet.group);
    console.log("adding " + packet.name + " to group " + packet.group);
    try {
      data.groups[packet.group].members.push(packet.name);
      data.groups[packet.group].started = true;
      io.sockets.in(packet.group).emit("session underway");
    } catch (noSuchGroup) {
      console.log("error adding " + packet.name + " to group " + packet.group +
                  ": no such group? (" + noSuchGroup + ")");
    }
    console.log(JSON.stringify(data));
  });
});
var getargs = function(string) {
  var list = decodeURIComponent(string.replace("+", "%20")).split("&");
  console.log("list: " + JSON.stringify(list));
  var args = {}, item, offset, key, value;
  for (var index = 0; index < list.length; index++) {
    item = list[index];
    offset = item.indexOf("=");
    key = item.substring(0, offset);
    value = item.substring(offset + 1);
    console.log(key + "=" + value);
    args[key] = value;
  }
  return args;
};
server.listen(7331);
// vim: tabstop=8 expandtab shiftwidth=2 softtabstop=2
