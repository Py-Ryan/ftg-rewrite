# ftg-rewrite:
A rewrote version of Ft.-Gunna

# version:
0.4.4

# updates:
    0.1.0:
        Barebones version.
        
    0.2.0:
        - Dynamic prefixing.
        - Built-in aiohttp.ClientSession() since aiohttp suggests this.
        - Implemented Jishaku.
        - Ftg.extensions yields None if no extensions are passed to the constructor.
        - DB parsing for guild specific data such as custom prefixes.
        - Ftg now has a cache.
            -> This cache is used to store.
                    -> Prefixes for a guild during `Ftg.run` and during runtime.
                    -> Deleted & edited messages. 
        - Added a new extension `config`.
            -> Features commands relating to guild & user configuration.
            -> Added a change prefix command.
            
    0.3.0:
        - Added a new extension `fun`
            -> Added `binary` command for binary conversions.
                -> Normal input will be converted to binary.
                -> 8-bit bytes seperated by spaces will be converted back into utf-8.
            -> Added `caesar` command for caesar cipher.
                -> Encrypt a string of text with a 4-shift caesar cipher.
            -> Added `catfact` command for random cat facts, UwU.
                -> Random cat facts.       
        - A ValueError is now raised in `bot.py` if vital toml keys are missing from the toml config.
        - `Ftg.extensions` now checks the type of _extensions and raises a warning if problems are found.
        - Use `set(config)` over `config.keys()` in the TOML key check inside of `bot.py`.
        - Changed common cooldown time from 2 to 1.5.
            -> With the exception of the epic catfact command.
        - Add a debug error handler in `bot.py`. This is not production.
        - Updated to discord.py-1.4.0a.
        
    0.3.1:
        - Fixed `binary` command breaking with long inputs.
        - Edited `binary` command minimum length for a hastebin post to 150 rather than 100.
        - Added an additional check to `binary` to allow users to convert numbers into binary.
        - Change `caesar` back to a command rather than a group.
       
    0.4.0:
        - `binary` command now supports 8-bit binary input without spaces between bytes.
        - `binary` command now supports text file input.
        - `binary` command double-checks bit length of inputted binary. If not 8, then input is converted to binary.
        - slightly edited conversion logic inside `binary` command.
        - `fun` extension:
            -> Added `ip` information command.        
            -> Added `hex` hexadecimal conversion command.    
            -> Added `morse` morse code conversion command.
        - Fixed `Ftg.get_prefix` from erroring in DMs.
        - New extension `meta`:
            -> `prefix` command migrated here.
            -> `av` command for viewing enlarged user avatars.
            -> `info` command migrated here.
        - Changed cog names from `ext_nameCog` to `ext_name`
        - Added helper methods to `fun` to prevent redundant code in conversion commands.
        
    0.5.0:
        - If `me` is the only argument to the `info` command, the author is specified.
        - Changed how cogs automatically get assigned a _raw_uptime attribute
        - Removed override for `add_cog` due to above ^
        - Added db as an automatically assigned attribute to each cog.
        - Added cog info command to `meta` invoked with `<prefix> info cog <cog_name>`
        - Implmented custom context with a reply method to emulate d.js `user.reply`.