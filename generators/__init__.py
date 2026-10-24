from .base_generator import BaseGenerator
from .grid_hunter import GridHunterGenerator
from .optical_swirl import OpticalSwirlGenerator
from .pemdas_math import PemdasMathGenerator
from .rebus_puzzle import RebusPuzzleGenerator
from .word_guess import WordGuessGenerator
from .tangled_wires import TangledWiresGenerator
from .pause_silhouette import PauseSilhouetteGenerator
from .matchstick_puzzle import MatchstickPuzzleGenerator
from .shape_counter import ShapeCounterGenerator
from .shadow_glitch import ShadowGlitchGenerator
from .logic_lock import LogicLockGenerator

# Batch 1 Additions (Total: 20 Engines)
from .color_shade_clash import ColorShadeClashGenerator
from .balance_scale import BalanceScaleAlgebraGenerator
from .pyramid_math import PyramidNumberFlowGenerator
from .missing_domino import MissingDominoGenerator
from .pattern_matrix import PatternMatrixGenerator
from .gear_rotation import GearRotationGenerator
from .water_tank import WaterTankRaceGenerator
from .clock_angle import ClockAngleGenerator
from .triangle_trap import TriangleTrapGenerator

ALL_GENERATORS = {
    "grid_hunter": GridHunterGenerator,
    "logic_lock": LogicLockGenerator,
    "optical_swirl": OpticalSwirlGenerator,
    "pemdas_math": PemdasMathGenerator,
    "rebus_puzzle": RebusPuzzleGenerator,
    "word_guess": WordGuessGenerator,
    "tangled_wires": TangledWiresGenerator,
    "matchstick_puzzle": MatchstickPuzzleGenerator,
    "shape_counter": ShapeCounterGenerator,
    "shadow_glitch": ShadowGlitchGenerator,
    "pause_silhouette": PauseSilhouetteGenerator,
    "color_shade_clash": ColorShadeClashGenerator,
    "balance_scale": BalanceScaleAlgebraGenerator,
    "pyramid_math": PyramidNumberFlowGenerator,
    "missing_domino": MissingDominoGenerator,
    "pattern_matrix": PatternMatrixGenerator,
    "gear_rotation": GearRotationGenerator,
    "water_tank": WaterTankRaceGenerator,
    "clock_angle": ClockAngleGenerator,
    "triangle_trap": TriangleTrapGenerator
}
