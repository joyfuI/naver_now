# 출처: https://stackoverflow.com/questions/36762098/how-to-decrypt-password-from-javascript-cryptojs-aes-encryptpassword-passphras
import base64
from hashlib import md5

from Crypto.Cipher import AES as CryptoAES
from Crypto.Random import get_random_bytes


class AES(object):
    BLOCK_SIZE = 16

    @staticmethod
    def pad(data):
        length = AES.BLOCK_SIZE - (len(data) % AES.BLOCK_SIZE)
        return data + (chr(length) * length).encode()

    @staticmethod
    def unpad(data):
        return data[: -(data[-1] if isinstance(data[-1], int) else ord(data[-1]))]

    @staticmethod
    def bytes_to_key(data, salt, output=48):
        assert len(salt) == 8, len(salt)
        data += salt
        key = md5(data).digest()
        final_key = key
        while len(final_key) < output:
            key = md5(key + data).digest()
            final_key += key
        return final_key[:output]

    @staticmethod
    def encrypt(message, passphrase):
        salt = get_random_bytes(8)
        key_iv = AES.bytes_to_key(passphrase.encode(), salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = CryptoAES.new(key, CryptoAES.MODE_CBC, iv)
        return base64.b64encode(
            b"Salted__" + salt + aes.encrypt(AES.pad(message.encode()))
        ).decode()

    @staticmethod
    def decrypt(encrypted, passphrase):
        encrypted = base64.b64decode(encrypted)
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = AES.bytes_to_key(passphrase.encode(), salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = CryptoAES.new(key, CryptoAES.MODE_CBC, iv)
        return AES.unpad(aes.decrypt(encrypted[16:])).decode()
