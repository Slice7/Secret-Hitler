# Rules
The rules for the game can be found [here](https://secrethitler.com/assets/Secret_Hitler_Rules.pdf).

# Setting up
### Network
Currently, the client is configured to run on the same computer as the server.  
- If you want to run the client on a different computer within the same LAN, you must change the `host` variable (in Client.py) to the server computer's name/private IP address on the network.
- If you want to run the client on a different computer across the internet, you must change the `host` variable (in Client.py) to the server computer's public IP address. You must also enable port forwarding on the server computer's network. (Remember to disable that once you're done)

Each program is also configured to use port number 12345, but you can set this to whatever you like by changing the `port` variable. It is recommended to use ports between 1024 and 65535. The server and client port numbers must match.

This program uses some simple security measures. Unless you would like to implement your own security, you must have Cryptography installed (`pip install cryptography` in the command line works).

### Files
You must have Client.py and the Assets folder in the same directory. The Server.py file can be wherever you like.

### Starting the game
Open the Server.py by navigating to its directory in the command line and entering `python Server.py`. Or, if you prefer, open it with the IDE of your choice and run from there.

Enter the number of players you would like in the game. Unless you've implemented your own security, it should spit out a key which you must then enter into each client when prompted to do so.

**[IMPORTANT: See known issue below]** Open the Client.py file for as many players as you entered before, and enter the server's key. Then enter your player name and you should now be able to choose your envelope and start playing.

# Known issue
On Windows (unable to verify for MacOS), when right-clicking and opening the client with python, the program is unable to locate the 'Assets' directory.

You must either run the client from the command line, or in your preferred IDE.

This doesn't affect the server as it doesn't access the Assets directory, so you may run it however you like.

# Outstanding
- Number of policies in each pile is not shown (refer to the server output to find this).

- The server doesn't recognise player names, only their ID numbers.

- Secret identities are not revealed at the end of the game.

- Only one secret role card is available for Fascists and Liberals.
