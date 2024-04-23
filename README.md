This repository contains two models for modeling a producer-consumer ring buffer.
The operational model which is implemented using Pytho and an formal model with Forge.

### Operational model (runnable demo)


To run the oprational model make sure you have python3 installed.
Then run following command:

```
python3 ringbuffer.py
```
If it fails to run, make sure the following python libraries are installed on your system and try again.

```
random
string
unittest
argparse
```

This will generate a text file name results.txt. This file will
contains all the results for the tests.

### Forge model (Under implementation)

Make sure Forge modeling language is install
following [these](https://csci1710.github.io/forge-documentation/getting-started/installation.html) instructions.
Then run prodcons.frg file to execute the model.
