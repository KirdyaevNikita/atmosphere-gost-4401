"""
Расчёт параметров стандартной атмосферы по ГОСТ 4401-81.
"""

import math

__author__ = "KirdyaevNikita"
__version__ = "0.1.0"


# Физические константы
_EARTH_RADIUS = 6356767    # Радиус Земли, м
_G0 = 9.80665              # Ускорение свободного падения, м/с²
_R_AIR = 287.05287         # Удельная газовая постоянная воздуха, Дж/(кг·К)
_K_AIR = 1.4               # Показатель адиабаты воздуха

# Геопотенциальные высоты, на которых меняется температурный градиент, м
_LAYER_HEIGHTS = [
    -2000,
    0,
    11000,
    20000,
    32000,
    47000,
    51000,
    71000,
    85000,
]

# Температуры на нижних границах слоёв, К
_LAYER_TEMPERATURES = [
    301.15,
    288.15,
    216.65,
    216.65,
    228.65,
    270.65,
    270.65,
    214.65,
    186.65,
]

# Градиенты температуры по геопотенциальной высоте, К/м
_TEMPERATURE_GRADIENTS = [
    -0.0065,
    -0.0065,
    0.0000,
    0.0010,
    0.0028,
    0.0000,
    -0.0028,
    -0.0020,
]

# Давления на нижних границах слоёв, Па
_LAYER_PRESSURES = [
    127774.0,
    101325.0,
    22632.0,
    5474.87,
    868.014,
    115.851,
    66.9384,
    3.95639,
    0.44571,
]


def _validate_height(h: float) -> None:
    """Проверяет допустимый диапазон геометрической высоты"""

    if not -2000 <= h <= 85000:
        raise ValueError(
            "Высота должна находиться в диапазоне от -2000 до 85000 м."
        )


def _geopotential_height(h: float) -> float:
    """Преобразует геометрическую высоту в геопотенциальную"""

    return _EARTH_RADIUS * h / (_EARTH_RADIUS + h)


def _find_layer(H: float) -> int:
    """Определяет индекс температурного слоя по геопотенциальной высоте"""

    if H < _LAYER_HEIGHTS[0]:
        return 0

    for i in range(len(_LAYER_HEIGHTS) - 1):
        if _LAYER_HEIGHTS[i] <= H < _LAYER_HEIGHTS[i + 1]:
            return i

    if H == _LAYER_HEIGHTS[-1]:
        return len(_LAYER_HEIGHTS) - 2

    raise ValueError("Не удалось определить температурный слой.")


def _temperature(H: float) -> float:
    """Вычисляет температуру атмосферы по геопотенциальной высоте"""

    i = _find_layer(H)

    return (_LAYER_TEMPERATURES[i] + _TEMPERATURE_GRADIENTS[i] * (H - _LAYER_HEIGHTS[i]))


def _pressure(H: float) -> float:
    """Вычисляет давление атмосферы по геопотенциальной высоте"""

    i = _find_layer(H)

    T_i = _LAYER_TEMPERATURES[i]
    p_i = _LAYER_PRESSURES[i]
    beta_i = _TEMPERATURE_GRADIENTS[i]
    H_i = _LAYER_HEIGHTS[i]

    if beta_i != 0:
        return p_i / (1 + beta_i / T_i * (H - H_i)) ** (_G0 / (beta_i * _R_AIR))

    return p_i * math.exp(-_G0 * (H - H_i) / (_R_AIR * T_i))


def _density(p: float, T: float) -> float:
    """Вычисляет плотность воздуха по уравнению состояния идеального газа"""

    return p / (_R_AIR * T)


def _speed_of_sound(T: float) -> float:
    """Вычисляет скорость звука в атмосфере"""

    return math.sqrt(_K_AIR * _R_AIR * T)


def atmosphere_geometrical(h: float) -> tuple[float, float, float, float, float]:
    """Рассчитывает параметры стандартной атмосферы по геометрической высоте"""

    _validate_height(h)

    H = _geopotential_height(h)

    g = _G0 * (_EARTH_RADIUS / (_EARTH_RADIUS + h)) ** 2
    T = _temperature(H)
    p = _pressure(H)
    rho = _density(p, T)
    a = _speed_of_sound(T)

    return g, T, p, rho, a