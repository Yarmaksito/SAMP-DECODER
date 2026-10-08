"""SA:MP 0.3.DL Heuristic Linker. Created by Yarmak. Discord: https://discord.gg/cRU3fMq7v5"""
import os
import string
import shutil
import concurrent.futures
import re

def print_watermark():
    print(r"""
 __   __                    _    
 \ \ / /_ _ _ __ _ __  __ _| |__ 
  \ V / _` | '__| '  \/ _` | / / 
   | | (_| | |  | |\/| (_| |   \ 
   |_|\__,_|_|  |_|  |\__,_|_|\_\
      
   SA:MP 0.3.DL Heuristic Linker
   Created by Yarmak
   Discord: https://discord.gg/cRU3fMq7v5
    """)

def extract_strings(filepath, min_len=4):
    """Extract printable ASCII strings from a binary file extremely fast using regex."""
    result = set()
    with open(filepath, 'rb') as f:
        data = f.read()

    # Find all sequences of alphanumeric characters and underscores of min_len or more
    pattern = rb'[a-zA-Z0-9_]{' + str(min_len).encode() + rb',}'
    matches = re.findall(pattern, data)

    for match in matches:
        result.add(match.decode('ascii').lower())

    return result

def link_cache(cache_dir, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    files = [f for f in os.listdir(cache_dir) if os.path.isfile(os.path.join(cache_dir, f))]
    dffs = [f for f in files if f.lower().endswith('.dff')]
    txds = [f for f in files if f.lower().endswith('.txd')]

    print(f"[*] Found {len(dffs)} DFFs and {len(txds)} TXDs.")
    print("[*] Extracting texture references...")

    # Pre-calculate strings for all TXDs (since they are usually smaller and we compare them often)
    txd_data = {}
    for txd in txds:
        txd_data[txd] = extract_strings(os.path.join(cache_dir, txd))

    pair_count = 1

    print("[*] Correlating DFFs to TXDs...")
    for dff in dffs:
        dff_strings = extract_strings(os.path.join(cache_dir, dff))

        best_match = None
        best_score = 0

        for txd, txd_strings in txd_data.items():
            score = len(dff_strings.intersection(txd_strings))
            if score > best_score:
                best_score = score
                best_match = txd

        if best_match and best_score >= 1:
            # Found a pair
            new_name = f"Linked_model_{pair_count}"
            print(f"[+] Paired {dff} <-> {best_match} (Score: {best_score}) -> {new_name}")

            # Copy to out_dir
            shutil.copy(os.path.join(cache_dir, dff), os.path.join(out_dir, f"{new_name}.dff"))
            shutil.copy(os.path.join(cache_dir, best_match), os.path.join(out_dir, f"{new_name}.txd"))

            pair_count += 1
        else:
            print(f"[-] Could not find a matching TXD for {dff}")

    print(f"\n[*] Finished. Successfully linked {pair_count - 1} pairs.")
    print(f"[*] Linked files saved to: {out_dir}")

if __name__ == "__main__":
    print_watermark()
    cache_dir = "Decoded_Cache"
    out_dir = "Linked_Cache"

    if not os.path.exists(cache_dir):
        print(f"[-] Directory '{cache_dir}' not found. Run the decoder first.")
    else:
        link_cache(cache_dir, out_dir)
