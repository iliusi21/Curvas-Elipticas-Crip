import random
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ==============================================================
# PARÁMETROS
# ==============================================================
P = 751
A = -1
B = 188
D_PRIVADA = 656

MENSAJE = "Perro"   

# ==============================================================
# ARITMÉTICA ECC
# ==============================================================

def inverso_mod(k, p):
    k = k % p
    if k == 0:
        return None
    return pow(k, p - 2, p)

def sumar_puntos(P1, P2, a, p):
    if P1 is None:
        return P2
    if P2 is None:
        return P1

    x1, y1 = P1
    x2, y2 = P2

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if P1 != P2:
        inv = inverso_mod(x2 - x1, p)
        if inv is None:
            return None
        m = ((y2 - y1) * inv) % p
    else:
        inv = inverso_mod(2 * y1, p)
        if inv is None:
            return None
        m = ((3 * x1 ** 2 + a) * inv) % p

    x3 = (m ** 2 - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def multiplicar_escalar(k, punto, a, p):
    resultado = None
    temp = punto
    while k > 0:
        if k & 1:
            resultado = sumar_puntos(resultado, temp, a, p)
        temp = sumar_puntos(temp, temp, a, p)
        k >>= 1
    return resultado

# ==============================================================
# PUNTOS
# ==============================================================

def encontrar_puntos_curva(a, b, p):
    puntos = []
    for x in range(p):
        rhs = (pow(x, 3, p) + a * x + b) % p
        for y in range(p):
            if pow(y, 2, p) == rhs:
                puntos.append((x, y))
    return puntos

def orden_punto(punto, a, p, limite=5000):
    Q = punto
    for i in range(1, limite + 1):
        if Q is None:
            return i
        Q = sumar_puntos(Q, punto, a, p)
    return None

def encontrar_generador(a, b, p, min_orden=100):
    print("Buscando punto generador G en la curva...")
    puntos = encontrar_puntos_curva(a, b, p)
    print(f"Puntos encontrados: {len(puntos)}")

    mejor_punto = None
    mejor_orden = 0

    for pt in puntos:
        orden = orden_punto(pt, a, p)
        if orden and orden > mejor_orden:
            mejor_orden = orden
            mejor_punto = pt
            if orden >= min_orden:
                break

    print(f"G seleccionado: {mejor_punto} (orden {mejor_orden})\n")
    return mejor_punto, mejor_orden, puntos

# ==============================================================
# CIFRADO
# ==============================================================

def construir_tabla(G, a, p, rango=256):
    return {multiplicar_escalar(i, G, a, p): chr(i) for i in range(rango)}

def cifrar_mensaje(mensaje, G, Q_publica, a, p):
    cifrado = []
    for char in mensaje:
        Pm = multiplicar_escalar(ord(char), G, a, p)
        k = random.randint(2, p - 2)
        C1 = multiplicar_escalar(k, G, a, p)
        S  = multiplicar_escalar(k, Q_publica, a, p)
        C2 = sumar_puntos(Pm, S, a, p)
        cifrado.append((C1, C2))
    return cifrado

def descifrar_mensaje(cifrado, d_privada, G, a, p, tabla):
    texto = ""
    for C1, C2 in cifrado:
        S = multiplicar_escalar(d_privada, C1, a, p)
        S_neg = (S[0], (-S[1]) % p)
        M = sumar_puntos(C2, S_neg, a, p)
        texto += tabla.get(M, "?")
    return texto

# ==============================================================
# GRÁFICAS
# ==============================================================

def graficar_ecc(puntos_finitos, G, Q, a, b, p):

    fig = plt.figure(figsize=(14, 6))
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.3)

    # ----------- CURVA REAL ----------- #
    ax1 = fig.add_subplot(gs[0])

    x_vals = np.linspace(-10, 10, 5000)
    y2 = x_vals**3 + a * x_vals + b

    y2[y2 < 0] = np.nan  # evitar errores

    y_pos = np.sqrt(y2)
    y_neg = -y_pos

    ax1.plot(x_vals, y_pos, color='blue')
    ax1.plot(x_vals, y_neg, color='red', linestyle='--')

    ax1.set_title("Curva en ℝ: y² = x³ - x + 188")
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    ax1.grid(True, linestyle=':')
    ax1.set_aspect('equal', adjustable='box')

    # ----------- CAMPO FINITO ----------- #
    ax2 = fig.add_subplot(gs[1])

    xs = [pt[0] for pt in puntos_finitos]
    ys = [pt[1] for pt in puntos_finitos]

    ax2.scatter(xs, ys, s=2, color='blue')

    ax2.scatter(G[0], G[1], color='green', s=60, label="G")
    ax2.scatter(Q[0], Q[1], color='orange', s=60, label="Q")

    ax2.set_xlim(0, p)
    ax2.set_ylim(0, p)

    ax2.set_title(f"Curva en F{p}")
    ax2.set_xlabel("x")
    ax2.set_ylabel("y")
    ax2.legend()

    plt.tight_layout()
    plt.savefig("ecc_curvas.png")
    print("Gráfica guardada como ecc_curvas.png")
    plt.show()

# ==============================================================
# MAIN
# ==============================================================

def ejecutar_examen():

    print("=== ECC ===")

    G, orden_G, puntos = encontrar_generador(A, B, P)

    Q = multiplicar_escalar(D_PRIVADA, G, A, P)

    print("G:", G)
    print("Q:", Q)

    mensaje = MENSAJE  

    tabla = construir_tabla(G, A, P)

    cifrado = cifrar_mensaje(mensaje, G, Q, A, P)

    print("\nCifrado:")
    for i, par in enumerate(cifrado):
        print(mensaje[i], par)

    descifrado = descifrar_mensaje(cifrado, D_PRIVADA, G, A, P, tabla)

    print("\nDescifrado:", descifrado)

    graficar_ecc(puntos, G, Q, A, B, P)

if __name__ == "__main__":
    ejecutar_examen()
