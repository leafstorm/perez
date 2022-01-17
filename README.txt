# Perez

Perez is a Web-based client for the Gemini and Titan protocols. The goal is to become the first client that supports WYSIWYG editing for Gemini space. Implementing it as a Web application, even though it seems very un-Gemini-like on the surface, allows the client to reach that goal faster. My conceptual roadmap for Perez looks like this:

* Implement Perez as a basic Gemini proxy server in Python.
* Integrate a WYSIWYG editor into the rendered HTML.
* Add support for uploading the edited HTML as Gemtext via Titan.
* Add support for client certificates.

At that point the project's core goal will be achieved. If developers of other Gemini clients see the value, I would hope that they integrate similar editing workflows into their own clients. However, the project could also continue developing as a standalone application:

* Improve the appearance of the generated HTML (likely taking inspiration from Lagrange).
* Migrate history management from the browser chrome into Perez's JavaScript.
* Migrate tab management from the browser chrome into Perez's JavaScript.
* Implement additional browser features (such as bookmarks).
* Port the application to Electron so it can run standalone, which would include porting the networking code from Python to JavaScript.

The latter part of this roadmap may end up requiring more JavaScript than I am comfortable with.


## How do I run it?

Perez is written in Python and requires Poetry to manage its dependencies. Once you have Python and Poetry installed, run the "poetry install" command in the source repository to download the dependencies. Then, run the "poetry run perez-proxy" command to start the server, which runs on port 8965. Visit http://localhost:8965/gemini.circumlunar.space/ to get started. (Or another Gemini server of your choice.)

=> https://python-poetry.org/ Poetry


## Why is it named Perez?

Perez is one of four twins mentioned in the Bible, who is born (along with his brother Zerah) in Genesis 38:27-30. If I develop server software to accompany Perez, it will be named Zerah. The other pair of twins mentioned in the Bible are Jacob and Esau (born in Genesis 25:19-26), who could also become the namesakes of a Gemini client/server pair in the future. :-)
