import random

# --- EXAMEN ---
P = 751 # Este es el número primo que define el tamaño del campo.
A = -1 # Coeficiente 'a' de la ecuación y² = x³ + ax + b.
B = 188 # Coeficiente 'b' de la ecuación.
G = (0, 376) # Punto base o generador.
D_PRIVADA = 656 # Tu clave secreta (d). Solo yo la conozco jejeje.

def inverso_mod(k, p):
    if k % p == 0: return None
    return pow(k, p - 2, p)

def sumar_puntos(P1, P2, a, p):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1
    x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P1 != P2:
        m = ((y2 - y1) * inverso_mod(x2 - x1, p)) % p
    else:
        m = ((3 * x1**2 + a) * inverso_mod(2 * y1, p)) % p
    x3 = (m**2 - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def multiplicar_escalar(k, punto, a, p):
    res = None
    temp = punto
    while k > 0:
        if k & 1: res = sumar_puntos(res, temp, a, p)
        temp = sumar_puntos(temp, temp, a, p)
        k >>= 1
    return res

def ejecutar_examen():
    print("--- VALIDACIÓN DE CALIBRACIÓN ---")
    # Validación de Clave Pública esperada
    Q_publica = multiplicar_escalar(D_PRIVADA, G, A, P)
    print(f"Punto G: {G}")
    print(f"Clave Privada d: {D_PRIVADA}")
    print(f"Clave Pública Q (d*G): {Q_publica}")
    
    print("\n" + "="*40)
    mensaje = input("Ingrese la palabra (ej. Adios): ")
    
    # Mapeo ASCII -> Punto (Método: ord(c) * G)
   
    tabla_puntos = {multiplicar_escalar(i, G, A, P): chr(i) for i in range(256)}

    # CIFRADO
    cifrado = []
    for char in mensaje:
        Pm = multiplicar_escalar(ord(char), G, A, P)
        k_efi = random.randint(2, P-2)
        C1 = multiplicar_escalar(k_efi, G, A, P)
        S = multiplicar_escalar(k_efi, Q_publica, A, P)
        C2 = sumar_puntos(Pm, S, A, P)
        cifrado.append((C1, C2))
    
    print(f"\n[+] Mensaje Cifrado (C1, C2):")
    for idx, par in enumerate(cifrado):
        print(f" Letra '{mensaje[idx]}': {par}")

    # DESCIFRADO
    descifrado = ""
    for C1, C2 in cifrado:
        S_desc = multiplicar_escalar(D_PRIVADA, C1, A, P)
        S_neg = (S_desc[0], (-S_desc[1]) % P)
        M_recup = sumar_puntos(C2, S_neg, A, P)
        descifrado += tabla_puntos.get(M_recup, "?")

    print(f"\n[!] Resultado Final Descifrado: {descifrado}")

if __name__ == "__main__":
    ejecutar_examen()