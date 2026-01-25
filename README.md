# SUMO - Slim U-Net trained on MODA

Implementation of the *SUMO* (*S*lim *U*-Net trained on *MODA*) model as described in:

```
Lars Kaulen, Justus T.C. Schwabedal, Jules Schneider, Philipp Ritter and Stephan Bialonski.
Advanced sleep spindle identification with neural networks. Sci Rep 12, 7686 (2022).
https://doi.org/10.1038/s41598-022-11210-y
```

## Installation Guide

- Install *uv*.

```bash
uv sync
```

- On Ubuntu 25.10, it says this error:

```python
from torch._C import *  # noqa: F403
ImportError: libtorch_cpu.so: cannot enable executable stack as shared object requires: Invalid argument
```

Fixed using *patchelf*, locate the file *libtorch_cpu.so*, and do:

```bash
sudo patchelf --clear-execstack <path/to/libtorch_cpu.so>
```

Notes:
    - removed *matplotlib* as is was not compiling, and showing segmentation fault.
    - added *six* package, it was not in the requirements.txt but was needed.

