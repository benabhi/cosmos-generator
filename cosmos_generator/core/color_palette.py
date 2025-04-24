"""
Color palette management for celestial bodies.
"""
from typing import Dict, List, Tuple, Union, Optional
import random

# Type aliases
RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]
Color = Union[RGB, RGBA]

from cosmos_generator.core.interfaces import ColorPaletteInterface


class ColorPalette(ColorPaletteInterface):
    """
    Manages color schemes for different celestial bodies.
    Provides methods for generating, manipulating, and retrieving colors.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize a color palette with an optional seed for reproducibility.

        Args:
            seed: Random seed for reproducible color generation
        """
        self.seed = seed if seed is not None else random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)

        # Predefined color palettes for different planet types
        self.planet_palettes: Dict[str, Dict[str, List[Color]]] = {
            "Desert": {
                # Paleta 1: Clásica (tonos arena y marrón)
                "base_1": [(210, 180, 140), (244, 164, 96), (222, 184, 135)],
                "highlight_1": [(255, 222, 173), (245, 222, 179)],
                "shadow_1": [(139, 69, 19), (160, 82, 45)],

                # Paleta 2: Rojiza (tonos rojizos y ocres)
                "base_2": [(210, 105, 30), (205, 133, 63), (230, 140, 50)],
                "highlight_2": [(255, 160, 122), (250, 170, 100)],
                "shadow_2": [(128, 0, 0), (139, 26, 26), (165, 42, 42)],

                # Paleta 3: Dorada (tonos dorados y amarillos)
                "base_3": [(218, 165, 32), (238, 221, 130), (240, 230, 140)],
                "highlight_3": [(250, 250, 210), (255, 236, 139)],
                "shadow_3": [(184, 134, 11), (205, 149, 12), (153, 101, 21)],
            },
            "Rocky": {
                # Palette 1: Stone Gray (grays and dark browns)
                "base_1": [(105, 105, 105), (112, 128, 144), (119, 136, 153)],  # Gray base
                "highlight_1": [(169, 169, 169), (192, 192, 192), (211, 211, 211)],  # Light gray highlights
                "shadow_1": [(47, 79, 79), (65, 65, 65), (84, 84, 84)],  # Dark gray shadows
                "crater_1": [(72, 61, 139), (85, 85, 85), (95, 95, 95)],  # Crater color
                "fracture_1": [(40, 40, 40), (50, 50, 50), (60, 60, 60)],  # Fracture color
                "peak_1": [(220, 220, 220), (230, 230, 230), (240, 240, 240)],  # Mountain peak color

                # Palette 2: Dark Copper (muted copper and dark browns)
                "base_2": [(101, 67, 33), (95, 61, 30), (85, 55, 25)],  # Dark copper base
                "highlight_2": [(128, 85, 51), (115, 78, 45), (110, 70, 40)],  # Muted copper highlights
                "shadow_2": [(60, 40, 20), (50, 35, 15), (40, 30, 10)],  # Very dark brown shadows
                "crater_2": [(70, 45, 25), (65, 40, 20), (55, 35, 15)],  # Crater color
                "fracture_2": [(45, 30, 15), (40, 25, 10), (35, 20, 5)],  # Fracture color
                "peak_2": [(140, 95, 60), (130, 90, 55), (120, 85, 50)],  # Mountain peak color

                # Palette 3: Slate Blue (bluish-grays and dark blues)
                "base_3": [(112, 128, 144), (119, 136, 153), (176, 196, 222)],  # Slate blue base
                "highlight_3": [(176, 196, 222), (202, 225, 255), (230, 230, 250)],  # Light blue highlights
                "shadow_3": [(47, 79, 79), (25, 25, 112), (72, 61, 139)],  # Dark blue shadows
                "crater_3": [(70, 70, 90), (60, 60, 80), (50, 50, 70)],  # Crater color
                "fracture_3": [(25, 25, 112), (0, 0, 128), (0, 0, 139)],  # Fracture color
                "peak_3": [(220, 220, 240), (230, 230, 250), (240, 248, 255)],  # Mountain peak color
            },
            "Furnace": {
                # Paleta 1: Rojo-Naranja (tonos de fuego y lava)
                "base_1": [(139, 0, 0), (178, 34, 34), (165, 42, 42)],
                "highlight_1": [(255, 69, 0), (255, 140, 0), (255, 165, 0)],
                "shadow_1": [(64, 0, 0), (80, 10, 10), (100, 20, 20)],
                "special_1": [(255, 215, 0), (255, 255, 0), (255, 223, 0)],  # Lava/magma

                # Paleta 2: Negro-Rojo (tonos de carbón y brasas)
                "base_2": [(50, 0, 0), (70, 10, 10), (90, 20, 20)],
                "highlight_2": [(255, 0, 0), (220, 20, 0), (200, 0, 0)],
                "shadow_2": [(20, 20, 20), (30, 30, 30), (40, 40, 40)],
                "special_2": [(255, 165, 0), (255, 140, 0), (255, 127, 80)],  # Brasas

                # Paleta 3: Marrón-Naranja (tonos de tierra quemada y fuego)
                "base_3": [(128, 42, 0), (139, 69, 19), (160, 82, 45)],
                "highlight_3": [(255, 99, 71), (255, 127, 80), (255, 140, 0)],
                "shadow_3": [(70, 35, 10), (85, 45, 15), (100, 50, 20)],
                "special_3": [(255, 215, 0), (255, 165, 0), (255, 190, 0)],  # Fuego
            },

            "Jovian": {
                # Paleta 1: Jupiter-like (ocres, naranjas, marrones)
                "base_1": [(233, 185, 110), (210, 170, 109), (240, 195, 130)],
                "highlight_1": [(255, 213, 145), (250, 200, 152), (245, 222, 179)],
                "midtone_1": [(220, 175, 100), (200, 160, 95), (215, 170, 90)],
                "shadow_1": [(160, 120, 60), (140, 100, 50), (120, 80, 40)],

                # Paleta 2: Neptune-like (azules, turquesas, cian)
                "base_2": [(70, 130, 180), (100, 149, 237), (30, 144, 255)],
                "highlight_2": [(135, 206, 250), (176, 224, 230), (173, 216, 230)],
                "midtone_2": [(65, 105, 225), (72, 118, 255), (95, 158, 160)],
                "shadow_2": [(25, 25, 112), (0, 0, 128), (0, 0, 139)],

                # Paleta 3: Púrpura-violeta (tonos morados y violetas)
                "base_3": [(147, 112, 219), (138, 43, 226), (148, 0, 211)],
                "highlight_3": [(216, 191, 216), (221, 160, 221), (238, 130, 238)],
                "midtone_3": [(153, 50, 204), (139, 0, 139), (128, 0, 128)],
                "shadow_3": [(75, 0, 130), (72, 61, 139), (106, 90, 205)],

                # Paleta 4: Verde-turquesa (tonos verdes y turquesas)
                "base_4": [(46, 139, 87), (60, 179, 113), (32, 178, 170)],
                "highlight_4": [(152, 251, 152), (144, 238, 144), (127, 255, 212)],
                "midtone_4": [(0, 128, 128), (0, 139, 139), (64, 224, 208)],
                "shadow_4": [(0, 100, 0), (0, 128, 0), (47, 79, 79)],

                # Paleta 5: Rojo-naranja (tonos cálidos intensos)
                "base_5": [(255, 99, 71), (255, 127, 80), (255, 140, 0)],
                "highlight_5": [(255, 160, 122), (255, 165, 0), (255, 215, 0)],
                "midtone_5": [(255, 69, 0), (255, 99, 71), (255, 105, 180)],
                "shadow_5": [(178, 34, 34), (139, 0, 0), (128, 0, 0)],

                # Colores para características especiales (compartidos entre paletas)
                "storm": [(255, 250, 240), (255, 245, 238), (250, 240, 230), (245, 235, 225)],  # Nubes brillantes
            },

            "Ocean": {
                # Paleta 1: Clásica (tonos turquesa)
                "base_1": [(0, 128, 128), (0, 139, 139), (32, 178, 170)],
                "highlight_1": [(64, 224, 208), (127, 255, 212)],
                "shadow_1": [(0, 105, 148), (25, 25, 112)],
                "land_1": [(240, 230, 140), (189, 183, 107)],  # Islands

                # Paleta 2: Azul profundo (tonos azul oscuro)
                "base_2": [(0, 105, 148), (65, 105, 225), (70, 130, 180)],
                "highlight_2": [(135, 206, 250), (176, 224, 230)],
                "shadow_2": [(0, 0, 128), (25, 25, 112)],
                "land_2": [(233, 150, 122), (210, 180, 140)],  # Islands

                # Paleta 3: Tropical (tonos azul verdoso)
                "base_3": [(0, 139, 139), (30, 144, 255), (0, 191, 255)],
                "highlight_3": [(173, 216, 230), (224, 255, 255)],
                "shadow_3": [(0, 0, 139), (0, 51, 102)],
                "land_3": [(244, 164, 96), (210, 105, 30)],  # Islands
            },

            "Vital": {
                # Palette 1: Earth-like (blues, greens, and browns)
                "base_1": [(70, 130, 180), (100, 149, 237), (30, 144, 255)],  # Blue base (oceans)
                "highlight_1": [(152, 251, 152), (144, 238, 144), (34, 139, 34)],  # Green highlights (vegetation)
                "shadow_1": [(139, 69, 19), (160, 82, 45), (205, 133, 63)],  # Brown shadows (land)
                "water_1": [(0, 191, 255), (30, 144, 255), (65, 105, 225)],  # Blue water
                "land_1": [(210, 180, 140), (222, 184, 135), (245, 222, 179)],  # Tan land
                "ice_1": [(240, 248, 255), (240, 255, 255), (230, 230, 250)],  # White ice

                # Palette 2: Lush (vibrant greens and deep blues)
                "base_2": [(46, 139, 87), (60, 179, 113), (32, 178, 170)],  # Green base (vegetation dominant)
                "highlight_2": [(0, 255, 127), (127, 255, 212), (152, 251, 152)],  # Bright green highlights
                "shadow_2": [(0, 100, 0), (0, 128, 0), (85, 107, 47)],  # Dark green shadows
                "water_2": [(0, 128, 128), (0, 139, 139), (70, 130, 180)],  # Teal water
                "land_2": [(154, 205, 50), (107, 142, 35), (173, 255, 47)],  # Light green land
                "ice_2": [(176, 224, 230), (175, 238, 238), (173, 216, 230)],  # Light blue ice

                # Palette 3: Diverse (varied biomes with rich colors)
                "base_3": [(0, 128, 128), (46, 139, 87), (70, 130, 180)],  # Mixed base
                "highlight_3": [(255, 215, 0), (255, 165, 0), (152, 251, 152)],  # Gold/green highlights
                "shadow_3": [(139, 0, 0), (165, 42, 42), (85, 107, 47)],  # Red/green shadows
                "water_3": [(65, 105, 225), (100, 149, 237), (30, 144, 255)],  # Deep blue water
                "land_3": [(210, 105, 30), (205, 133, 63), (222, 184, 135)],  # Orange/tan land
                "ice_3": [(240, 248, 255), (240, 255, 255), (230, 230, 250)],  # White ice
            },

            "Toxic": {
                # Palette 1: Toxic Green (fluorescent greens and dark grays)
                "base_1": [(60, 60, 60), (70, 70, 70), (80, 80, 80)],  # Dark gray base (lightened)
                "highlight_1": [(0, 255, 0), (50, 255, 50), (100, 255, 100)],  # Bright toxic green highlights
                "shadow_1": [(40, 40, 40), (50, 50, 50), (60, 60, 60)],  # Dark gray shadows (lightened)
                "special_1": [(0, 255, 0), (50, 205, 50), (0, 250, 154)],  # Fluorescent green for toxic elements

                # Palette 2: Acid Yellow (yellows and sickly greens)
                "base_2": [(70, 70, 60), (80, 80, 70), (90, 90, 80)],  # Dark yellowish-gray base (lightened)
                "highlight_2": [(255, 255, 0), (255, 215, 0), (255, 255, 50)],  # Bright yellow highlights
                "shadow_2": [(50, 50, 40), (60, 60, 50), (70, 70, 60)],  # Dark yellowish shadows (lightened)
                "special_2": [(173, 255, 47), (154, 205, 50), (255, 255, 0)],  # Acid yellow-green for toxic elements

                # Palette 3: Corrosive Purple (purples and toxic blues)
                "base_3": [(60, 50, 70), (70, 60, 80), (80, 70, 90)],  # Dark purplish-gray base (lightened)
                "highlight_3": [(138, 43, 226), (148, 0, 211), (186, 85, 211)],  # Bright purple highlights
                "shadow_3": [(45, 35, 55), (55, 45, 65), (65, 55, 75)],  # Dark purple shadows (lightened)
                "special_3": [(0, 255, 255), (0, 206, 209), (127, 255, 212)],  # Cyan/turquoise for toxic elements
            },

            "Ice": {
                # Palette 1: Arctic Blue (cold blues and whites)
                "base_1": [(176, 224, 230), (173, 216, 230), (135, 206, 235)],  # Light blue base
                "highlight_1": [(240, 248, 255), (240, 255, 255), (248, 248, 255)],  # White highlights
                "shadow_1": [(70, 130, 180), (100, 149, 237), (30, 144, 255)],  # Deeper blue shadows
                "deep_1": [(25, 25, 112), (0, 0, 128), (0, 0, 139)],  # Deep blue for crevasses
                "rock_1": [(105, 105, 105), (112, 128, 144), (119, 136, 153)],  # Gray for rocky outcrops
                "water_1": [(0, 191, 255), (30, 144, 255), (65, 105, 225)],  # Blue for water in cracks

                # Palette 2: Glacial Turquoise (turquoise and white)
                "base_2": [(175, 238, 238), (64, 224, 208), (72, 209, 204)],  # Turquoise base
                "highlight_2": [(240, 255, 255), (245, 255, 250), (255, 250, 250)],  # White highlights
                "shadow_2": [(0, 139, 139), (0, 128, 128), (32, 178, 170)],  # Darker turquoise shadows
                "deep_2": [(0, 105, 148), (0, 128, 128), (47, 79, 79)],  # Deep teal for crevasses
                "rock_2": [(169, 169, 169), (128, 128, 128), (192, 192, 192)],  # Silver-gray for rocky outcrops
                "water_2": [(127, 255, 212), (102, 205, 170), (0, 139, 139)],  # Aquamarine for water in cracks

                # Palette 3: Snow White (predominantly white with subtle blue tints)
                "base_3": [(245, 245, 255), (240, 240, 255), (235, 235, 255)],  # Almost white base with slight blue tint
                "highlight_3": [(255, 255, 255), (250, 250, 255), (245, 245, 255)],  # Pure white highlights
                "shadow_3": [(220, 225, 235), (210, 215, 230), (200, 210, 225)],  # Very light blue-gray shadows
                "deep_3": [(180, 190, 210), (170, 180, 200), (160, 170, 190)],  # Light blue for crevasses
                "rock_3": [(200, 200, 210), (190, 190, 200), (180, 180, 190)],  # Very light gray for rocky outcrops
                "water_3": [(210, 230, 250), (200, 220, 240), (190, 210, 230)],  # Very light blue for water in cracks
            },

            "Jungle": {
                # Palette 1: Emerald Green (rich greens and dark browns)
                "base_1": [(34, 139, 34), (0, 128, 0), (46, 139, 87)],  # Emerald green base
                "highlight_1": [(144, 238, 144), (152, 251, 152), (143, 188, 143)],  # Light green highlights
                "shadow_1": [(0, 100, 0), (0, 85, 0), (0, 70, 0)],  # Dark green shadows
                "vine_1": [(85, 107, 47), (107, 142, 35), (128, 128, 0)],  # Olive green vines
                "undergrowth_1": [(60, 179, 113), (32, 178, 170), (0, 139, 139)],  # Medium green undergrowth
                "canopy_1": [(0, 128, 0), (34, 139, 34), (50, 205, 50)],  # Green canopy
                "midlevel_1": [(46, 139, 87), (60, 179, 113), (32, 178, 170)],  # Sea green mid-level
                "understory_1": [(0, 100, 0), (85, 107, 47), (107, 142, 35)],  # Forest green understory
                "dark_base_1": [(0, 50, 0), (0, 40, 0), (0, 30, 0)],  # Very dark green base for bioluminescent
                "glow_bright_1": [(0, 255, 127), (50, 255, 150), (100, 255, 175)],  # Bright green glow
                "glow_medium_1": [(0, 205, 102), (0, 180, 90), (0, 155, 77)],  # Medium green glow
                "glow_dim_1": [(0, 155, 77), (0, 130, 65), (0, 105, 52)],  # Dim green glow

                # Palette 2: Tropical Jungle (vibrant greens and reds)
                "base_2": [(0, 128, 0), (34, 139, 34), (50, 205, 50)],  # Green base
                "highlight_2": [(124, 252, 0), (173, 255, 47), (154, 205, 50)],  # Lime green highlights
                "shadow_2": [(0, 100, 0), (0, 85, 0), (0, 70, 0)],  # Dark green shadows
                "vine_2": [(139, 69, 19), (160, 82, 45), (205, 133, 63)],  # Brown vines
                "undergrowth_2": [(255, 69, 0), (255, 99, 71), (255, 127, 80)],  # Red-orange undergrowth
                "canopy_2": [(50, 205, 50), (60, 179, 113), (46, 139, 87)],  # Bright green canopy
                "midlevel_2": [(107, 142, 35), (128, 128, 0), (154, 205, 50)],  # Yellow-green mid-level
                "understory_2": [(210, 105, 30), (205, 133, 63), (139, 69, 19)],  # Brown understory
                "dark_base_2": [(0, 40, 0), (20, 40, 0), (40, 40, 0)],  # Very dark green-brown base for bioluminescent
                "glow_bright_2": [(255, 140, 0), (255, 165, 0), (255, 215, 0)],  # Bright orange-yellow glow
                "glow_medium_2": [(255, 99, 71), (255, 127, 80), (255, 140, 0)],  # Medium orange glow
                "glow_dim_2": [(178, 34, 34), (205, 92, 92), (240, 128, 128)],  # Dim red glow

                # Palette 3: Mystical Forest (blue-greens and purples)
                "base_3": [(0, 128, 128), (0, 139, 139), (32, 178, 170)],  # Teal base
                "highlight_3": [(127, 255, 212), (102, 205, 170), (64, 224, 208)],  # Aquamarine highlights
                "shadow_3": [(0, 64, 64), (0, 75, 75), (0, 86, 86)],  # Dark teal shadows
                "vine_3": [(138, 43, 226), (148, 0, 211), (153, 50, 204)],  # Purple vines
                "undergrowth_3": [(72, 209, 204), (64, 224, 208), (0, 206, 209)],  # Turquoise undergrowth
                "canopy_3": [(0, 139, 139), (32, 178, 170), (47, 79, 79)],  # Teal canopy
                "midlevel_3": [(70, 130, 180), (100, 149, 237), (30, 144, 255)],  # Steel blue mid-level
                "understory_3": [(106, 90, 205), (123, 104, 238), (147, 112, 219)],  # Purple understory
                "dark_base_3": [(0, 0, 50), (0, 0, 40), (0, 0, 30)],  # Very dark blue base for bioluminescent
                "glow_bright_3": [(0, 255, 255), (64, 224, 208), (127, 255, 212)],  # Bright cyan glow
                "glow_medium_3": [(0, 206, 209), (72, 209, 204), (32, 178, 170)],  # Medium turquoise glow
                "glow_dim_3": [(0, 139, 139), (0, 128, 128), (47, 79, 79)],  # Dim teal glow
            },

        }

        # Atmospheric color palettes
        self.atmosphere_palettes: Dict[str, List[RGBA]] = {
            "Desert": [(255, 200, 150, 60), (255, 220, 180, 40)],
            "Furnace": [(255, 100, 0, 80), (255, 150, 50, 60)],
            "Jovian": [
                # Atmósfera para paleta 1 (Jupiter-like)
                (255, 220, 180, 80), (255, 230, 190, 70), (240, 210, 170, 60),
                # Atmósfera para paleta 2 (Neptune-like)
                (180, 220, 255, 80), (190, 230, 255, 70), (170, 210, 240, 60),
                # Atmósfera para paleta 3 (Púrpura-violeta)
                (220, 180, 255, 80), (230, 190, 255, 70), (210, 170, 240, 60),
                # Atmósfera para paleta 4 (Verde-turquesa)
                (180, 255, 220, 80), (190, 255, 230, 70), (170, 240, 210, 60),
                # Atmósfera para paleta 5 (Rojo-naranja)
                (255, 180, 180, 80), (255, 190, 190, 70), (240, 170, 170, 60),
            ],
            "Ocean": [(150, 200, 255, 70), (180, 230, 255, 50)],
            "Vital": [
                # Atmosphere for palette 1 (Earth-like)
                (150, 200, 255, 60), (200, 230, 255, 40), (180, 220, 255, 50),
                # Atmosphere for palette 2 (Lush)
                (150, 255, 200, 60), (180, 255, 220, 50), (200, 255, 230, 40),
                # Atmosphere for palette 3 (Diverse)
                (200, 220, 255, 60), (220, 230, 255, 50), (180, 210, 255, 40),
            ],
            "Toxic": [
                # Atmosphere for palette 1 (Toxic Green)
                (0, 255, 0, 80), (50, 255, 50, 70), (100, 255, 100, 60),
                # Atmosphere for palette 2 (Acid Yellow)
                (255, 255, 0, 80), (255, 215, 0, 70), (173, 255, 47, 60),
                # Atmosphere for palette 3 (Corrosive Purple)
                (138, 43, 226, 80), (148, 0, 211, 70), (186, 85, 211, 60),
            ],
            "Ice": [
                # Atmosphere for palette 1 (Arctic Blue)
                (200, 230, 255, 70), (220, 240, 255, 60), (180, 220, 255, 50),
                # Atmosphere for palette 2 (Glacial Turquoise)
                (180, 255, 255, 70), (200, 255, 255, 60), (220, 255, 255, 50),
                # Atmosphere for palette 3 (Snow White)
                (230, 240, 255, 70), (235, 245, 255, 60), (240, 250, 255, 50),
            ],
            "Rocky": [
                # Atmosphere for palette 1 (Stone Gray)
                (180, 180, 180, 70), (200, 200, 200, 60), (220, 220, 220, 50),
                # Atmosphere for palette 2 (Rusty Red)
                (255, 180, 150, 70), (255, 200, 170, 60), (255, 220, 190, 50),
                # Atmosphere for palette 3 (Slate Blue)
                (180, 200, 230, 70), (200, 220, 240, 60), (220, 230, 250, 50),
            ],
            "Jungle": [
                # Atmosphere for palette 1 (Emerald Green)
                (150, 255, 150, 70), (180, 255, 180, 60), (210, 255, 210, 50),
                # Atmosphere for palette 2 (Tropical Jungle)
                (255, 200, 150, 70), (255, 220, 180, 60), (255, 240, 210, 50),
                # Atmosphere for palette 3 (Mystical Forest)
                (150, 220, 255, 70), (180, 230, 255, 60), (210, 240, 255, 50),
            ],
        }

        # Ring color palettes - Increased opacity for better visibility
        self.ring_palettes: Dict[str, List[RGBA]] = {
            "Desert": [(210, 180, 140, 200), (244, 164, 96, 180), (222, 184, 135, 160)],
            "Furnace": [(139, 0, 0, 200), (178, 34, 34, 180), (165, 42, 42, 160)],
            "Jovian": [
                # Anillos para paleta 1 (Jupiter-like)
                (233, 185, 110, 200), (210, 170, 109, 180), (240, 195, 130, 160), (220, 175, 100, 170),
                # Anillos para paleta 2 (Neptune-like)
                (100, 149, 237, 200), (70, 130, 180, 180), (30, 144, 255, 160), (65, 105, 225, 170),
                # Anillos para paleta 3 (Púrpura-violeta)
                (147, 112, 219, 200), (138, 43, 226, 180), (148, 0, 211, 160), (153, 50, 204, 170),
                # Anillos para paleta 4 (Verde-turquesa)
                (46, 139, 87, 200), (60, 179, 113, 180), (32, 178, 170, 160), (0, 128, 128, 170),
                # Anillos para paleta 5 (Rojo-naranja)
                (255, 99, 71, 200), (255, 127, 80, 180), (255, 140, 0, 160), (255, 69, 0, 170),
            ],
            "Ocean": [(0, 128, 128, 200), (0, 139, 139, 180), (32, 178, 170, 160)],
            "Vital": [(0, 128, 128, 200), (46, 139, 87, 180), (60, 179, 113, 160)],
            "Toxic": [
                # Rings for palette 1 (Toxic Green)
                (0, 255, 0, 200), (50, 255, 50, 180), (100, 255, 100, 160), (0, 250, 154, 170),
                # Rings for palette 2 (Acid Yellow)
                (255, 255, 0, 200), (255, 215, 0, 180), (173, 255, 47, 160), (154, 205, 50, 170),
                # Rings for palette 3 (Corrosive Purple)
                (138, 43, 226, 200), (148, 0, 211, 180), (186, 85, 211, 160), (0, 255, 255, 170),
            ],
            "Ice": [
                # Rings for palette 1 (Arctic Blue)
                (176, 224, 230, 200), (173, 216, 230, 180), (135, 206, 235, 160), (240, 248, 255, 170),
                # Rings for palette 2 (Glacial Turquoise)
                (175, 238, 238, 200), (64, 224, 208, 180), (72, 209, 204, 160), (240, 255, 255, 170),
                # Rings for palette 3 (Snow White)
                (245, 245, 255, 200), (235, 235, 255, 180), (225, 225, 245, 160), (255, 255, 255, 170),
            ],
            "Rocky": [
                # Rings for palette 1 (Stone Gray)
                (169, 169, 169, 200), (192, 192, 192, 180), (211, 211, 211, 160), (128, 128, 128, 170),
                # Rings for palette 2 (Rusty Red)
                (160, 82, 45, 200), (205, 133, 63, 180), (210, 105, 30, 160), (139, 69, 19, 170),
                # Rings for palette 3 (Slate Blue)
                (112, 128, 144, 200), (119, 136, 153, 180), (176, 196, 222, 160), (70, 130, 180, 170),
            ],
            "Jungle": [
                # Rings for palette 1 (Emerald Green)
                (34, 139, 34, 200), (46, 139, 87, 180), (60, 179, 113, 160), (0, 128, 0, 170),
                # Rings for palette 2 (Tropical Jungle)
                (107, 142, 35, 200), (154, 205, 50, 180), (173, 255, 47, 160), (128, 128, 0, 170),
                # Rings for palette 3 (Mystical Forest)
                (0, 139, 139, 200), (32, 178, 170, 180), (64, 224, 208, 160), (0, 206, 209, 170),
            ],
        }

        # Cloud color palettes - Customized for each planet type
        self.cloud_palettes: Dict[str, List[RGBA]] = {
            "Desert": [(255, 255, 255, 255)],      # Pure white for desert planets
            "Furnace": [
                # Incandescent clouds with reddish-orange glow
                (255, 180, 100, 255),  # Bright orange-yellow
                (255, 150, 50, 255),   # Deep orange
                (255, 120, 20, 255),   # Reddish-orange
                (255, 100, 0, 255)     # Fiery red-orange
            ],
            "Jovian": [
                # Stormy clouds that match the planet's color palette
                # Palette 1 (Jupiter-like)
                (255, 240, 200, 255),  # Cream-white for Jupiter-like
                (255, 230, 180, 255),  # Light tan for Jupiter-like
                # Palette 2 (Neptune-like)
                (220, 240, 255, 255),  # Light blue-white for Neptune-like
                (200, 220, 255, 255),  # Pale blue for Neptune-like
                # Palette 3 (Purple-violet)
                (240, 220, 255, 255),  # Pale lavender for Purple-violet
                (230, 200, 255, 255),  # Light purple for Purple-violet
                # Palette 4 (Green-turquoise)
                (220, 255, 240, 255),  # Pale mint for Green-turquoise
                (200, 255, 230, 255),  # Light turquoise for Green-turquoise
                # Palette 5 (Red-orange)
                (255, 220, 200, 255),  # Pale peach for Red-orange
                (255, 200, 180, 255)   # Light salmon for Red-orange
            ],
            "Ocean": [(255, 255, 255, 255)],      # Pure white for ocean planets
            "Vital": [(255, 255, 255, 255)],      # Pure white for vital planets
            "Toxic": [
                # Toxic-looking clouds with greenish and yellowish tints
                (220, 255, 220, 255),  # Pale toxic green
                (200, 255, 200, 255),  # Light toxic green
                (220, 255, 180, 255),  # Yellowish-green
                (180, 255, 180, 255),  # Medium toxic green
                (200, 255, 150, 255)   # Acid green-yellow
            ],
            "Ice": [(255, 255, 255, 255)],        # Pure white for ice planets
            "Rocky": [(255, 255, 255, 255)],      # Pure white for rocky planets
            "Jungle": [(255, 255, 255, 255)]      # Pure white for jungle planets
        }

    def get_random_color(self, planet_type: str, category: str = "base") -> Color:
        """
        Get a random color from a specific planet type and category.

        Args:
            planet_type: The type of planet (e.g., "Desert", "Ocean")
            category: The color category (e.g., "base", "highlight", "shadow")

        Returns:
            A random color from the specified palette
        """
        if planet_type not in self.planet_palettes:
            raise ValueError(f"Unknown planet type: {planet_type}")

        palette = self.planet_palettes[planet_type]
        if category not in palette:
            raise ValueError(f"Unknown color category '{category}' for planet type '{planet_type}'")

        return self.rng.choice(palette[category])

    def get_atmosphere_color(self, planet_type: str) -> RGBA:
        """
        Get a random atmospheric color for a specific planet type.

        Args:
            planet_type: The type of planet

        Returns:
            An RGBA color for the atmosphere
        """
        if planet_type not in self.atmosphere_palettes:
            raise ValueError(f"Unknown planet type: {planet_type}")

        return self.rng.choice(self.atmosphere_palettes[planet_type])

    def get_ring_color(self, planet_type: str) -> RGBA:
        """
        Get a random ring color for a specific planet type.

        Args:
            planet_type: The type of planet

        Returns:
            An RGBA color for the rings
        """
        if planet_type not in self.ring_palettes:
            raise ValueError(f"Unknown planet type: {planet_type}")

        return self.rng.choice(self.ring_palettes[planet_type])

    def get_cloud_color(self, planet_type: str) -> RGBA:
        """
        Get a random cloud color for a specific planet type.

        Args:
            planet_type: The type of planet

        Returns:
            An RGBA color for the clouds
        """
        if planet_type not in self.cloud_palettes:
            # Default to white clouds if planet type not found
            return (255, 255, 255, 180)

        return self.rng.choice(self.cloud_palettes[planet_type])

    def blend_colors(self, color1: Color, color2: Color, ratio: float = 0.5) -> Color:
        """
        Blend two colors together.

        Args:
            color1: First color
            color2: Second color
            ratio: Blend ratio (0.0 = all color1, 1.0 = all color2)

        Returns:
            Blended color
        """
        # Handle different color formats (RGB vs RGBA)
        if len(color1) == 3 and len(color2) == 3:
            # Both RGB
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            return (r, g, b)
        elif len(color1) == 4 and len(color2) == 4:
            # Both RGBA
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            a = int(color1[3] * (1 - ratio) + color2[3] * ratio)
            return (r, g, b, a)
        elif len(color1) == 3 and len(color2) == 4:
            # RGB and RGBA
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            a = int(255 * (1 - ratio) + color2[3] * ratio)
            return (r, g, b, a)
        elif len(color1) == 4 and len(color2) == 3:
            # RGBA and RGB
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            a = int(color1[3] * (1 - ratio) + 255 * ratio)
            return (r, g, b, a)
        else:
            raise ValueError("Invalid color formats")

    def adjust_brightness(self, color: Color, factor: float) -> Color:
        """
        Adjust the brightness of a color.

        Args:
            color: The color to adjust
            factor: Brightness factor (>1.0 brightens, <1.0 darkens)

        Returns:
            Adjusted color
        """
        if len(color) == 3:
            # RGB
            r = min(255, int(color[0] * factor))
            g = min(255, int(color[1] * factor))
            b = min(255, int(color[2] * factor))
            return (r, g, b)
        elif len(color) == 4:
            # RGBA
            r = min(255, int(color[0] * factor))
            g = min(255, int(color[1] * factor))
            b = min(255, int(color[2] * factor))
            return (r, g, b, color[3])
        else:
            raise ValueError("Invalid color format")
