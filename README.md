
Bitcoin: 1NfGejohzoVGffAD1CnCRgo9vApjCU2viY
Litecoin: LiUGs9sqH6GBHsvzpNtLCoyXB5aCDi9HsQ
Dogecoin: DTy5q7uUQ1whqyUrwC1LbhgqwKgovJT5R7
Protoshares (BitShares-PTS): PZxpdC8RqWsdU3pVJeobZY7JFKVPfNpy5z
BTSX: drltc

This is a specification of the BitShares toolkit blockchain.  This is a work-in-progress.  The principal author is `drltc`.
Development can be followed in this forum thread:  https://bitsharestalk.org/index.php?topic=1738.0

To make sure I fully understand the blockchain format, I'm adding `chain.py` which can talk to the built-in
chain server which allows a binary download of the blockchain.

This was tested with the following test network version:

    {
    "bitshares_toolkit_revision": "e6744e252c4f89c8d2156800edf55c483d6e8614",
    "bitshares_toolkit_revision_age": "79 hours ago",
    "fc_revision": "a0b3a9a92d28ec0b3a08b45b8c1449737f56dd34",
    "fc_revision_age": "6 days ago",
    "compile_date": "compiled on Sep  9 2014 at 01:22:59"
    "blockchain_description": "BitShares X Test Network",
    "test_network_version": "23"
    }

It has not been tested on live network data yet.

Files
-----

- `README.md` is this cruft
- `chain.py` parses the blockchain from a chainserver (currently must be running on `localhost:11235`)
- `notes.md` is my (drltc's) raw notes from looking at the code
- `questions.md` is questions for more knowledgeable developers
- `block.md` is the actual documentation
- `dump2bin.py` converts the server side of a `socat` dump to binary
- `nctest.sh` respawns `nc` in a `while` loop.  It makes the server side of the conversation reproducible and suppresses the client side entirely.

