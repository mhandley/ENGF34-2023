# Welcome to Networked Pong

This game uses UDP ports 9872 and 9873 - two ports are used to allow
local testing on localhost, because both pong instances cannot open
the same port.  This means we need to manually select who is player 1
and who is player 2. This differs from the mechanisms described in the
pong specifications.  Player 2 must specify the "-s" flag when
starting pong, whereas player 1 must not specify "-s".

Other command line flags:

`-a`
  Specifies that the game will autoplay.  The AI's bat is yellow.

`-c <ip-address>`
  Connect to the remote IP address specified

`-l <lossrate>`
  Emulate packet loss at the specified percentage

`-d <delay>`
  Emulate one-way network latency.  Value is in milliseconds

To play against yourself locally, with player 2 auto-playing:

Player 1:
  `python pong.py`

Player 2:
  `python pong.py -s -a`


With player 1 on 10.0.0.1 and player 1 on 10.0.0.2, both players manual:

Player 1:
  `python pong.py -c 10.0.0.2`

Player 2:
  `python pong.py -s -c 10.0.0.1`



