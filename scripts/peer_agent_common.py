#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ACTIONS = {"review", "patch", "edit"}
DEBATE_ACTIONS = {"debate", "judge"}
ALL_ACTIONS = ACTIONS | DEBATE_ACTIONS
INLINE_LIMIT = 120_000
ARTIFACT_DIRS = {
    "review": "reviews",
    "patch": "patches",
    "edit": "edits",
    "debate": "debates",
    "judge": "debates",
}
ARTIFACT_EXTS = {
    "review": ".md",
    "patch": ".patch",
    "edit": ".md",
    "debate": ".md",
    "judge": ".md",
}


@dataclass(frozen=True)
class TargetSnapshot:
    launch_id: str
    launched_at_utc: str
    target_path: str
    target_sha256: str
    target_size_bytes: int
    target_mtime_ns: int
    target_mtime_utc: str
    content_truncated: bool
    inlined_byte_count: int
    content_note: str
    content_start_marker: str
    content_end_marker: str
    target_content: str


def base_dir() -> Path:
    return resource_dir()


def resource_dir() -> Path:
    return Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    override = os.environ.get("PEER_AGENT_HOME")
    if override:
        root = Path(override).expanduser()
    else:
        root = Path.home() / ".local" / "share" / "peer-agent"
    root.mkdir(parents=True, exist_ok=True)
    return root


def parse_args(agent: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=f"ask-{agent}",
        description=f"Invoke {agent} from another coding-agent session.",
    )
    parser.add_argument("action", choices=sorted(ACTIONS))
    parser.add_argument("target", help="Target file or plan path.")
    parser.add_argument(
        "instruction",
        nargs="*",
        help="Optional free-form instruction appended to the action.",
    )
    parser.add_argument(
        "--cwd",
        default=None,
        help="Working directory context to pass to the peer agent.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not persist an artifact copy under ~/.local/share/peer-agent/artifacts/.",
    )
    return parser.parse_args()


