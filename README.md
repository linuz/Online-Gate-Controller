This project is to allow users to control their remote controlled gates from a Raspberry Pi.

Users can hook their RF remote to the Raspberry Pi and use this project to allow visitors to open the gates from their smartphone by visiting a specific URL meant for that visitor.

gate_controller_server.py = Starts a web server on a specific port. Will watch for specific requests and opens the gate of the correct request is seen

visitor_access_manager.py = Will create and remove visitor URLs for you

visitors.txt = Default file to store visitors and their unique URLs

settings.cfg = Contains all the settings needed for this project

logs/ = Web server access log files as well as visitor access logs
