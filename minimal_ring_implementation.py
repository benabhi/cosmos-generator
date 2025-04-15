from PIL import Image, ImageDraw, ImageChops
import numpy as np

# Dimensiones del lienzo
width, height = 800, 800
center_x, center_y = width // 2, height // 2

# Crear lienzo principal
image = Image.new("RGBA", (width, height), "black")

# Parámetros del planeta
planet_radius = 100

# Parámetros del anillo (elipse)
outer_rx, outer_ry = 200, 50
inner_rx, inner_ry = 160, 30

# Crear la capa base del anillo (elipse con hueco)
ring_layer = Image.new("1", (width, height), 0)
draw_ring = ImageDraw.Draw(ring_layer)
draw_ring.ellipse(
    [center_x - outer_rx, center_y - outer_ry, center_x + outer_rx, center_y + outer_ry],
    fill=1
)
draw_ring.ellipse(
    [center_x - inner_rx, center_y - inner_ry, center_x + inner_rx, center_y + inner_ry],
    fill=0
)

# Capa del planeta
planet_layer = Image.new("1", (width, height), 0)
draw_planet = ImageDraw.Draw(planet_layer)
draw_planet.ellipse(
    [center_x - planet_radius, center_y - planet_radius, center_x + planet_radius, center_y + planet_radius],
    fill=1
)

# Arcos externos: diferencia entre la elipse del anillo y el planeta
ring_arcs = ImageChops.subtract(ring_layer.convert("L"), planet_layer.convert("L"))

# Crear una máscara para la mitad frontal (solo la mitad inferior de la imagen)
front_mask = Image.new("L", (width, height), 0)
draw_front = ImageDraw.Draw(front_mask)
draw_front.rectangle([0, center_y, width, height], fill=255)

# Intersección entre el anillo y el planeta
ring_intersection = ImageChops.logical_and(ring_layer, planet_layer)

# La banda frontal es solo la mitad frontal de la intersección
ring_front = ImageChops.multiply(ring_intersection.convert("L"), front_mask)

# Crear la imagen de los arcos externos
ring_arcs_colored = Image.new("RGBA", (width, height))
ring_arcs_colored.paste((160, 160, 160, 255), mask=ring_arcs)

# Crear la imagen de la banda frontal
ring_front_colored = Image.new("RGBA", (width, height))
ring_front_colored.paste((180, 180, 180, 255), mask=ring_front)

# Crear la imagen del planeta
planet_colored = Image.new("RGBA", (width, height))
draw_colored_planet = ImageDraw.Draw(planet_colored)
draw_colored_planet.ellipse(
    [center_x - planet_radius, center_y - planet_radius, center_x + planet_radius, center_y + planet_radius],
    fill=(63, 167, 214, 255)
)

# Composición final (orden de dibujo: arcos externos → planeta → banda frontal)
image.paste(ring_arcs_colored, (0, 0), ring_arcs_colored)
image.paste(planet_colored, (0, 0), planet_colored)
image.paste(ring_front_colored, (0, 0), ring_front_colored)

# Mostrar y guardar la imagen
image.show()
image.save("planeta_con_anillo_corregido.png")