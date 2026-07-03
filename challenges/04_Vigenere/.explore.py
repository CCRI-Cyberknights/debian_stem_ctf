#!/usr/bin/env python3
import sys
import re
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, spinner, print_success, print_error, print_info, resize_terminal, clear_screen, safe_input

# === Config ===
CIPHER_FILE = "cipher.txt"
OUTPUT_FILE = "decoded_output.txt"

# === Vigenère Logic (Internal) ===
def vigenere_decrypt(ciphertext, key):
    result = []
    key = key.lower()
    if not key: 
        return ciphertext 
    
    key_len = len(key)
    key_indices = [ord(k) - ord('a') for k in key]
    key_pos = 0

    for char in ciphertext:
        if char.isalpha():
            offset = ord('A') if char.isupper() else ord('a')
            pi = ord(char) - offset
            ki = key_indices[key_pos % key_len]
            decrypted = chr((pi - ki) % 26 + offset)
            result.append(decrypted)
            key_pos += 1
        else:
            result.append(char)

    return ''.join(result)

def find_flag(text):
    match = re.search(r"CCRI-[A-Z0-9]{4}-\d{4}", text)
    return match.group(0) if match else None

# === Main Flow ===
def main():
    # 1. Setup
    resize_terminal(35, 90)
    script_dir = Path(__file__).resolve().parent
    cipher_path = script_dir / CIPHER_FILE
    output_path = script_dir / OUTPUT_FILE

    if not cipher_path.is_file():
        print_error(f"{CIPHER_FILE} not found.")
        sys.exit(1)

    # 2. Mission Briefing
    header("🔐 Vigenère Cipher Breaker")
    
    print(f"📄 Target File: {Colors.BOLD}{CIPHER_FILE}{Colors.END}")
    print("🎯 Goal: Decrypt the message using the correct Keyword.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Cipher:** Vigenère (Polyalphabetic Substitution).")
    print("   ➤ **The Challenge:** Each letter is shifted differently based on a keyword.")
    print("   ➤ **The Clue:** The admin asked: \"What is the opposite of `logout`?\"\n")
    
    try:
        ciphertext = cipher_path.read_text(encoding="utf-8")
    except Exception as e:
        print_error(f"Failed to load cipher text from storage: {e}")
        sys.exit(1)

    require_input("Type 'ready' to understand the decryption logic: ", "ready")

    # 3. Algorithm Explanation
    header("🛠️ Behind the Scenes")
    print("Deciphering Vigenère by hand is tedious. In a real scenario, you would")
    print("write a script to handle the math for you.\n")
    print("I have a decryption algorithm loaded into memory that does exactly this:\n")
    print(f"   1. It takes your {Colors.BOLD}KEYWORD{Colors.END} (e.g., 'TEST').")
    print("   2. It converts the key into numbers (T=19, E=4, S=18, T=19).")
    print("   3. It subtracts those numbers from the cipher text, looping the key.\n")
    
    print("We will simulate running a command like this:\n")
    print(f"   {Colors.GREEN}python3 decrypt.py {CIPHER_FILE} [YOUR_KEY]{Colors.END}\n")
    
    require_input("Type 'start' to boot the decryption module: ", "start")

    # 4. Main Loop
    while True:
        clear_screen()
        print(f"{Colors.CYAN}{Colors.BOLD}🔐 Vigenère Decryption Console{Colors.END}")
        print("=============================\n")
        
        # Show encrypted snippet
        print(f"📄 {CIPHER_FILE} (First 80 chars):")
        print(f"> {Colors.YELLOW}{ciphertext[:80]}...{Colors.END}\n")

        # Utilize unified safe_input to protect terminal loops
        key = safe_input(f"{Colors.YELLOW}🔑 Enter the keyword based on the clue (or 'exit'): {Colors.END}").strip().lower()

        if key == "exit":
            print(f"\n{Colors.CYAN}👋 Exiting.{Colors.END}")
            break

        if not key:
            continue

        print(f"\n⏳ Running decryption algorithm with key: '{Colors.BOLD}{key}{Colors.END}'")
        spinner("Processing")

        plaintext = vigenere_decrypt(ciphertext, key)
        flag = find_flag(plaintext)

        # Show Results
        clear_screen()
        print(f"🔑 Key Used: '{Colors.BOLD}{key}{Colors.END}'")
        print("=============================")
        print("📄 Resulting Text:")
        print("-" * 50)
        print(plaintext[:500] + ("..." if len(plaintext) > 500 else ""))
        print("-" * 50 + "\n")

        if flag:
            print_success(f"SUCCESS! Flag found: {Colors.BOLD}{flag}{Colors.END}")
            print(f"📁 Full output saved to: {Colors.BOLD}{OUTPUT_FILE}{Colors.END}\n")
            try:
                output_path.write_text(plaintext, encoding="utf-8")
            except Exception as e:
                print_error(f"Failed to record decoded data to disk: {e}")
            
            pause("Press ENTER to close this terminal...")
            break
        else:
            print_error("FAILURE: No valid flag found.")
            print("   The output is still garbled. That was the wrong key.")
            print(f"   (Hint: Read the clue again. What do you do to start a session?)\n")
            
            choice = safe_input(f"{Colors.YELLOW}🔁 Try again? (y/n): {Colors.END}").strip().lower()
            if choice == 'n':
                print(f"\n{Colors.CYAN}👋 Exiting.{Colors.END}")
                sys.exit(0)

if __name__ == "__main__":
    main()