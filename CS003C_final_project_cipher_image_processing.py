###
## This program takes a BMP image and writes the characters of
## an encrypted text at the byte position of the red color in
## every pixel with a prime index.
## Designed by: Kenneth Hanson
##

from io import SEEK_CUR
from sys import exit
from sys import argv
import random

class ImageProcess:
   """
   ImageProcess class for writing encrypted messages to 
   pixels of image using the Vigenère cipher method.
   """
   def __init__(self, filename):
      """
      Initializes the ImageProcess object.

      Parameters:
      - filename(str): The name of the image file.
      """
      self._filename = filename
      self._imageFile = ""
      self._cipherText = ""
      self._checkMessage = "" 
      self._encryptedChars = []
      self._width = 0
      self._start = 0
      self._height = 0
      
   def enter_cipher_text(self, cipherText):
      """
      Enters the cipher text for writing.

      Parameters:
      - cipherText (str): The encrypted message provided by the user.
      """
      self._cipherText = cipherText
      for i in range(len(cipherText)):
            # Takes encrypted text, converts each character to its ASCII code, and 
            # appends the ASCII code to the empty list encryptedChars.
         self._encryptedChars.append(ord(cipherText[i]))

   def main(self):
      askCheck = input("Enter Y if you want to check the message, else enter N: ")
      self._checkMessage = askCheck

      # Opens the binary file for reading and writing.
      self._imageFile = open(self._filename, "rb+")

      # Extracts information from the image header.
      fileSize = self.read_int(2)
      self._start = self.read_int(10)
      self._width = self.read_int(18)
      self._height = self.read_int(22)

      maxStartingPoint = self._width - self._start
      startingPoint = self.generate_prime_start(10, min(99, maxStartingPoint))
      textSize = len(self._encryptedChars)
      skipOrder = "8082737769"
      userHint = str(startingPoint) + skipOrder + str(textSize)
      hintMessage = print(f'Here is your clue: {userHint}')
      imageSize = self._width * self._height * 3

      # Determine that scan lines occupy multiples of four bytes.
      padding = self.calculate_padding(0, self._width)
      
      charsCount = 0
      for row in range(self._height):
         for col in range(self._width):
            if self.is_prime(col):
               self.write_pixel(chars=self._encryptedChars,i=charsCount, checkMessage=self._checkMessage, prime=True)
               charsCount += 1
            else:
               self.write_pixel()
      
         # Moves file pointer to skip over empty spaces and/or padding.
         padding = self.calculate_padding(self._imageFile.tell(), self._width)
         self._imageFile.seek(padding, SEEK_CUR)

      self._imageFile.close()

      if self._checkMessage == "Y":
         print("Now decrypt the message according to the Vigenère cipher method.")

   def calculate_padding(self, current_position):
      """
      Calculates the padding necessary to align the current position to the next multiple of 4.

      Parameters:
      - current_position (int): The current index of the pointer.

      Returns:
      -int: Padding of 0 if the number of row pixels is a multiple of 4, else returns
            the number of bytes requires to align to the next multiple of 4.
      """
      # The total size of the row in bytes.
      line_size = self._width * 3 
      # Checks if the total size of the row plus the 
      # current position is already a multiple of 4.
      if (current_position + line_size) % 4 == 0:
         return 0
      else:
         # Determines how many bytes are required to reach the next 
         # multiple of 4, subtracting that number from 4 to find the number 
         # of bytes necessary to align to the next multiple of 4.
         return 4 - (current_position + line_size) % 4

   def is_prime(self, col):
      """
      Determines if the index position of the column is prime.

      Parameters:
      - col (int): The column position in the row.

      Returns:
      - bool: True if it is prime, else False.
      """
      if col < 2:
         return False
      for i in range(2, int(col**0.5) + 1):
         if col % i == 0:
            return False
      return True

   def generate_prime_start(self, min_value, max_value):
      """
      Generates a prime number index at which the first character of the cipher text is inserted.

      Parameters:
      - min_value (int): The lower bound of the range.
      - max_value (int): The upper bound of the range.

      Returns:
      - int: The random prime number integer.
      """
      num = random.randint(min_value, max_value)
      
      # Continues generating number until it is prime.
      while not self.is_prime(num):
         num = random.randint(min_value, max_value)
         
      return num

   def write_pixel(self, chars=[], i=0, checkMessage="N", prime=False): 
      """
      Takes pixel and inserts character at the red byte representing 
      8 bits if it is in a prime position in the row, until all characters
      in the encrypted message are stored. If not prime, it writes
      the original pixel.

      Parameters:
      - chars (list): The the list of characters or ASCII codes from the encrypted text.
      - i (int): The index in the chars list when called.
      - width (int): The width of the image row.
      - checkMessage (str): The keyword argument to indicate whether to print characters.
      - prime (bool): The keyword argument to indicate if pixel position is prime.
      """
      theBytes = self._imageFile.read(3)

      if len(theBytes) == 3:
         red = theBytes[0]
         green = theBytes[1]
         blue = theBytes[2]

         if prime == True and i < len(chars):
            self._imageFile.seek(-3, SEEK_CUR)
               # Inserts ASCII number of encrypted text character where the byte for red was placed.
            self._imageFile.write(bytes([chars[i], green, blue]))
            if checkMessage == "Y":
               print(bytes([chars[i], green, blue]))
         else:
            self._imageFile.seek(-3, SEEK_CUR)
            self._imageFile.write(bytes([red, green, blue]))

   def read_int(self, offset):
      """
      Converts a series of four bytes to a little-endian integer.

      Parameters:
      - offset (int): The offset to read the integer based on the header information.

      Returns:
      - int: The integer from the four bytes at that offset 
             (2 for file size; 10 for offset; 18 for width; and 22 for height.)
      """
      self._imageFile.seek(offset)

      theBytes = self._imageFile.read(4)
      result = 0
      base = 1
      for i in range(4):
         result = result + theBytes[i] * base
         base = base * 256

      return result

