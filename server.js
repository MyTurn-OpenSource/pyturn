var express = require('express');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io')(server);

app.post("/", function(req, res, next) {
  console.log("got POST");
});

app.use(express.static(__dirname + '/'));
server.listen(0xf331);
/*
# vim tabstop=8 expandtab shiftwidth=2 softtabstop=2
*/
