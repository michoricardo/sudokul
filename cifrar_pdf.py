"""
Pone contraseña (cifrado AES-256) a un PDF, todo en tu computadora, sin internet.

Instalación (una sola vez):
    pip install pypdf cryptography

Uso:
    python cifrar_pdf.py propuesta.pdf v7k2.pdf

  - propuesta.pdf  es tu PDF original (sin contraseña)
  - v7k2.pdf       es el PDF cifrado que le entregarás tú (el PDF NO va al repositorio)

La contraseña se pide al ejecutar el script y se guarda en MAYÚSCULAS (igual que las letras
que muestra el juego). No queda escrita en ningún archivo.
"""
import getpass
import secrets
import sys

from pypdf import PdfReader, PdfWriter


def main():
    if len(sys.argv) != 3:
        sys.exit("Uso: python cifrar_pdf.py <pdf_original> <pdf_cifrado>")
    origen, destino = sys.argv[1], sys.argv[2]
    if origen == destino:
        sys.exit("El archivo de salida debe tener otro nombre para no pisar tu original.")

    lector = PdfReader(origen)
    if lector.is_encrypted:
        sys.exit("Ese PDF ya tiene contraseña. Usa el original sin cifrar.")

    clave = getpass.getpass("Contraseña (la palabra secreta): ").strip().upper()  # el juego muestra las letras en mayúsculas
    if getpass.getpass("Repítela: ").strip().upper() != clave:
        sys.exit("No coinciden. Intenta de nuevo.")
    if len(clave) < 3:
        sys.exit("Contraseña demasiado corta.")
    if len(clave) < 8:
        print("Aviso: una contraseña corta se puede adivinar por fuerza bruta.")

    escritor = PdfWriter()
    escritor.append(lector)
    # La contraseña de propietario es aleatoria y se descarta: solo importa la de apertura.
    escritor.encrypt(user_password=clave, owner_password=secrets.token_urlsafe(32), algorithm="AES-256")
    with open(destino, "wb") as f:
        escritor.write(f)

    # Verificación: sin clave no abre, con clave sí y con las mismas páginas.
    prueba = PdfReader(destino)
    assert prueba.is_encrypted, "El PDF no quedó cifrado."
    assert prueba.decrypt("clave-incorrecta-xyz") == 0, "Se abrió con una clave incorrecta."
    prueba = PdfReader(destino)
    assert prueba.decrypt(clave) != 0, "No abre con tu contraseña."
    assert len(prueba.pages) == len(lector.pages), "Cambió el número de páginas."
    print(f"Listo: {destino} ({len(prueba.pages)} páginas) cifrado con AES-256 y verificado.")


if __name__ == "__main__":
    main()
