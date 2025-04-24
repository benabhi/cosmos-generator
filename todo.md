- [ ] Hacer errores mas claros en la web.
- [ ] Guardar lindas imagenes (unas 10) y hacer que la imagen del dashboard del planeta varie cada cierto tiempo.
- [ ] Verificar.

```
Hay cierta duplicación en la funcionalidad de limpieza entre:
 web/routes.py
 web/utils.py
 cosmos_generator/subcommands/planet/clean.py

 Recomendación: Unificar la lógica de limpieza en un solo lugar
```

- [ ] Revisar estas ideas, estan geniales!!

1. Sistema de Atmósfera Mejorado

```python
class AdvancedAtmosphere:
    def __init__(self, planet_type, variation):
        self.planet_type = planet_type
        self.variation = variation

    def generate_atmosphere_glow(self, base_image, intensity=1.0):
        """Generate atmospheric glow effect."""
        # Diferentes tipos de brillo según el tipo de planeta
        glow_effects = {
            "Toxic": self._generate_toxic_glow,
            "Ice": self._generate_ice_glow,
            "Furnace": self._generate_heat_glow,
            "Jovian": self._generate_gas_glow
        }

        if self.planet_type in glow_effects:
            return glow_effects[self.planet_type](base_image, intensity)
        return base_image

    def _generate_toxic_glow(self, image, intensity):
        """Generate eerie toxic glow with particle effects."""
        # Implementar brillo verdoso/amarillento con partículas
        pass

    def _generate_ice_glow(self, image, intensity):
        """Generate crystalline ice refraction effects."""
        # Implementar efectos de refracción helada
        pass
```

2. Sistema de Detalles de Superficie

```python
class SurfaceDetailGenerator:
    def add_surface_features(self, planet_type, base_image):
        """Add detailed surface features based on planet type."""
        features = {
            "Rocky": [
                self._add_impact_craters,
                self._add_mountain_ranges,
                self._add_canyons
            ],
            "Ocean": [
                self._add_waves,
                self._add_underwater_features,
                self._add_coastal_details
            ],
            "Jungle": [
                self._add_canopy_variations,
                self._add_river_systems,
                self._add_seasonal_variations
            ],
            "Desert": [
                self._add_dune_patterns,
                self._add_wind_erosion,
                self._add_ancient_riverbeds
            ]
        }

        if planet_type in features:
            for feature_func in features[planet_type]:
                base_image = feature_func(base_image)

        return base_image
```

3. Sistema de Iluminación Dinámica

```python
class PlanetaryLighting:
    def apply_lighting_effects(self, planet_type, base_image):
        """Apply advanced lighting effects."""
        effects = {
            "Ice": self._apply_crystalline_reflections,
            "Toxic": self._apply_bioluminescence,
            "Furnace": self._apply_magma_glow,
            "Vital": self._apply_atmospheric_scattering
        }

        if planet_type in effects:
            return effects[planet_type](base_image)
        return self._apply_default_lighting(base_image)
```
4. Características Específicas por Tipo

* Para planetas rocosos:
    * Sistemas de grietas y fallas
    * Patrones de erosión
    * Variaciones de altura más pronunciadas
* Para planetas oceánicos:
    * Corrientes oceánicas visibles
    * Diferentes profundidades de agua
    * Efectos de reflexión del agua
* Para planetas tóxicos:
    * Efectos de partículas en la atmósfera
    * Patrones de corrosión
    * Lagos de sustancias tóxicas con brillos
* Para planetas vitales
    * Sistemas climáticos visibles
    * Variaciones estacionales
    * Patrones de vegetación realistas

5. Sistema de Anillos Mejorado

```python
class EnhancedRingSystem:
    def generate_rings(self, planet_type):
        """Generate detailed ring systems."""
        ring_types = {
            "Ice": self._generate_ice_rings,
            "Rocky": self._generate_rocky_rings,
            "Toxic": self._generate_toxic_rings,
            "Jovian": self._generate_complex_rings
        }

        if planet_type in ring_types:
            return ring_types[planet_type]()
        return self._generate_default_rings()

    def _generate_complex_rings(self):
        """Generate complex ring systems with multiple layers and gaps."""
        # Implementar anillos complejos tipo Saturno
        pass
```

6. Sistema de Post-Procesamiento

```python
class PostProcessor:
    def apply_effects(self, planet_image, planet_type):
        """Apply post-processing effects."""
        effects = [
            self._apply_bloom,
            self._apply_color_grading,
            self._apply_atmospheric_depth,
            self._apply_edge_enhancement,
            self._apply_final_adjustments
        ]

        for effect in effects:
            planet_image = effect(planet_image, planet_type)

        return planet_image
```

- [ ] Ver esto

