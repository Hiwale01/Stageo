import cv2
import os
import hashlib
import numpy as np

def hash_password(password, salt):
    # Use a combination of password and salt to create a hash
    hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed_password

def compress_image(img):
    # Use cv2 to compress the image
    _, compressed_img = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    compressed_img = cv2.imdecode(compressed_img, 1)  # Use 1 for 3-channel images
    return compressed_img

def embed_message(img, message, password):
    salt = os.urandom(16).hex()  # Generate a random salt
    hashed_password = hash_password(password, salt)

    # Use the modulo operation to ensure the seed falls within the valid range
    seed = int(hashed_password, 16) % (2**32 - 1)
    np.random.seed(seed)  # Seed the random number generator

    h, w, c = img.shape
    total_pixels = h * w * c
    message_length = len(message)

    if total_pixels < message_length * 8:
        raise ValueError("Message is too long for the given image.")

    # Flatten the image to a 1D array
    flat_img = img.flatten()

    # Convert the message to a binary string
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    # Embed the message in the least significant bits
    for i in range(message_length * 8):
        bit = int(binary_message[i])
        flat_img[i] = (flat_img[i] & 0xFE) | bit

    # Reshape the array back to the original image shape
    embedded_img = flat_img.reshape((h, w, c))

    return embedded_img, salt

def extract_message(img, password, salt, message_length):
    hashed_password = hash_password(password, salt)

    # Use the modulo operation to ensure the seed falls within the valid range
    seed = int(hashed_password, 16) % (2**32 - 1)
    np.random.seed(seed)  # Seed the random number generator

    h, w, c = img.shape

    # Flatten the image to a 1D array
    flat_img = img.flatten()

    # Extract the message from the least significant bits
    binary_message = ''
    for i in range(message_length * 8):
        bit = flat_img[i] & 1
        binary_message += str(bit)

    # Convert the binary string back to characters
    extracted_message = ''.join([chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8)])

    return extracted_message

# Example usage
img_path = "lux.jpg"
if not os.path.isfile(img_path):
    print(f"Error: Image file '{img_path}' not found.")
    exit()

img = cv2.imread(img_path)

# Compress the image before embedding the message
compressed_img = compress_image(img)

# Input validation for secret message and password
secret_message = input("Enter the secret message: ").strip()
password = input("Enter the password: ").strip()

if not secret_message or not password:
    print("Error: Please provide a valid secret message and password.")
    exit()

try:
    # Embed the message in the image
    embedded_img, salt = embed_message(compressed_img, secret_message, password)

    # Save the image with the embedded message
    cv2.imwrite("EmbeddedMsg.jpg", embedded_img)
    print("Message successfully embedded.")
    os.system("start EmbeddedMsg.jpg")

    # Prompt for decryption password
    decryption_password = input("Enter the decryption password: ").strip()

    # Extract the message from the image
    extracted_message = extract_message(embedded_img, decryption_password, salt, len(secret_message))
    print("Extracted Message:", extracted_message.strip())

except ValueError as ve:
    print(f"ValueError: {ve}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
