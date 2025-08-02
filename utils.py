def encodeRot13(input_text):
    """
    Encode text using ROT13 cipher.
    """ 
    output = ""
    for letter in input_text:
        if letter == ' ':
            output += ' '
        else:
            pos = ord(letter) - ord('A')
            new_pos = (pos + 13) % 26
            new_letter = chr(new_pos + ord('A'))
            output += new_letter
    return output