def resolve_target(target: str, cwd: Path) -> Path:
    path = Path(target).expanduser()
    if not path.is_absolute():
        path = (cwd / path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Target does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Target is not a file: {path}")
    return path


def load_template(action: str) -> str:
    template_path = resource_dir() / "prompts" / f"{action}.md"
    return template_path.read_text(encoding="utf-8")


def _format_slug(dt: datetime) -> str:
    return dt.strftime("%Y%m%d-%H%M%S-%fZ")


def _format_utc(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_from_epoch_ns(epoch_ns: int) -> str:
    return _format_utc(datetime.fromtimestamp(epoch_ns / 1_000_000_000, timezone.utc))


def _build_content_markers(
    content: str,
    *,
    launch_id: str,
    digest: str,
) -> tuple[str, str]:
    base = f"PEER_AGENT_TARGET_CONTENT_{launch_id}_{digest[:12]}"
    suffix = 0
    while True:
        counter = "" if suffix == 0 else f"_{suffix}"
        start = f"<<<<{base}_START{counter}>>>>"
        end = f"<<<<{base}_END{counter}>>>>"
        if start not in content and end not in content:
            return start, end
        suffix += 1


def capture_target_snapshot(target: Path) -> TargetSnapshot:
    launched_at = datetime.now(timezone.utc)
    launch_id = _format_slug(launched_at)
    stat = target.stat()
    raw = target.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()

    if len(raw) <= INLINE_LIMIT:
        content = raw.decode("utf-8", errors="replace")
        note = "Full target content is inlined below."
        truncated = False
        inlined_byte_count = len(raw)
    else:
        content = raw[:INLINE_LIMIT].decode("utf-8", errors="ignore")
        note = (
            "Target content was truncated before inlining because the file is large. "
            f"Use the target path for the full file if you need more context."
        )
        truncated = True
        inlined_byte_count = len(content.encode("utf-8"))

    content_start_marker, content_end_marker = _build_content_markers(
        content,
        launch_id=launch_id,
        digest=digest,
    )

    return TargetSnapshot(
        launch_id=launch_id,
        launched_at_utc=_format_utc(launched_at),
        target_path=str(target),
        target_sha256=digest,
        target_size_bytes=len(raw),
        target_mtime_ns=stat.st_mtime_ns,
        target_mtime_utc=_utc_from_epoch_ns(stat.st_mtime_ns),
        content_truncated=truncated,
        inlined_byte_count=inlined_byte_count,
        content_note=note,
        content_start_marker=content_start_marker,
        content_end_marker=content_end_marker,
        target_content=content,
    )


def render_prompt(
    action: str,
    caller: str,
    cwd: Path,
    target: Path,
    instruction: str,
    snapshot: TargetSnapshot,
    *,
    extra_replacements: dict[str, str] | None = None,
) -> str:
    template = load_template(action)
    replacements = {
        "{{CALLER}}": caller,
        "{{CWD}}": str(cwd),
        "{{TARGET}}": str(target),
        "{{INSTRUCTION}}": instruction or "(none provided)",
        "{{CONTENT_NOTE}}": snapshot.content_note,
        "{{TARGET_CONTENT_START}}": snapshot.content_start_marker,
        "{{TARGET_CONTENT_END}}": snapshot.content_end_marker,
        "{{TARGET_CONTENT}}": snapshot.target_content,
    }
    if extra_replacements:
        replacements.update(extra_replacements)

    rendered = template
    for marker, value in replacements.items():
        rendered = rendered.replace(marker, value)
    return rendered


def artifact_metadata(
    *,
    peer: str,
    action: str,
    target: Path,
    snapshot: TargetSnapshot,
    requested_cwd: Path,
    exec_cwd: Path,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "peer": peer,
        "action": action,
        "target_path": str(target),
        "requested_cwd": str(requested_cwd),
        "exec_cwd": str(exec_cwd),
        "launch_id": snapshot.launch_id,
        "launched_at_utc": snapshot.launched_at_utc,
        "saved_at_utc": _format_utc(datetime.now(timezone.utc)),
        "target_snapshot": {
            "path": snapshot.target_path,
            "sha256": snapshot.target_sha256,
            "size_bytes": snapshot.target_size_bytes,
            "mtime_ns": snapshot.target_mtime_ns,
            "mtime_utc": snapshot.target_mtime_utc,
            "content_truncated": snapshot.content_truncated,
            "inlined_byte_count": snapshot.inlined_byte_count,
        },
    }


def artifact_path(action: str, peer: str, target: Path, snapshot: TargetSnapshot) -> Path:
    safe_name = target.name.replace("/", "_")
    directory = data_dir() / "artifacts" / ARTIFACT_DIRS[action]
    directory.mkdir(parents=True, exist_ok=True)
    return directory / (
        f"{snapshot.launch_id}-{peer}-{safe_name}-sha{snapshot.target_sha256[:12]}"
        f"{ARTIFACT_EXTS[action]}"
    )


def log_path(peer: str, action: str, target: Path, snapshot: TargetSnapshot) -> Path:
    safe_name = target.name.replace("/", "_")
    directory = data_dir() / "artifacts" / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / (
        f"{snapshot.launch_id}-{peer}-{action}-{safe_name}-sha{snapshot.target_sha256[:12]}.log"
    )


def choose_exec_cwd(action: str, requested_cwd: Path, target: Path) -> Path:
    try:
        target.relative_to(requested_cwd)
        return requested_cwd
    except ValueError:
        if action == "edit":
            return target.parent
        return requested_cwd


def write_artifact(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def metadata_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.meta.json")


def write_artifact_metadata(path: Path, metadata: dict[str, object]) -> None:
    metadata_path(path).write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def fail_with_log(
    *,
    peer: str,
    action: str,
    target: Path,
    snapshot: TargetSnapshot,
    requested_cwd: Path,
    exec_cwd: Path,
    command: list[str],
    stdout: str,
    stderr: str,
    returncode: int,
) -> int:
    log = [
        f"command: {' '.join(command)}",
        f"returncode: {returncode}",
        "",
        "stdout:",
        stdout,
        "",
        "stderr:",
        stderr,
    ]
    path = log_path(peer, action, target, snapshot)
    write_artifact(path, "\n".join(log))
    write_artifact_metadata(
        path,
        {
            **artifact_metadata(
                peer=peer,
                action=action,
                target=target,
                snapshot=snapshot,
                requested_cwd=requested_cwd,
                exec_cwd=exec_cwd,
            ),
            "returncode": returncode,
        },
    )
    sys.stderr.write(stderr or stdout or f"{peer} invocation failed\n")
    sys.stderr.write(f"\nFailure log saved to {path}\n")
    return returncode


def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return run_with_input(command, cwd=cwd, stdin_text=None)


def run_with_input(
    command: list[str],
    *,
    cwd: Path,
    stdin_text: str | None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        input=stdin_text,
        check=False,
    )
