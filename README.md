# namesearch

Just some quick experiments with people searching using Typesense.

Notes:

* Just throwing names and addresses into typesense as-is and querying on them works pretty well
* Vectorizing the name and address, and doing a hybrid search on the encoding and name fields shows some mild improvement.
* Considered experimenting with a phonetic algorithm (Metaphone) to see if using that could improve search results.
    * The hybrid search does well at handling the worst misspellings I can come up with--not sure Metaphone will help here.