```python
class PlanetPostProcessor:
    def __init__(self):
        self.effects_chain = {
            "base": [
                self._apply_contrast_enhancement,
                self._apply_sharpening,
                self._apply_color_balance
            ],
            "atmosphere": [
                self._apply_atmospheric_scatter,
                self._apply_atmospheric_depth,
                self._apply_atmospheric_glow
            ],
            "lighting": [
                self._apply_specular_highlights,
                self._apply_ambient_occlusion,
                self._apply_rim_lighting
            ],
            "detail": [
                self._apply_surface_detail_enhancement,
                self._apply_micro_detail,
                self._apply_noise_reduction
            ],
            "final": [
                self._apply_bloom,
                self._apply_color_grading,
                self._apply_vignette
            ]
        }

    def process_planet(self, image, planet_type, settings=None):
        """
        Aplica la cadena completa de post-procesamiento.

        Args:
            image: Imagen base del planeta
            planet_type: Tipo de planeta ("rocky", "gas", etc.)
            settings: Diccionario de configuraciones específicas
        """
        # Configuraciones específicas por tipo de planeta
        type_settings = {
            "toxic": {"bloom_intensity": 1.5, "color_saturation": 1.2},
            "ice": {"specular_intensity": 1.3, "clarity": 1.2},
            "furnace": {"glow_intensity": 1.4, "heat_distortion": 1.0},
            "jovian": {"band_enhancement": 1.2, "cloud_detail": 1.3},
            "vital": {"vegetation_enhancement": 1.1, "water_reflection": 1.2},
            "desert": {"surface_detail": 1.3, "heat_haze": 0.8},
            "ocean": {"water_caustics": 1.2, "wave_detail": 1.1}
        }

        # Aplicar efectos base
        for effect in self.effects_chain["base"]:
            image = effect(image, type_settings.get(planet_type, {}))

        # Aplicar efectos atmosféricos
        if self._has_atmosphere(planet_type):
            for effect in self.effects_chain["atmosphere"]:
                image = effect(image, type_settings.get(planet_type, {}))

        # Aplicar efectos de iluminación
        for effect in self.effects_chain["lighting"]:
            image = effect(image, type_settings.get(planet_type, {}))

        # Aplicar mejoras de detalle
        for effect in self.effects_chain["detail"]:
            image = effect(image, type_settings.get(planet_type, {}))

        # Aplicar efectos finales
        for effect in self.effects_chain["final"]:
            image = effect(image, type_settings.get(planet_type, {}))

        return image

    def _apply_atmospheric_scatter(self, image, settings):
        """
        Simula la dispersión atmosférica basada en el tipo de planeta.
        Añade profundidad y realismo a la atmósfera.
        """
        # Implementación específica
        pass

    def _apply_specular_highlights(self, image, settings):
        """
        Añade brillos especulares en superficies reflectantes.
        Especialmente importante para planetas helados y oceánicos.
        """
        # Implementación específica
        pass

    def _apply_surface_detail_enhancement(self, image, settings):
        """
        Mejora los detalles de la superficie manteniendo un aspecto natural.
        Utiliza técnicas de realce de bordes adaptativo.
        """
        # Implementación específica
        pass

    def _apply_color_grading(self, image, settings):
        """
        Aplica corrección de color y ajustes tonales.
        Incluye curvas de color específicas por tipo de planeta.
        """
        # Implementación específica
        pass

    def _apply_bloom(self, image, settings):
        """
        Añade efecto de resplandor a áreas brillantes.
        Especialmente útil para planetas tóxicos y furnace.
        """
        # Implementación específica
        pass

    def _apply_atmospheric_depth(self, image, settings):
        """
        Simula la profundidad atmosférica y efectos de dispersión.
        Crea transiciones suaves en los bordes del planeta.
        """
        # Implementación específica
        pass

    def _apply_rim_lighting(self, image, settings):
        """
        Añade iluminación en los bordes para dar profundidad.
        Simula la dispersión de luz en la atmósfera.
        """
        # Implementación específica
        pass

    def _apply_micro_detail(self, image, settings):
        """
        Añade detalles finos y textura a nivel micro.
        Mantiene el realismo sin sobre-procesar.
        """
        # Implementación específica
        pass

    def _apply_ambient_occlusion(self, image, settings):
        """
        Simula sombras suaves en detalles de la superficie.
        Mejora la percepción de profundidad.
        """
        # Implementación específica
        pass

    def _apply_vignette(self, image, settings):
        """
        Añade un sutil viñeteado para dirigir la atención.
        Personalizado según el tipo de planeta.
        """
        # Implementación específica
        pass

    @staticmethod
    def _has_atmosphere(planet_type):
        """
        Determina si un tipo de planeta debe tener efectos atmosféricos.
        """
        return planet_type not in ["rocky", "asteroid"]
```