def vigenereCipher(textInput, keyword, mode):
    """
    Converts the input text by the user and returns the encrypted or decrypted text according
    to the Vigenère cipher method with the shift of the uppercase character in the keyword.

    Parameters:
    - textInput (str): The character in the text to be encoded or decoded.
    - keyword (str): The keyword on which encryption or decryption shift is based.
    - mode (str): The mode indicating whether to 'encrypt' or 'decrypt'.

    Returns:
    - resultText (str): The resulting text of encryption or decryption.
    """
    resultText = ""
    keyword = keyword.upper()
    key_index = 0

    for char in textInput:
        if char.isalpha():
            # Determines difference of input character from capital letter A in the ASCII table.
            shift = ord(char.upper()) - ord('A')

            if mode == 'encrypt':
               # Adds by keyword character from capital letter A for encryption.
               shift += (ord(keyword[key_index]) - ord('A'))
            elif mode == 'decrypt':
               # Subtracts by keyword character from capital letter A for decryption.
               shift -= (ord(keyword[key_index]) - ord('A'))

            # Ensures the shift does not exceed the length of the alphabet of 26.
            encrypt_shift = shift % 26

            # Determines whether textInput character is uppercase or lowercase,
            # providing the offset to be used in calculation.
            if char.isupper():
               resultText += chr(encrypt_shift + ord('A'))
            else:
               resultText += chr(encrypt_shift + ord('a'))

            key_index += 1
            if key_index == len(keyword):
               key_index = 0
        else:
            resultText += char
    
    return resultText

if __name__ in '__main__':
   filename = input("Enter name of image file: ")
   userText = input("Enter the text you want to encrypt: ")
   userKey = input("Enter the key you want to use: ")

   encryptedText = vigenereCipher(userText, userKey)
   decryptedText = vigenereCipher(encryptedText, userKey)

   cipherImage = ImageProcess(filename)
   cipherImage.enter_cipher_text(encryptedText)
   cipherImage.main()