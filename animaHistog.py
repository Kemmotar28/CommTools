import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Leer datos desde el archivo
with open('datos.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Procesar categorías y valores
categorias = lines[0].strip().split(',')
valores = list(map(float, lines[1].strip().split(',')))  # Convierte a números

n = len(valores)

# Configurar la figura
fig, ax = plt.subplots(figsize=(10, 6))

# Inicializar barras horizontales con altura 0 (ancho 0 en horizontal)
bars = ax.barh(categorias, [0] * n, color='gray', edgecolor='black', height=0.6)

# Determinar colores finales (rojo para negativos, verde para positivos)
colores_finales = ['green' if v >= 0 else 'red' for v in valores]

# Ajustar límites del eje X (ahora es el eje de valores, horizontal)
max_abs = max(abs(v) for v in valores)
ax.set_xlim(-max_abs * 1.1, max_abs * 1.1)
ax.axvline(0, color='black', linewidth=0.8)  # Línea en x=0 para referencia
ax.set_title("Histograma Animado Horizontal", fontsize=14)
ax.grid(axis='x', linestyle='--', alpha=0.7)
ax.set_xlabel("Valor")
ax.set_ylabel("Categoría")

# Función de animación
def animate(i):
    for j, bar in enumerate(bars):
        if j <= i:
            bar.set_width(valores[j])       # En horizontal, el "ancho" es el valor
            bar.set_color(colores_finales[j])  # Aplicar color según signo
        else:
            bar.set_width(0)
            bar.set_color('gray')  # Opcional: mantener gris hasta que les toque
    return bars

# Crear animación
ani = animation.FuncAnimation(
    fig, animate, frames=n,
    interval=800,  # 0.8 segundos entre barras
    blit=False,
    repeat=False
)

plt.tight_layout()
plt.show()