<!--
If your issue is a usage or a general question, please submit it here instead:
- Mailing List: https://groups.google.com/forum/#!forum/gensim
-->

<!-- Instructions For Filing a Bug: https://github.com/RaRe-Technologies/gensim/blob/develop/CONTRIBUTING.md -->

#### Description
TODO: change commented example
<!-- Example: Not counting words over 42 characters. -->

#### Steps/Code/Corpus to Reproduce
<!--
Example:
```
from bounter import CountMinSketch

cms = CountMinSketch(width=1, depth=1)
cms.increment("42****************************************")
cms.increment("43*****************************************")
print(cms["42****************************************"]) # 1
print(cms["43*****************************************"]) # 0

```
If the code is too long, feel free to put it in a public gist and link
it in the issue: https://gist.github.com
-->

#### Expected Results
<!-- Example: Expected to receive 1 as a frequency for both words.-->

#### Actual Results
<!-- Example: Got 1 for short word but 0 for long word. -->

#### Versions
<!--
Please run the following snippet and paste the output below.
import platform; print(platform.platform())
import sys; print("Python", sys.version)
import numpy; print("NumPy", numpy.__version__)
import bounter; print("bounter", bounter.__version__)
-->


<!-- Thanks for contributing! -->