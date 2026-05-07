from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Hash import SHA256
from PIL import Image
import os
import random

def derive_key(password: str) -> bytes:
    return SHA256.new(password.encode('utf-8')).digest()

def encrypt_secure_aes(input_path, output_path, password):
    key = derive_key(password)
    with open(input_path, 'rb') as f:
        file_data = f.read()

    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(file_data, AES.block_size))

    with open(output_path, 'wb') as f:
        f.write(iv)
        f.write(encrypted_data)
    return True

def encrypt_visual_stream(input_path, output_path, key_string):
    """Secure visual mode using PRNG and XOR."""
    img = Image.open(input_path).convert('RGB')
    pixels = img.load()
    width, height = img.size
    
    seed_bytes = SHA256.new(key_string.encode('utf-8')).digest()
    seed_int = int.from_bytes(seed_bytes, 'big')
    random.seed(seed_int)

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            rand_r = random.randint(0, 255)
            rand_g = random.randint(0, 255)
            rand_b = random.randint(0, 255)
            pixels[x, y] = (r ^ rand_r, g ^ rand_g, b ^ rand_b)
            
    img.save(output_path)
    return True

def encrypt_visual_vulnerable(input_path, output_path, key_string):
    """The original Vigenere mode to demonstrate the repeating key vulnerability."""
    img = Image.open(input_path).convert('RGB')
    pixels = img.load()
    width, height = img.size
    
    key_bytes = key_string.encode('utf-8')
    key_length = len(key_bytes)

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            shift = key_bytes[(x + y) % key_length]
            pixels[x, y] = ((r + shift) % 256, (g + shift) % 256, (b + shift) % 256)
            
    img.save(output_path)
    return True