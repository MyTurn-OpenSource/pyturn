var express = require('express');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io')(server);
var data = {"groups": []};

app.post("/", function(req, res, next) {
  var body = "";
  req.on("data", function(chunk) {body += chunk.toString();});
  req.on("end", function() {
    console.log("got POST: " + body);
    res.redirect("back");
  });
});

app.use(express.static(__dirname + '/'));
server.listen(7331);
/*
# vim tabstop=8 expandtab shiftwidth=2 softtabstop=2
*/
