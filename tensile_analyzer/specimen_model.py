"""
Specimen Model for Tensile Test Analyzer

Defines the geometry and material properties of a tensile test specimen.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class MaterialProperties:
    """Material properties for steel."""
    youngs_modulus: float = 200e3  # MPa (200 GPa)
    poisson_ratio: float = 0.3
    yield_strength: float = 400.0  # MPa
    ultimate_strength: float = 550.0  # MPa
    elongation_at_break: float = 0.25  # 25%
    hardening_exponent: float = 0.15  # n for power-law hardening


@dataclass
class GeometricProperties:
    """Geometric properties of the specimen."""
    gauge_length: float = 100.0  # mm
    gauge_diameter: float = 12.5  # mm
    grip_diameter: float = 20.0  # mm
    fillet_radius: float = 15.0  # mm
    grip_length: float = 50.0  # mm


class TensileSpecimen:
    """
    Represents a tensile test specimen with gauge section, transitions, and grips.
    """
    
    def __init__(self, geometry: GeometricProperties, material: MaterialProperties):
        self.geometry = geometry
        self.material = material
        
    @property
    def gauge_area(self) -> float:
        """Cross-sectional area of gauge section (mm²)."""
        return np.pi * (self.geometry.gauge_diameter / 2) ** 2
    
    @property
    def grip_area(self) -> float:
        """Cross-sectional area of grip section (mm²)."""
        return np.pi * (self.geometry.grip_diameter / 2) ** 2
    
    def stress_concentration_factor(self) -> float:
        """
        Calculate stress concentration factor at fillet using Peterson's approximation.
        
        K_t for shoulder fillet in tension.
        """
        r = self.geometry.fillet_radius
        d = self.geometry.gauge_diameter
        D = self.geometry.grip_diameter
        
        # Peterson's chart approximation for shoulder fillet
        # K_t ≈ 1 + (D/d - 1) / (1 + sqrt(r/d))
        if r > 0:
            ratio = D / d
            K_t = 1.0 + (ratio - 1.0) / (1.0 + np.sqrt(r / d))
        else:
            K_t = 3.0  # Sharp corner approximation
        
        return K_t
    
    def get_profile_coordinates(self, num_points: int = 200) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate x, y coordinates for the specimen profile (half-section).
        
        Returns:
            x: Axial position (mm)
            y: Radial position (mm, half-diameter)
        """
        total_length = 2 * self.geometry.grip_length + self.geometry.gauge_length
        
        # Define sections
        grip1_end = self.geometry.grip_length
        transition1_end = grip1_end + self.geometry.fillet_radius
        gauge_end = transition1_end + self.geometry.gauge_length
        transition2_end = gauge_end + self.geometry.fillet_radius
        
        x = np.linspace(0, total_length, num_points)
        y = np.zeros_like(x)
        
        r_grip = self.geometry.grip_diameter / 2
        r_gauge = self.geometry.gauge_diameter / 2
        r_fillet = self.geometry.fillet_radius
        
        for i, xi in enumerate(x):
            if xi < grip1_end:
                # Left grip
                y[i] = r_grip
            elif xi < transition1_end:
                # Left transition (fillet)
                t = (xi - grip1_end) / r_fillet
                y[i] = r_grip - (r_grip - r_gauge) * (1 - np.cos(t * np.pi / 2))
            elif xi < gauge_end:
                # Gauge section
                y[i] = r_gauge
            elif xi < transition2_end:
                # Right transition (fillet)
                t = (xi - gauge_end) / r_fillet
                y[i] = r_gauge + (r_grip - r_gauge) * (1 - np.cos(t * np.pi / 2))
            else:
                # Right grip
                y[i] = r_grip
        
        return x, y
    
    def calculate_stress(self, force: float) -> float:
        """
        Calculate engineering stress in gauge section.
        
        Args:
            force: Applied tensile force (N)
            
        Returns:
            Stress in MPa
        """
        return force / self.gauge_area
    
    def calculate_strain_elastic(self, stress: float) -> float:
        """
        Calculate elastic strain from stress.
        
        Args:
            stress: Engineering stress (MPa)
            
        Returns:
            Engineering strain (dimensionless)
        """
        return stress / self.material.youngs_modulus
    
    def calculate_strain_plastic(self, stress: float) -> float:
        """
        Calculate total strain (elastic + plastic) using Ramberg-Osgood model.
        
        Args:
            stress: Engineering stress (MPa)
            
        Returns:
            Total engineering strain (dimensionless)
        """
        E = self.material.youngs_modulus
        sigma_y = self.material.yield_strength
        n = self.material.hardening_exponent
        
        # Elastic component
        epsilon_elastic = stress / E
        
        # Plastic component (Ramberg-Osgood)
        if stress > sigma_y:
            K = sigma_y / (0.002 ** (1/n))  # Strength coefficient
            epsilon_plastic = (stress / K) ** (1/n) - (sigma_y / K) ** (1/n)
        else:
            epsilon_plastic = 0.0
        
        return epsilon_elastic + epsilon_plastic
    
    def calculate_lateral_strain(self, axial_strain: float) -> float:
        """
        Calculate lateral strain from axial strain using Poisson's ratio.
        
        Args:
            axial_strain: Axial engineering strain
            
        Returns:
            Lateral engineering strain (negative for contraction)
        """
        return -self.material.poisson_ratio * axial_strain
    
    def calculate_deformed_diameter(self, axial_strain: float) -> float:
        """
        Calculate deformed gauge diameter.
        
        Args:
            axial_strain: Axial engineering strain
            
        Returns:
            Deformed diameter (mm)
        """
        lateral_strain = self.calculate_lateral_strain(axial_strain)
        return self.geometry.gauge_diameter * (1 + lateral_strain)
