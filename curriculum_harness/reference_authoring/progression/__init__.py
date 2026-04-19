"""Source-native progression-structure detection.

The reference-authoring pipeline does not impose any single school's
band/level/grade framework on its outputs. Each curriculum source is
read, its own native progression structure is detected (Welsh
Progression Steps, US Common Core grade levels, Scottish CfE Levels,
etc.), and downstream stages generate band statements and observation
indicators against THAT structure. Translation between native frameworks
is out of scope.
"""

from curriculum_harness.reference_authoring.progression.detect_progression import (
    PROGRESSION_DETECTION_VERSION,
    DETECTION_CONFIDENCE_LEVELS,
    ProgressionDetectionError,
    ProgressionStructure,
    band_label_slug,
    detect_progression,
    load_progression_structure,
)

__all__ = [
    "PROGRESSION_DETECTION_VERSION",
    "DETECTION_CONFIDENCE_LEVELS",
    "ProgressionDetectionError",
    "ProgressionStructure",
    "band_label_slug",
    "detect_progression",
    "load_progression_structure",
]
