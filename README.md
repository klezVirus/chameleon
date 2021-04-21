# Chameleon

Chameleon is yet another PowerShell obfuscation tool designed to bypass AMSI and commercial antivirus solutions. 
The tool has been developed as a Python port of the [Chimera][1] project, by [tokioneon_][2]. As such, it uses 
mostly the same techniques to evade common detection signatures, such as:

* comment deletion/substitution
* string substitution (variables, functions, data-types)
* variable concatenation
* indentation randomization
* semi-random backticking
* case randomization
* encoding 

## Why porting it

Chimera was indeed a shiny project, so why did I decided to port it to Python and why you should use chameleon?
Well, there are several reasons why I decided to build Chameleon, and I've listed below the most important ones. 

##### Reliability

As the author of Chimera states in the readme, the chimera script can successfully obfuscate scripts that the author
tested personally, which are contained in the [shells][3] directory. However, the tool is not very reliable with other, 
untested, scripts. Quoting the author:

> there's no telling how untested scripts will reproduce with Chimera... 

This alone was a good reason to attempt to make the tool a bit more reliable, and also capable to obfuscate 
more complex scripts.

##### Speed

Chimera attempts several obfuscation steps, which usually requires the input to be read from a file, and stored back 
in a file again. While this is a safe approach, because each step is saved to disk (let's say there is an error at step 
n, we would still have the result of the obfuscation till n - 1), this is not really efficient. The overhead of writing 
and reading from a file at each time make the tool really slow when operating on large scripts (up to several minutes 
with the -a option). 

Chameleon, instead, performs all obfuscation steps in memory, meaning it is extremely faster.

##### Portability

Chimera has been developed as a Bash Script, and heavily relies on common Linux utilities to accomplish the obfuscation.

Chameleon, on the other hand, is built with Python, meaning that you can use it wherever Python is installed.

##### Smart evasion checking

Chimera offers a function to submit scripts to VirusTotal directly. While this might be considered a useful utility, 
it will expose the obfuscated script to third party threat-intelligence, weakening the obfuscation engine. 

To address this issue, Chameleon uses the utility [AMSITrigger][4] by [RhytmStick][5], to check if the obfuscated result will indeed 
bypass AMSI.

### Improvements

So far, we've talked about the efficiency and reliability issues of chimera, but what are the real improvements 
from an obfuscation standpoint? The techniques used by Chameleon are for the most the same as Chimera, with some improvements:

* "Smart" variable scope identification (function local variables will be replaced "carefully" or left untouched)
* Random backticking (not just limited to a set of strings)
* Random case switch (not just limited to a set of strings)
* Supports an external obfuscation mapping for functions ~~and parameters~~ (TODO)
* Additional Base64 Encoding wrapping

Chameleon manages to handle function and local parameters by implementing a very minimalist PowerShell "reader", which is
capable of distinguish three contexts: 

* Global/Main Scope
* In-Function Scope
    * Param() Blocks

The reader is still not a real parser, and relies on Dick Language to find relevant areas limits.

### Notes 

Worth saying that, even if now Chameleon is capable of obfuscate also complex scripts, it's still not comparable with
Invoke-Obfuscation, which actually is way more mature and is also backed-up by a fully fledged parser `Management.Automation.Language.Parser`.

### Next steps

Moreover, Chameleon is still not perfect and still needs further development to increase both its accuracy and improve 
its obfuscation techniques. A non-exhaustive list of planned improvements are below:

* Upgrade the PowerShell reader
* Include other encoding schemes
* Add more obfuscation methods

## Conclusions

As [tokioneon_][2], I also hope this project would encourage someone to leverage what has been developed so far to 
produce something better, as Chimera encouraged me.

## Credits

Worth saying that Chameleon would not be a thing without the work of [tokioneon_][2] on [Chimera][1], as the most of the
obfuscation process was ported from Bash to Python (of course with some mods).

## Contribute

If you want to contribute, just fork the repository 
Any PR is well accepted.


[1]: https://github.com/tokyoneon/Chimera.git
[2]: https://twitter.com/tokyoneon_
[3]: https://github.com/tokyoneon/Chimera/tree/master/shells
[4]: https://github.com/RythmStick/AMSITrigger
[5]: https://github.com/RythmStick