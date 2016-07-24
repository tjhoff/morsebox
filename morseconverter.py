text_to_morse = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "...._",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ".": ".-.-.-",
    ",": "--..--",
    ";": "---...",
    "?": "..--..",
    "@": ".--.-."}

morse_to_text = {}
for key, val in text_to_morse.items():
    morse_to_text[val] = key

def convert_text(text):
    morse = ""
    for char in text:
        c = char.upper()
        if c == " ":
            morse += "|"
        elif c in text_to_morse:
            morse += text_to_morse[c] + " "

    return morse

def convert_morse(morse):
    words = morse.split("|")
    text = ""

    for word in words:
        characters = word.split(" ")
        for c in characters:
            char = convert_morse_char(c)
            if char:
                text += char
        text += " "

    if text == "":
        text = None

    return text

def convert_morse_char(c):

    if (not c) or (c not in morse_to_text):
        return None
    else:
        return morse_to_text[c]

if __name__ == "__main__":
    text = raw_input()

    morse = convert_text(text)
    print morse
    print convert_morse(morse)
