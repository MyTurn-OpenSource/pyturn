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

## Tests

As indicated under "Responsiveness", a complete test suite should run at
page load, testing everything that will possibly done with JavaScript during
the execution of the app. If any test fails, an alert should be given and
the pure HTML restored.
