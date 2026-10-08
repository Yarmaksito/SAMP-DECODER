# SA:MP 0.3.DL Cache Decoder
**Created by Yarmak**
Discord: @yarmaksito / yarmaksito@proton.me

An automated, brute-force decryption tool designed to crack and recover obfuscated assets (models and textures) from SA:MP 0.3.DL server cache folders.

## What it does
Many custom SA:MP 0.3.DL servers attempt to protect their custom skins and assets by:
1. Stripping file extensions (`.dff`, `.txd`, `.col`).
2. Applying a simple XOR cipher to the binary files to prevent players from stealing them or viewing them in standard 3D editors.

This tool bypasses these protections completely. It doesn't need to know the specific server's encryption key. Instead, it reads the mathematically predictable RenderWare headers that GTA San Andreas requires, derives the XOR key dynamically from the obfuscated bytes, cracks the file, and restores the original asset.

## Features
- **Universal XOR Cracking**: Automatically derives 1-byte and multi-byte repeating XOR keys on the fly.
- **Magic Byte Detection**: Identifies `.dff` (Clumps) and `.txd` (Texture Dictionaries) using RenderWare core structure rules.
- **Smart Renaming**: Safely appends the correct extensions without duplicating them.
- **Batch Processing**: Scans massive cache folders in seconds.

## How to use

1. Locate the target SA:MP cache folder. It is usually found in your GTA San Andreas documents folder or main game directory under `SAMP/cache/<server_ip_port>`.
2. Open your terminal or command prompt.
3. Run the decoder script, passing the path to the cache folder:

```bash
python cache_decoder.py "C:\path\to\GTA San Andreas User Files\SAMP\cache\127.0.0.1_7777"
```

## Output
The script will generate a new folder named `Decoded_Cache` inside the directory where you run the tool. All recovered skins, textures, and collisions will be dumped there in plain, unencrypted formats ready to be opened in any editor.

## Linking orphans (Heuristic Linker)
After decrypting the cache, you will notice the files retain their hexadecimal hash names (e.g., `0x1A51D1EF.txd` and `0x1A9F9F7D.dff`). To use them, you must pair the 3D model with its correct texture dictionary.

There is now a companion script, `linker.py`, to automatically pair them:

1. After generating the `Decoded_Cache` folder using the decoder, simply run:
```bash
python linker.py
```
2. The script will aggressively scan every `.dff` and `.txd` file, extracting their internal ASCII texture strings using optimized C-level regex bindings.
3. It geometrically cross-references these strings to pair the exact 3D model with its corresponding textures.
4. The paired assets are automatically grouped, renamed, and copied into a clean `Linked_Cache` folder.
---
*Yarmak's Suite - HIT 'EM UP*
