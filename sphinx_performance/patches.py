"""
Stores some patches for Sphinx to test certain changes
"""

from math import sqrt
from typing import Any, Callable, Dict, List, Optional, Sequence
import sphinx


def patch():
    sphinx.util.parallel.make_chunks = __make_chunks_patch


def __make_chunks_patch(arguments: Sequence[str], nproc: int, maxbatch: int = 10) -> List[Any]:
    # determine how many documents to read in one go
    nargs = len(arguments)
    chunksize = nargs // nproc
    if chunksize >= maxbatch:
        # try to improve batch size vs. number of batches
        chunksize = int(sqrt(nargs / nproc * maxbatch))
    if chunksize == 0:
        chunksize = 1
    nchunks, rest = divmod(nargs, chunksize)
    if rest:
        nchunks += 1
    # partition documents in "chunks" that will be written by one Process
    return [arguments[i * chunksize:(i + 1) * chunksize] for i in range(nchunks)]
