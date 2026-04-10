import random
import matplotlib
# Forzamos a que no use ventana externa para evitar el error de "documento en blanco"
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os

# --- PARÁMETROS DEL EXAMEN ---
P, A, B = 751, -1, 188
G = (0, 376) 
D_PRIVADA = 656 

def inverso_mod(k, p):
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

def graficar_y_guardar(a, b, p, pts_msj, pts_cif):
    print("\n[!] Calculando puntos para la grafica...")
    x_todos, y_todos = [], []
    for x in range(p):
        rhs = (x**3 + a*x + b) % p
        for y in range(p):
            if (y**2) % p == rhs:
                x_todos.append(x)
                y_todos.append(y)

    plt.figure(figsize=(10, 7))
    plt.scatter(x_todos, y_todos, s=2, color='lightgray', label='Puntos de la Curva')
    
    # Mensaje original
    xm = [p[0] for p in pts_msj if p is not None]
    ym = [p[1] for p in pts_msj if p is not None]
    plt.scatter(xm, ym, color='blue', s=80, label='Mensaje Original (Pm)', edgecolors='black')

    # Criptograma
    xc = [p[0] for p in pts_cif if p is not None]
    yc = [p[1] for p in pts_cif if p is not None]
    plt.scatter(xc, yc, color='red', s=80, label='Criptograma (C2)', marker='X')

  
    plt.title(f'Curva Eliptica: y^2 = x^3 - x + 188 (mod {p})')
    plt.xlabel('Eje X')
    plt.ylabel('Eje Y')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    
    # GUARDAR
    nombre_img = 'resultado_grafica.png'
    plt.savefig(nombre_img)
    print(f"\n[LISTO] Grafica guardada exitosamente como: {nombre_img}")

def main():
    Q_pub = multiplicar_escalar(D_PRIVADA, G, A, P)
    print(f"--- SISTEMA ECC ---")
    print(f"Clave Publica Q: {Q_pub}\n")
    
    mensaje = input("Ingresa la palabra: ")
    
    inv_tabla = {chr(i): multiplicar_escalar(i, G, A, P) for i in range(256)}
    puntos_msj, puntos_c2, cifrado = [], [], []

    for char in mensaje:
        Pm = inv_tabla.get(char)
        puntos_msj.append(Pm)
        k_efi = random.randint(2, P-2)
        C1 = multiplicar_escalar(k_efi, G, A, P)
        S = multiplicar_escalar(k_efi, Q_pub, A, P)
        C2 = sumar_puntos(Pm, S, A, P)
        puntos_c2.append(C2)
        cifrado.append((C1, C2))

    print(f"\n[+] Proceso terminado.")
    graficar_y_guardar(A, B, P, puntos_msj, puntos_c2)

if __name__ == "__main__":
    main()