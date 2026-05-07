from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from PIL import Image
from encrypt import derive_key
from Crypto.Hash import SHA256
import random

def decrypt_secure_aes(input_path, output_path, password):
    key = derive_key(password)
    with open(input_path, 'rb') as f:
        iv = f.read(16)
        encrypted_data = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        return True
    except ValueError:
        return False

def decrypt_visual_stream(input_path, output_path, key_string):
    """Reverses the PRNG stream cipher using XOR."""
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

def decrypt_visual_vulnerable(input_path, output_path, key_string):
    """Reverses the classic Vigenere repeating key."""
    img = Image.open(input_path).convert('RGB')
    pixels = img.load()
    width, height = img.size
    
    key_bytes = key_string.encode('utf-8')
    key_length = len(key_bytes)

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            shift = key_bytes[(x + y) % key_length]
            pixels[x, y] = ((r - shift) % 256, (g - shift) % 256, (b - shift) % 256)
            
    img.save(output_path)
    return True