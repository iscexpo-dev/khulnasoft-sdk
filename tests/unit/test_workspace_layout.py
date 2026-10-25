from __future__ import annotations

from typing import Any

from scripts import workspace

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]


def _pyproject(package: workspace.Package) -> dict[str, Any]:
    return tomllib.loads((package.path / "pyproject.toml").read_text(encoding="utf-8"))


def _target_paths(path: str, sources: dict[str, Any]) -> list[str]:
    path = path.strip("/")
    for source, targets in sorted(sources.items(), key=lambda item: len(item[0]), reverse=True):
        prefix = source.strip("/")
        if prefix and path != prefix and not path.startswith(prefix + "/"):
            continue
        rest = path[len(prefix) :].lstrip("/") if prefix else path
        values = targets if isinstance(targets, list) else [targets]
        return [
            "/".join(part for part in (str(target).strip("/"), rest) if part) for target in values
        ]
    return [path]


def _wheel_paths(package: workspace.Package) -> list[str]:
    wheel = _pyproject(package)["tool"]["hatch"]["build"]["targets"]["wheel"]
    only_include = wheel.get("only-include", [])
    if isinstance(only_include, str):
        only_include = [only_include]
    sources = wheel.get("sources", {})
    paths = []
    for entry in only_include:
        for path in _target_paths(entry, sources):
            if path == "khulnasoft" or path.startswith("khulnasoft/"):
                paths.append(path)
    return paths


def _overlaps(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def test_wheel_include_paths_do_not_overlap() -> None:
    claims: dict[str, str] = {}
    for name, package in workspace.packages().items():
        paths = _wheel_paths(package)
        assert paths, f"{name} must declare wheel only-include paths under khulnasoft/"
        for path in paths:
            for other_path, other_name in claims.items():
                assert not _overlaps(path, other_path), (
                    f"{name} claims {path}, which overlaps {other_name}'s {other_path}"
                )
            claims[path] = name


def test_live_marker_packages_exclude_live_tests_by_default() -> None:
    checked = []
    for name, package in workspace.packages().items():
        options = _pyproject(package).get("tool", {}).get("pytest", {}).get("ini_options", {})
        markers = options.get("markers", [])
        if isinstance(markers, str):
            markers = [markers]
        defines_live = any(str(marker).split(":", 1)[0].strip() == "live" for marker in markers)
        has_live_tests = (package.path / "tests" / "live").is_dir()
        if not (defines_live or has_live_tests):
            continue
        assert defines_live, f"{name} has tests/live but does not define a live marker"
        addopts = options.get("addopts", "")
        assert "-m 'not live'" in addopts or '-m "not live"' in addopts, (
            f"{name} defines a live marker but does not exclude live tests by default"
        )
        checked.append(name)
    assert checked
