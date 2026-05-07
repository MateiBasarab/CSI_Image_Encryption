# (EN) Image Cryptography Project


## User Interfaces

This project features two distinct Graphical User Interfaces (GUIs) to suit different needs and hardware capabilities:

1. **`UI_Lite.py`**: A lightweight, fast, and highly compatible interface built using Python's native `tkinter` library. It uses a clean, tabbed layout and is perfect for systems with limited resources.
2. **`UI_Modern.py`**: A premium, hardware-accelerated interface built with `PyQt6`. It runs at a 1600x1000 resolution, features a modern dark theme, fluid morphing animations, and a dynamic 16:9 dual-preview gallery for real-time cryptographic visualization.

---

## Cryptographic Theory & Implementation

This application splits image encryption into two fundamental categories: **Visual (Pixel-Level) Encryption** and **Secure (File-Level) Encryption**.

### 1. Visual Encryption (Pixel-Level)
Visual encryption manipulates only the RGB (Red, Green, Blue) data of the image. The file headers remain intact, meaning the output is still a valid image file that can be opened in any standard viewer. The goal is to scramble the visual data mathematically.

#### The Repeating Key Vulnerability (Classic Vigenère)
The **Vulnerability Demo** tab implements a pixel-adapted version of the classic Vigenère cipher. 
- **The Math:** For every pixel, the algorithm extracts the RGB values (0-255). It takes the user's password, maps each character to its byte value, and adds that value to the pixel's color channels: `C = (P + K) mod 256` (where `C` is ciphertext, `P` is plaintext pixel, and `K` is the key character).
- **The Vulnerability:** Because the password is short (e.g., "SECRET"), it repeats infinitely across the millions of pixels. If an image has a large area of uniform color (like a blue sky), the exact same mathematical shift is applied repeatedly. This predictable pattern allows the human eye (and cryptanalysts) to easily see the original outlines, gradients, and shapes of the image. This perfectly visualizes why repeating-key ciphers and modern algorithms running in ECB (Electronic Codebook) mode are fundamentally insecure for pattern-heavy data.

#### The Secure Visual Stream (XOR + PRNG)
To fix the repeating key vulnerability, the **Visual Stream** tab implements a Pseudo-Random Stream Cipher using the ultimate cryptographic operator: **XOR (`^`)**.
- **The Math:** Instead of repeating the password, the password is put through a **SHA-256** hash function to create a mathematically secure 32-byte seed. This seed is fed into a Pseudo-Random Number Generator (PRNG). 
- **The Execution:** The PRNG generates an infinitely long, completely unpredictable stream of numbers (0-255). Every single RGB channel of every pixel is XORed against a unique random number. 
- **Why it works:** Because the stream never repeats its pattern, the output is pure, uniform, high-frequency static. No outlines or shapes survive. Furthermore, the XOR operation is perfectly symmetrical: `(A ^ B) ^ B = A`. If the receiver enters the exact same password, the exact same PRNG stream is generated, and XORing the static with the stream perfectly restores the original photo.

*Note on Data Compression:* Visual encryption results in high-frequency static. Lossy compression algorithms like JPEG alter pixels to save space, which permanently destroys the precise math needed for decryption. Therefore, this tool forces the output of visual encryptions to `.png` (Lossless Compression) to guarantee 100% mathematical recovery.

### 2. Secure File-Level Encryption (AES)
The **Secure Mode** tab abandons pixel manipulation entirely. Instead, it treats the image as a raw sequence of binary data.

#### Advanced Encryption Standard (AES-256)
- **Algorithm:** AES is a modern symmetric block cipher. We use a 256-bit key length for maximum security. The user's password is hashed via SHA-256 to derive this exact 32-byte key.
- **Block Mode (CBC):** The data is encrypted in Cipher Block Chaining (CBC) mode. Unlike ECB, CBC takes the ciphertext of the previous block and XORs it with the plaintext of the current block before encrypting it. This creates a chain reaction that completely obliterates any repeating patterns in the data.
- **Initialization Vector (IV):** For the very first block of data, there is no "previous ciphertext" to XOR against. Therefore, a cryptographically secure random 16-byte IV is generated using `os.urandom(16)`. This IV is prepended to the final `.bin` file so the decryption algorithm can read it and start the unchaining process.
- **Padding:** AES operates strictly on 16-byte blocks. If the image file size is not a perfect multiple of 16, PKCS#7 padding is applied to fill the gap before encryption, and mathematically stripped away during decryption.
- **Result:** The output is a `.bin` file. It is no longer an image. The file headers, metadata, and pixel arrays are completely encrypted.

---

## Prerequisites & Execution
Ensure you have the required libraries installed before running the GUIs:
```bash
pip install pycryptodome Pillow PyQt6
```
To run the modern interface:
```bash
python UI_Modern.py
```

---
---

# (RO) Criptarea imaginilor


## Interfete Utilizator

Acest proiect dispune de doua Interfete Grafice pentru Utilizator (GUIs) distincte pentru a se potrivi diferitelor nevoi si capacitati hardware:

1. **`UI_Lite.py`**: O interfata usoara, rapida si extrem de compatibila construita folosind libraria nativa `tkinter` din Python. Foloseste un design curat, cu tab-uri, si este perfecta pentru sistemele cu resurse limitate.
2. **`UI_Modern.py`**: O interfata premium, accelerata hardware, construita cu `PyQt6`. Ruleaza la o rezolutie de 1600x1000, dispune de o tema intunecata moderna, animatii fluide de tip morphing si o galerie duala dinamica 16:9 pentru vizualizarea criptografica in timp real.

---

## Teorie Criptografica si Implementare

