"""Test bootstrap that avoids importing Home Assistant itself."""

import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]

custom_components = ModuleType("custom_components")
custom_components.__path__ = [str(ROOT / "custom_components")]
sys.modules.setdefault("custom_components", custom_components)

guangzhou_gas = ModuleType("custom_components.guangzhou_gas")
guangzhou_gas.__path__ = [str(ROOT / "custom_components" / "guangzhou_gas")]
sys.modules.setdefault("custom_components.guangzhou_gas", guangzhou_gas)
