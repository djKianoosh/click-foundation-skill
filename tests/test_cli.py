import json
import subprocess
import sys
from pathlib import Path


def run_cli(*args, cwd=None):
    script = (
        Path(__file__).parent.parent / "skills" / "click-foundation" / "scripts" / "click_coach.py"
    )
    cmd = [sys.executable, str(script), *args]
    return subprocess.run(cmd, check=False, cwd=cwd, capture_output=True, text=True)


class TestCliEndToEnd:
    def test_full_sprint_lifecycle(self, tmp_path):
        # 1. init
        res = run_cli("init", "--name", "Acme Health", cwd=tmp_path)
        assert res.returncode == 0
        assert "Initialized Click project" in res.stdout
        assert (tmp_path / ".click" / "click.db").exists()

        # 2. save basics
        res = run_cli(
            "foundation",
            "save-basics",
            "--customer",
            "Nurses in ER",
            "--problem",
            "Chart handoff delays",
            "--capability",
            "Voice transcription",
            "--insight",
            "Noise canceling mic",
            "--motivation",
            "Patient safety",
            "--gorilla",
            "Epic EHR",
            "--alternatives",
            "Sticky notes, verbal handoff",
            cwd=tmp_path,
        )
        assert res.returncode == 0
        assert "Basics saved" in res.stdout

        # 3. save differentiation
        res = run_cli(
            "foundation",
            "save-differentiation",
            "--diff1",
            "Hands-free voice",
            "--diff2",
            "Instant sync",
            "--axes-x-low",
            "Slow",
            "--axes-x-high",
            "Fast",
            "--axes-y-low",
            "Screen-based",
            "--axes-y-high",
            "Hands-free",
            "--principles",
            "Voice first, Zero extra taps, Patient privacy safeguard",
            cwd=tmp_path,
        )
        assert res.returncode == 0
        assert "Differentiation saved" in res.stdout

        # 4. save approach
        res = run_cli(
            "foundation",
            "save-approach",
            "--title",
            "Lanyard Wearable",
            "--summary",
            "Clip-on audio badge",
            "--how-it-works",
            "Transcribes handoff notes via button press",
            "--top-bet",
            cwd=tmp_path,
        )
        assert res.returncode == 0
        assert "saved" in res.stdout

        # 5. save hypothesis
        res = run_cli(
            "foundation",
            "save-hypothesis",
            "--customer",
            "ER nurses",
            "--problem",
            "handoff delays",
            "--approach",
            "clip-on voice badges",
            "--competitors",
            "Epic typing",
            "--differentiation",
            "hands-free 30-second handoffs",
            cwd=tmp_path,
        )
        assert res.returncode == 0
        assert "Founding Hypothesis saved" in res.stdout

        # 6. scorecard update
        res = run_cli(
            "scorecard",
            "update",
            "--right-customer",
            "yes",
            "--right-problem",
            "yes",
            "--right-approach",
            "maybe",
            "--will-they-switch",
            "maybe",
            "--right-differentiation",
            "yes",
            "--does-it-click",
            "not_yet",
            "--notes",
            "Need to test in noisy ward",
            cwd=tmp_path,
        )
        assert res.returncode == 0
        assert "Scorecard saved" in res.stdout

        # 7. status
        res = run_cli("status", cwd=tmp_path)
        assert res.returncode == 0
        assert "Project: Acme Health" in res.stdout
        assert "Founding Hypothesis: v1" in res.stdout

        # 8. export-docs
        res = run_cli("export-docs", cwd=tmp_path)
        assert res.returncode == 0
        out_dir = tmp_path / "click-output"
        assert (out_dir / "founding-hypothesis.md").exists()
        assert (out_dir / "scorecard.md").exists()

        # 9. learnings record & show
        res = run_cli(
            "learnings",
            "record",
            "--source-type",
            "foundation_sprint",
            "--insight",
            "Nurses love the concept but worry about battery life",
            "--lesson-number",
            "2",
            cwd=tmp_path,
        )
        assert res.returncode == 0
        res = run_cli("learnings", "show", cwd=tmp_path)
        assert res.returncode == 0
        assert "battery life" in res.stdout

        # 10. design sprint workflow
        res = run_cli(
            "sprint",
            "new",
            "--risk-question",
            "Can speech-to-text handle medical acronyms accurately?",
            cwd=tmp_path,
        )
        assert res.returncode == 0
        assert "Testing:" in res.stdout

        res = run_cli(
            "sprint",
            "log",
            "--sprint-id",
            "1",
            "--day",
            "prototype",
            "--notes",
            "Mock badge with Whisper",
            cwd=tmp_path,
        )
        assert res.returncode == 0

        reactions = [
            {
                "customer": "Nurse Jen",
                "reaction": "Tried it on 3 patients",
                "is_reaction": True,
            },
            {
                "customer": "Nurse Dave",
                "reaction": "Said it was cool",
                "is_reaction": False,
            },
        ]
        res = run_cli(
            "sprint",
            "test",
            "--sprint-id",
            "1",
            "--reactions-json",
            json.dumps(reactions),
            cwd=tmp_path,
        )
        assert res.returncode == 0
        assert "genuine reactions" in res.stdout

        res = run_cli(
            "sprint",
            "complete",
            "--sprint-id",
            "1",
            "--outcome",
            "98% accuracy achieved",
            cwd=tmp_path,
        )
        assert res.returncode == 0
        assert "Sprint complete" in res.stdout
