Candidate Name: Ahmed Khan
Candidate Number: 2255610
Project: MSc Computer Science Final Project

Both the database GUI and Flask Application have been tested on the following platforms: 

MacOS Big Sur 11.5.2
Windows 10 Pro 21H1

*************************
Installation instructions
*************************

1. Run this command to install all libraries in /server directory

"pip install -r requirements.txt"

2. If you are on Windows install SQLite Studio from https://www.sqlite.org/download.html and then manually connect to the database by pressing "Ctrl + O". 

-->If your machine is running MacOS install the 'Precompiled Binaries for Mac OS X (x86)' from https://www.sqlite.org/download.html
After that, there will be an button called "Open Database" on the top left.

--> The DB Browswer also works on Linux however I have not tested it. The notes for compiling it on Linux are here: https://github.com/sqlitebrowser/sqlitebrowser/wiki

3. To initiate the application:

"python app.py"

Note to marker:

If you have both Python 2 and Python 3 on your local machine then run the following command:

"python3 app.py"

4. The session time can be set in line 13 of "app.py"