Aceasta aplicatie imparte criptarea imaginilor in doua categorii fundamentale: **Criptare Vizuala (La nivel de pixel)** si **Criptare Securizata (La nivel de fisier)**.

### 1. Criptare Vizuala (Nivel de Pixel)
Criptarea vizuala manipuleaza doar datele RGB (Rosu, Verde, Albastru) ale imaginii. Headerele fisierului raman intacte, ceea ce inseamna ca rezultatul este in continuare un fisier imagine valid care poate fi deschis in orice vizualizator standard. Scopul este de a amesteca datele vizuale in mod matematic.

#### Vulnerabilitatea Cheii Repetitive (Vigenere Clasic)
Tab-ul **Demo Vulnerabilitate** implementeaza o versiune adaptata pentru pixeli a cifrului clasic Vigenere.
- **Matematica:** Pentru fiecare pixel, algoritmul extrage valorile RGB (0-255). Preia parola utilizatorului, mapeaza fiecare caracter la valoarea sa in octeti si aduna acea valoare la canalele de culoare ale pixelului: `C = (P + K) mod 256` (unde `C` este ciphertext, `P` este pixelul plaintext, iar `K` este caracterul cheii).
- **Vulnerabilitatea:** Deoarece parola este scurta (de exemplu, "SECRET"), aceasta se repeta la infinit peste milioanele de pixeli. Daca o imagine are o zona mare de culoare uniforma (cum ar fi un cer albastru), aceeasi deplasare matematica este aplicata in mod repetat. Acest sablon (pattern) predictibil permite ochiului uman (si criptanalistilor) sa vada cu usurinta contururile, gradientii si formele originale ale imaginii. Acest lucru vizualizeaza perfect de ce cifrurile cu cheie repetitiva si algoritmii moderni care ruleaza in modul ECB (Electronic Codebook) sunt fundamental nesigure pentru date cu sabloane repetitive.

#### Fluxul Vizual Securizat (Stream Cipher cu XOR + PRNG)
Pentru a repara vulnerabilitatea cheii repetitive, tab-ul **Flux Vizual** implementeaza un Cifru de Flux Pseudo-Aleator folosind operatorul criptografic suprem: **XOR (`^`)**.
- **Matematica:** In loc sa repete parola, parola este trecuta printr-o functie hash **SHA-256** pentru a crea un seed matematic sigur de 32 de octeti. Acest seed este introdus intr-un Generator de Numere Pseudo-Aleatoare (PRNG).
- **Executia:** PRNG genereaza un flux infinit si complet imprevizibil de numere (0-255). Fiecare canal RGB al fiecarui pixel este aplicat prin operatia XOR impotriva unui numar aleatoriu unic.
- **De ce functioneaza:** Deoarece fluxul nu isi repeta niciodata sablonul, rezultatul este zgomot static (static noise) pur, uniform, de inalta frecventa. Nu supravietuiesc contururi sau forme. Mai mult, operatia XOR este perfect simetrica: `(A ^ B) ^ B = A`. Daca receptorul introduce exact aceeasi parola, este generat exact acelasi flux PRNG, iar aplicarea XOR asupra staticului cu fluxul restaureaza perfect fotografia originala.

*Nota despre Compresia Datelor:* Criptarea vizuala rezulta in zgomot static de inalta frecventa. Algoritmii de compresie cu pierderi (lossy) precum JPEG altereaza pixelii pentru a economisi spatiu, ceea ce distruge permanent matematica precisa necesara pentru decriptare. Prin urmare, acest instrument forteaza salvarea criptarilor vizuale in format `.png` (Compresie Fara Pierderi / Lossless) pentru a garanta o recuperare matematica de 100%.

### 2. Criptare Securizata la Nivel de Fisier (AES)
Tab-ul **Mod Securizat** abandoneaza complet manipularea pixelilor. In schimb, trateaza imaginea ca pe o secventa bruta de date binare.

#### Standardul de Criptare Avansat (AES-256)
- **Algoritmul:** AES este un cifru bloc simetric modern. Folosim o lungime a cheii de 256 de biti pentru securitate maxima. Parola utilizatorului este trecuta prin hash via SHA-256 pentru a deriva exact aceasta cheie de 32 de octeti.
- **Modul Bloc (CBC):** Datele sunt criptate in modul Cipher Block Chaining (CBC). Spre deosebire de ECB, CBC preia ciphertext-ul blocului anterior si ii aplica operatia XOR cu plaintext-ul blocului curent inainte de a-l cripta. Acest lucru creeaza o reactie in lant care oblitereaza complet orice tipar repetitiv in date.
- **Vectorul de Initializare (IV):** Pentru primul bloc de date, nu exista un "ciphertext anterior" impotriva caruia sa se aplice XOR. Prin urmare, un IV aleatoriu de 16 octeti, sigur din punct de vedere criptografic, este generat folosind `os.urandom(16)`. Acest IV este adaugat la inceputul fisierului final `.bin` astfel incat algoritmul de decriptare sa-l poata citi si sa inceapa procesul de desfacere a lantului.
- **Padding:** AES opereaza strict pe blocuri de 16 octeti. Daca dimensiunea fisierului imagine nu este un multiplu perfect de 16, se aplica padding PKCS#7 pentru a umple golul inainte de criptare, care este indepartat matematic in timpul decriptarii.
- **Rezultatul:** Rezultatul este un fisier `.bin`. Nu mai este o imagine. Headerele fisierului, metadatele si matricile de pixeli sunt complet criptate.

---

## Cerinte Preliminare si Executie
Asigura-te ca ai instalate librariile necesare inainte de a rula aplicatiile:
```bash
pip install pycryptodome Pillow PyQt6
```
Pentru a rula interfata moderna:
```bash
python UI_Modern.py
```