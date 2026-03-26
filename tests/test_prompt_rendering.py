from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from peer_agent_common import (
    _build_content_markers,
    capture_target_snapshot,
    load_template,
    render_prompt,
)


class PromptTemplateTests(unittest.TestCase):
    def test_templates_use_explicit_content_markers(self) -> None:
        for action in ("review", "patch", "edit", "debate", "judge"):
            with self.subTest(action=action):
                template = load_template(action)
                self.assertIn("{{TARGET_CONTENT_START}}", template)
                self.assertIn("{{TARGET_CONTENT_END}}", template)
                self.assertNotIn("```text", template)

    def test_rendered_prompt_uses_marker_lines_for_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = Path(tmpdir)
            target = cwd / "sample.md"
            target.write_text(
                "# Sample\n\n```text\nliteral backticks inside the file stay literal\n```\n",
                encoding="utf-8",
            )
            snapshot = capture_target_snapshot(target)
            prompt = render_prompt("review", "claude", cwd, target, "check correctness", snapshot)

        self.assertIn(snapshot.content_start_marker, prompt)
        self.assertIn(snapshot.content_end_marker, prompt)
        self.assertIn(snapshot.target_content, prompt)
        self.assertIn(
            "Only the text between the marker lines below is target content.",
            prompt,
        )
        self.assertNotIn("```text\n{{TARGET_CONTENT}}\n```", prompt)
        self.assertNotIn(snapshot.content_start_marker, snapshot.target_content)
        self.assertNotIn(snapshot.content_end_marker, snapshot.target_content)

    def test_content_markers_avoid_collisions_with_inlined_content(self) -> None:
        launch_id = "20260324-131500-000000Z"
        digest = "0123456789abcdef" * 4
        conflicting_start = (
            f"<<<<PEER_AGENT_TARGET_CONTENT_{launch_id}_{digest[:12]}_START>>>>"
        )
        conflicting_end = f"<<<<PEER_AGENT_TARGET_CONTENT_{launch_id}_{digest[:12]}_END>>>>"
        content = f"{conflicting_start}\n{conflicting_end}\n"

        start, end = _build_content_markers(content, launch_id=launch_id, digest=digest)

        self.assertNotEqual(start, conflicting_start)
        self.assertNotEqual(end, conflicting_end)
        self.assertNotIn(start, content)
        self.assertNotIn(end, content)


if __name__ == "__main__":
    unittest.main()
