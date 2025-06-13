import random
import string

def generate_password(length=12):
    """
    Generate a random password with the specified length.
    The password includes uppercase letters, lowercase letters, numbers, and special characters.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(characters, k=length))

def copy_to_clipboard(root, text):
    """
    Copy text to clipboard and show a success message
    """
    root.clipboard_clear()
    root.clipboard_append(text)
    return "Password copied to clipboard!" 