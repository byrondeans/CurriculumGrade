I had the idea for this business after doing market research and discovering there doesn't seem to be a site other than MasterClass that really focuses on the world's top experts doing the teaching.  After years of studying Tony Robbins, with his enormous emphasis on learning from the best, and emulating their bodies and mannerisms to achieve greatness, that convinced me I was on to a good idea.  I decided to add social networking, so the site would be like a LinkedIn for education, and decided to open the site up to any content producers, with the idea that I would seek to profit not only from my idea for education content (by opening a channel on the site, competing with other content producers, but, in my imagination, beating them based on quality), but from the site itself, with its potential to be a social networking hit.  My initial idea was to have professors like François Englert and Peter W. Higgs teach lessons for secondary and primary students.  There are a combination of reasons I decided to go with secondary and primary lessons first: mainly, they're taught to all kids, whereas at the university level, the audience narrows dramatically, and also secondarily because they're less controversial to teach; the closer you are to advanced physics, the closer you are to nuclear knowledge and other defense-related subjects.


I created the site in the middle of doing a Harvard certificate in Python and JavaScript, using Python/Flask and WebSockets taught in the course.  After finishing it, I approached a large number of investors and was turned down, so after over two years, I decided to make it open source.

If anyone out there is interested, I can help them set this web app up and host it, or I can modify it for a fee.

INSTALLATION INSTRUCTIONS
On my VPS, I use Apache2, but here I will just explain how to get it going on a Mac.  On my Mac, here's how I do it: first, use the database file to create the database in postgresql (assuming you have postgresql installed and working).  Then, put the application in a folder and assuming you have venv installed and pip3 installed, run python3 -m venv venv.  Then, enter your venv with . venv/bin/activate and run the following:

pip3 install flask

pip3 install requests

pip3 install flask_session

pip3 install sqlalchemy

pip3 install flask_socketio

Then just type flask run.

NOTE: Although on my business's Linux VPS and on an older venv installation on my Mac, the websockets work, when I justed tried the web app (28 Jul 2022) with the latest versions of everything in a new venv, the websockets part produced an error.  Some of the versions of the above on the older venv on my Mac that work are:

flask = 1.1.2

requests = 2.24.0

flask_session = 0.3.2

sqlalchemy = 1.3.19

flask_socketio = 4.3.1

Results will vary based on your operating system over time.  As of this date, the web app is about two years old and not working perfectly on new software, and that will only get worse over time.
