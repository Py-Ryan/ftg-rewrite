# ftg-rewrite:
A rewrote version of Ft.-Gunna

# version:
0.2.0

# updates:
    0.1.0:
        Barebones version.
    0.2.0:
        - Dynamic prefixing
        - Built-in aiohttp.ClientSession() since aiohttp suggests this
        - Implemented Jishaku
        - Ftg.extensions yields None if no extensions are passed to the constructor
        - Setup DB parsing for guild specific data such as custom prefixes.
        - Ftg now has a cache
            ->
                - This cache is used to store
                    ->
                        - Prefixes for a guild during init and during runtime.
                        - Deleted & edited messages. 
        - Added a new cog `config`
            ->
                - Features commands relating to guild & user configuration
                    ->
                        - Added a change prefix command