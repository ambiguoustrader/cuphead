from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import arcade


ACTION_LABELS: dict[str, str] = {
    "move_up": "Вверх",
    "move_down": "Вниз",
    "move_left": "Влево",
    "move_right": "Вправо",
    "shoot": "Выстрел",
    "dash": "Рывок",
    "pause": "Пауза",
}

DEFAULT_BINDINGS: dict[str, list[int]] = {
    "move_up":    [arcade.key.UP],
    "move_down":  [arcade.key.DOWN],
    "move_left":  [arcade.key.LEFT],
    "move_right": [arcade.key.RIGHT],
    "shoot":      [arcade.key.SPACE],
    "dash":       [arcade.key.LSHIFT],
    "pause":      [arcade.key.ESCAPE],
}


def build_key_name_map() -> dict[int, str]:
    """code -> 'W'/'SPACE'/..."""
    out: dict[int, str] = {}
    for name in dir(arcade.key):
        if not name.isupper():
            continue
        val = getattr(arcade.key, name)
        if isinstance(val, int):
            # Если несколько имён на один код — оставим первое
            out.setdefault(val, name)
    return out


_KEY_NAME_BY_CODE = build_key_name_map()


def key_to_json_value(key_code: int) -> str | int:
    """Сохраняем человекочитаемо, если знаем имя; иначе числом."""
    return _KEY_NAME_BY_CODE.get(key_code, key_code)


def json_value_to_key(v: str | int) -> int | None:
    """Читаем из json: 'W' -> arcade.key.W или 32 -> 32."""
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        if v.isdigit():
            return int(v)
        if hasattr(arcade.key, v):
            attr = getattr(arcade.key, v)
            if isinstance(attr, int):
                return attr
    return None


@dataclass(slots=True)
class Controls:
    bindings: dict[str, list[int]]

    def is_action_down(self, action: str, pressed_keys: set[int]) -> bool:
        keys = self.bindings.get(action, [])
        return any(k in pressed_keys for k in keys)

    def set_primary(self, action: str, key_code: int, *, no_duplicates: bool = True) -> None:
        """Назначить основную кнопку для действия."""
        if action not in self.bindings:
            self.bindings[action] = []

        if no_duplicates:
            self._remove_key_from_all_actions(key_code)

        keys = self.bindings[action]
        if not keys:
            keys.append(key_code)
        else:
            keys[0] = key_code

    def add_secondary(self, action: str, key_code: int, *, no_duplicates: bool = True) -> None:
        """Добавить вторую кнопку (например, WASD + стрелки)."""
        if action not in self.bindings:
            self.bindings[action] = []

        if no_duplicates:
            self._remove_key_from_all_actions(key_code)

        keys = self.bindings[action]
        if key_code not in keys:
            keys.append(key_code)

    def clear_action(self, action: str) -> None:
        self.bindings[action] = []

    def _remove_key_from_all_actions(self, key_code: int) -> None:
        for a, keys in self.bindings.items():
            self.bindings[a] = [k for k in keys if k != key_code]


class ControlsStorage:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> Controls:
        if not self.path.exists():
            controls = Controls(bindings={k: v[:] for k, v in DEFAULT_BINDINGS.items()})
            self.save(controls)
            return controls

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # Если файл битый — откатываемся на дефолт
            controls = Controls(bindings={k: v[:] for k, v in DEFAULT_BINDINGS.items()})
            self.save(controls)
            return controls

        bindings: dict[str, list[int]] = {k: v[:] for k, v in DEFAULT_BINDINGS.items()}

        # Ожидаем формат: {"move_up": ["W","UP"], "shoot":["SPACE"], ...}
        if isinstance(raw, dict):
            for action, keys in raw.items():
                if not isinstance(action, str) or not isinstance(keys, list):
                    continue
                parsed: list[int] = []
                for item in keys:
                    key_code = json_value_to_key(item)
                    if isinstance(key_code, int):
                        parsed.append(key_code)
                if parsed:
                    bindings[action] = parsed

        return Controls(bindings=bindings)

    def save(self, controls: Controls) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, list[str | int]] = {}
        for action, keys in controls.bindings.items():
            data[action] = [key_to_json_value(k) for k in keys]
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
