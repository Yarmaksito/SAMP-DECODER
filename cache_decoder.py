import os
import sys

def print_watermark():
    print(r"""
 __   __                    _    
 \ \ / /_ _ _ __ _ __  __ _| |__ 
  \ V / _` | '__| '  \/ _` | / / 
   | | (_| | |  | |\/| (_| |   \ 
   |_|\__,_|_|  |_|  |\__,_|_|\_\
      
   SA:MP 0.3.DL Cache Decoder
   Created by Yarmak
    """)

# RenderWare Magic Bytes (Little Endian)
# DFF starts with Clump (0x10) -> 10 00 00 00
# TXD starts with TextureDictionary (0x16) -> 16 00 00 00
# COL starts with 'COLL' -> 43 4F 4C 4C

MAGIC_DFF = b'\x10\x00\x00\x00'
MAGIC_TXD = b'\x16\x00\x00\x00'
MAGIC_COL = b'COLL'

def get_xor_key(data, expected_magic):
    """Attempt to derive a single-byte or multi-byte XOR key by comparing the first 4 bytes."""
    key = bytearray()
    for i in range(4):
        key.append(data[i] ^ expected_magic[i])
    
    # Check if it's a repeating 1-byte key
    if key[0] == key[1] == key[2] == key[3]:
        return key[0:1]
    # Check if it's a repeating 2-byte key
    if key[0] == key[2] and key[1] == key[3]:
        return key[0:2]
    
    return key

def decrypt_data(data, key):
    """Decrypt data using the derived XOR key."""
    decrypted = bytearray(data)
    key_len = len(key)
    for i in range(len(decrypted)):
        decrypted[i] ^= key[i % key_len]
    return decrypted

def analyze_file(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    if len(data) < 4:
        return None, None
    
    header = data[:4]
    
    # Check if it's already raw and unencrypted
    if header == MAGIC_DFF:
        return 'dff', data
    if header == MAGIC_TXD:
        return 'txd', data
    if header == MAGIC_COL:
        return 'col', data
        
    # Attempt to derive XOR key for DFF
    dff_key = get_xor_key(header, MAGIC_DFF)
    decrypted_dff = decrypt_data(data[:8], dff_key)
    # Check if the next 4 bytes look like a valid size (just a basic sanity check)
    if decrypted_dff[:4] == MAGIC_DFF:
        return 'dff', decrypt_data(data, dff_key)
        
    # Attempt to derive XOR key for TXD
    txd_key = get_xor_key(header, MAGIC_TXD)
    decrypted_txd = decrypt_data(data[:8], txd_key)
    if decrypted_txd[:4] == MAGIC_TXD:
        return 'txd', decrypt_data(data, txd_key)

    return None, None

def process_cache(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    extracted_count = {'dff': 0, 'txd': 0, 'col': 0}
    
    print(f"[*] Scanning cache folder: {input_dir}")
    
    for root, _, files in os.walk(input_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # Skip if it's a directory or too small
            if not os.path.isfile(filepath):
                continue
                
            file_type, decrypted_data = analyze_file(filepath)
            
            if file_type:
                # Ensure we don't duplicate extensions
                base_name = filename
                if '.' in base_name:
                    base_name = base_name.rsplit('.', 1)[0]
                out_name = f"{base_name}.{file_type}"
                out_path = os.path.join(output_dir, out_name)
                
                with open(out_path, 'wb') as out_f:
                    out_f.write(decrypted_data)
                    
                extracted_count[file_type] += 1
                print(f"[+] Recovered {file_type.upper()}: {filename} -> {out_name}")
                
    print("\n[*] Extraction Complete.")
    print(f"    DFF Models: {extracted_count['dff']}")
    print(f"    TXD Textures: {extracted_count['txd']}")
    print(f"    COL Collisions: {extracted_count['col']}")
    print(f"[*] Saved to: {output_dir}")

if __name__ == "__main__":
    print_watermark()
    if len(sys.argv) < 2:
        print("Usage: python cache_decoder.py <path_to_samp_cache_folder>")
        sys.exit(1)
        
    input_cache = sys.argv[1]
    output_folder = os.path.join(os.getcwd(), 'Decoded_Cache')
    
    process_cache(input_cache, output_folder)
