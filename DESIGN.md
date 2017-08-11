# App design guidelines

## Responsiveness

Few things are more annoying than buttons that don't work as intended, or
don't give any immediate feedback. Make everything pure HTML by default, and
only override with scripting after testing all scripts on load to make sure
they work for that browser.

Note that the pure HTML isn't expected to function properly for this app,
just that all buttons give appropriate feedback. That feedback, for example
in the case of pressing the MyTurn button, could say that the function
is unsupported for the user's platform. Adding or joining a group should
still work.

Another way to increase responsiveness, in script-capable browsers, is to
deliver all the possible "pages" in the same HTML glob, and let JavaScript 
hide/unhide sections as required.

## Tests

As indicated under "Responsiveness", a complete test suite should run at
page load, testing everything that will possibly done with JavaScript during
the execution of the app. If any test fails, an alert should be given and
the pure HTML restored.

## Race conditions

An app, even one as simple as this one, has numerous possibilities of race
conditions: a resource being changed, added, or deleted between accesses
because another thread modified it. Some of the issues and possible
solutions are discussed 
[here](http://effbot.org/zone/thread-synchronization.htm). I started out
with the "atomic operation" approach but quickly decided it was overly
complex. I'm going with the thread.Lock method now.

## Websockets

The `myturnb` app used websockets, and I may have to, but since uwsgi doesn't
allow websocket API calls except from the primary callable, it ties up the
`core` thread, meaning I can't service more than 4 clients at a time. So I
either have to use a different library, or use AJAX calls instead. For now
I'm going with AJAX.

John Comeau <jc@unternet.net> 2017-07
