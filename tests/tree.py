"""Reads the pieces of the source tree the overlays and flag values refer to."""

import functools
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOP = Path(os.environ.get("ANDROID_BUILD_TOP", REPO.parent.parent.parent))

# Resource directories of each package an overlay of this repo targets.
TARGET_RES_DIRS = {
    "android": ["frameworks/base/core/res/res"],
    "com.android.systemui": [
        "frameworks/base/packages/SystemUI/res",
        "frameworks/base/packages/SystemUI/res-keyguard",
        "frameworks/base/packages/SystemUI/res-product",
        "frameworks/base/libs/WindowManager/Shell/res",
        "frameworks/base/libs/WindowManager/Shell/shared/res",
        "frameworks/base/packages/SettingsLib/res",
    ],
    "com.android.launcher3": [
        "packages/apps/Launcher3/res",
        "packages/apps/Launcher3/quickstep/res",
    ],
    "com.android.providers.settings": ["frameworks/base/packages/SettingsProvider/res"],
}

VALUE_TAGS = {"bool", "integer", "dimen", "color", "string", "fraction", "array",
              "string-array", "integer-array", "item"}


def has_tree():
    return (TOP / "frameworks/base/core/res/res/values/config.xml").is_file()


def find_overlays():
    """Every runtime_resource_overlay of the repo: its directory and target package."""
    overlays = []
    for manifest in sorted((REPO / "overlay").glob("*/AndroidManifest.xml")):
        root = ET.parse(manifest).getroot()
        tag = root.find("overlay")
        target = tag.get("{http://schemas.android.com/apk/res/android}targetPackage")
        overlays.append((manifest.parent, target))
    return overlays


def read_overlay_values(overlay_dir):
    """(type, name, value text, values dir name) of every value resource in the overlay."""
    found = []
    for xml in sorted(overlay_dir.glob("res/values*/*.xml")):
        for element in ET.parse(xml).getroot():
            kind = element.tag if element.tag != "item" else element.get("type")
            kind = "array" if kind in ("string-array", "integer-array") else kind
            found.append((kind, element.get("name"), (element.text or "").strip(), xml.parent.name))
    return found


def read_overlay_files(overlay_dir):
    """(type, name) of every file resource (color/, drawable/, layout/) of the overlay."""
    found = []
    for res_file in sorted(overlay_dir.glob("res/*/*.xml")):
        kind = res_file.parent.name.split("-")[0]
        if kind == "values":
            continue
        found.append((kind, res_file.stem))
    return found


@functools.lru_cache(maxsize=None)
def find_declared_resources(target):
    """Set of (type, name) the target package declares, from its source resource dirs."""
    declared = set()
    for res_dir in TARGET_RES_DIRS[target]:
        base = TOP / res_dir
        for xml in base.glob("values*/*.xml"):
            declared |= _read_value_names(xml)
        for res_file in base.glob("*/*"):
            kind = res_file.parent.name.split("-")[0]
            if kind != "values":
                declared.add((kind, res_file.name.split(".")[0]))
        declared |= _read_pc_branch_value_names(base)
    return frozenset(declared)


_PC_VALUE_RE = re.compile(r'<(bool|integer|dimen|color|string|fraction)\s+name="([^"]+)"')


def _read_pc_branch_value_names(base):
    """Value names the project's `pc` branch declares under base, before it is checked out."""
    git = ["git", "-C", str(base)]
    found = subprocess.run(git + ["rev-parse", "--verify", "--quiet", "pc"],
                           capture_output=True)
    if found.returncode != 0:
        return set()
    listing = subprocess.run(git + ["grep", "-h", "-E", _PC_VALUE_RE.pattern, "pc", "--", "."],
                             capture_output=True, text=True)
    return set(_PC_VALUE_RE.findall(listing.stdout))


def _read_value_names(xml):
    names = set()
    try:
        root = ET.parse(xml).getroot()
    except ET.ParseError:
        return names
    for element in root:
        if element.tag not in VALUE_TAGS:
            continue
        kind = element.get("type") if element.tag == "item" else element.tag
        kind = "array" if kind in ("string-array", "integer-array") else kind
        names.add((kind, element.get("name")))
    return names


_FLAG_RE = re.compile(r'flag\s*\{[^{}]*?name:\s*"([^"]+)"', re.S)
_PACKAGE_RE = re.compile(r'^package:\s*"([^"]+)"', re.M)

# Where the aconfig declarations of the packages this repo sets live.
DECLARATION_DIRS = [
    "frameworks/base/core/java/android/window/flags",
    "frameworks/base/libs/WindowManager/Shell/aconfig",
    "frameworks/base/packages/SystemUI/aconfig",
    "packages/apps/Launcher3/aconfig",
    "frameworks/base/core/java/android/companion",
    "frameworks/base/core/java/android/content/pm",
]


@functools.lru_cache(maxsize=None)
def find_declared_flags():
    """Set of fully qualified aconfig flag names declared in DECLARATION_DIRS."""
    declared = set()
    for directory in DECLARATION_DIRS:
        for aconfig in (TOP / directory).glob("*.aconfig"):
            text = aconfig.read_text()
            package = _PACKAGE_RE.search(text)
            if not package:
                continue
            declared |= {f"{package.group(1)}.{name}" for name in _FLAG_RE.findall(text)}
    return frozenset(declared)


_VALUE_RE = re.compile(
    r'flag_value\s*\{\s*package:\s*"([^"]+)"\s*name:\s*"([^"]+)"\s*state:\s*(\w+)\s*'
    r'permission:\s*(\w+)\s*\}')


def read_flag_values():
    """(file, package, name, state, permission) of every flag value file of the repo."""
    values = []
    for textproto in sorted((REPO / "flags").rglob("*_flag_values.textproto")):
        for package, name, state, permission in _VALUE_RE.findall(textproto.read_text()):
            values.append((textproto, package, name, state, permission))
    return values


PRODUCT_MAKEFILES = ("pc_ui.mk", "pc_login.mk")


def read_product_packages(makefile=None):
    """Module names a product makefile of the repo (all of them by default) adds to PRODUCT_PACKAGES."""
    paths = [makefile] if makefile else [REPO / name for name in PRODUCT_MAKEFILES]
    text = "\n".join(path.read_text() for path in paths).replace("\\\n", " ")
    modules = set()
    for line in text.splitlines():
        if line.strip().startswith("PRODUCT_PACKAGES"):
            modules |= set(line.split("+=", 1)[1].split())
    return modules


_MODULE_RE = re.compile(r'runtime_resource_overlay\s*\{\s*name:\s*"([^"]+)"')


def read_overlay_module(overlay_dir):
    match = _MODULE_RE.search((overlay_dir / "Android.bp").read_text())
    return match.group(1) if match else None
