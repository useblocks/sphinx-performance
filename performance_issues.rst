Possible Sphinx performance issues
==================================

Theories

- Forking of new processes cost time
  - Sphinx creates more processes than worker count
  - Merging of parallel env to main env runs in main process and blocks next chunk
  - Merging of parallel env may be expensive
- Merging of env blocks runs before next chunk execution
- write_doc_serialized is running before all parallelisation.
  - Can this be parallelized?
- doctrees are read from hard disk in main process, then sent to workers.
  This leads to expensive pickle operation and sending more data.
- Distribution of files to workers is pre-calculated and static.
  One workers may get 80% of the biggest documents.
- Sphinx uses fork which does not work on Windows (needs spawn)
