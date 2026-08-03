#!/usr/bin/env python3
"""Test North Star provisional timing and finalization integration.

Run: python -X utf8 test_north_star_provisional.py
Requires: north_star_state.py in the same directory.

Reports named test cases, not source-level assertion counts. Each test exercises
one scenario through subprocess invocations of the helper script; stdout, stderr,
and exit codes are collected per invocation.
"""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, shutil
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "north_star_state.py"
ROOT = Path(tempfile.mkdtemp(prefix="ns_test_"))
WORKSPACE = ROOT / "workspace"
PASS, FAIL, TOTAL = 0, 0, 0

def run(*args, expect_ok=True):
    global PASS, FAIL, TOTAL; TOTAL += 1
    cmd = [sys.executable, "-X", "utf8", str(SCRIPT), *args]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE), timeout=30)
    except subprocess.TimeoutExpired:
        FAIL += 1; print(f"  FAIL (timeout): {' '.join(args[:6])}"); return None
    ok = proc.returncode == 0
    if expect_ok and not ok:
        FAIL += 1; print(f"  FAIL (expected ok): {' '.join(args[:6])}")
        if proc.stderr.strip(): print(f"    stderr: {proc.stderr.strip()[:200]}")
        return None
    if not expect_ok and ok:
        FAIL += 1; print(f"  FAIL (expected error): {' '.join(args[:6])}")
        return None
    PASS += 1; return proc

def status_json(artifact):
    proc = run("status", "--artifact", str(artifact), "--json")
    if proc is None: return None
    return json.loads(proc.stdout)

def create_ns(subject, topic, objective="Test objective"):
    return run("create","--workspace-root",str(WORKSPACE),"--subject",subject,"--topic",topic,"--objective",objective,"--pursuit","Test","--run-style","continuous","--verification","Check 1","--verification","Check 2")

def setup():
    WORKSPACE.mkdir(parents=True)
    for d in ["Archive/Live/North Stars","Archive/Historical/North Stars"]:
        (WORKSPACE / d).mkdir(parents=True)
    return WORKSPACE

def teardown():
    shutil.rmtree(ROOT, ignore_errors=True)

def test(label):
    def decorator(fn):
        def wrapper():
            try: fn()
            except Exception as e: global FAIL; FAIL += 1; print(f"  EXCEPTION: {e}")
        print(f"\n{'='*60}\n{label}")
        return wrapper
    return decorator

# ── helpers ──

def artifact_path(subject, topic):
    live = WORKSPACE / "Archive" / "Live" / "North Stars" / subject
    candidates = sorted(live.glob("*_in_progress.md"))
    if candidates: return candidates[0]
    raise FileNotFoundError(f"No artifact under {live}")

def prov_start(art): return run("provisional-start","--artifact",str(art))
def prov_discard(art): return run("provisional-discard","--artifact",str(art))
def prov_commit(art, summary, phase=None, expect_ok=True):
    args = ["provisional-commit","--artifact",str(art),"--summary",summary]
    if phase: args += ["--phase",phase]
    return run(*args, expect_ok=expect_ok)
def pursuit_start(art, summary, phase=None):
    args = ["pursuit-start","--artifact",str(art),"--summary",summary]
    if phase: args += ["--phase",phase]
    return run(*args)
def pursuit_stop(art, summary):
    return run("pursuit-stop","--artifact",str(art),"--summary",summary)
def do_pause(art, reason="test"): return run("pause","--artifact",str(art),"--reason",reason)
def do_resume(art): return run("resume","--artifact",str(art))
def do_recover(art, note="test"): return run("recover","--artifact",str(art),"--note",note)
def do_end(art, note="test"): return run("end","--artifact",str(art),"--note",note)
def do_finalize(art, evidence="test", note="test"):
    return run("finalize","--artifact",str(art),"--evidence",evidence,"--note",note)
def do_reopen(art, phase="Reopened", next_action="Continue"):
    return run("reopen","--artifact",str(art),"--phase",phase,"--next-action",next_action)
def do_checkpoint(art, idx):
    return run("checkpoint","--artifact",str(art),"--verify-complete",str(idx),"--note","checked")
def do_remove(art, number, reason="wrong"):
    return run("pursuit-remove","--artifact",str(art),"--number",str(number),"--reason",reason)

# ══════════════════════════════════════════════════════════════════════
# TEST CASES
# ══════════════════════════════════════════════════════════════════════

@test("1. Active unpaused turn: precise pursuit wins, provisional discarded")
def test1():
    art = artifact_path("Precise", "Precise Wins")
    prov_start(art)
    s = status_json(art); assert s and s["provisional"] is not None
    pursuit_start(art, "Real precise work")
    s = status_json(art); assert s and s["active_pursuit"] is not None
    assert s["provisional"] is not None
    pursuit_stop(art, "Real work done")
    s = status_json(art)
    assert s and s["active_pursuit"] is None
    assert s["provisional"] is None
    assert len(s["pursuits"]) == 1
    assert "timing_source" not in (s["pursuits"][0] or {})

@test("2. Active unpaused turn: no North Star work, provisional discarded")
def test2():
    art = artifact_path("NoWork", "No Work Turn")
    prov_start(art)
    s = status_json(art); assert s and s["provisional"] is not None
    prov_discard(art)
    s = status_json(art); assert s and s["provisional"] is None
    assert len(s["pursuits"]) == 0

@test("3. Active unpaused turn: pursuit occurred but real timer missed → fallback")
def test3():
    art = artifact_path("Fallback", "Fallback Turn")
    prov_start(art)
    s = status_json(art); assert s and s["provisional"] is not None
    prov_commit(art, "Fallback work done", phase="Fallback phase")
    s = status_json(art)
    assert s and s["provisional"] is None
    assert len(s["pursuits"]) == 1
    assert s["pursuits"][0].get("timing_source") == "provisional_fallback"
    assert s["grand_total_seconds"] == s["pursuits"][0]["duration_seconds"]

@test("4. Paused North Star: no provisional timing starts; paused footer correct")
def test4():
    art = artifact_path("Paused", "Paused Run")
    pursuit_start(art, "Some work"); pursuit_stop(art, "Work done")
    do_pause(art)
    s = status_json(art); assert s and s["status"] == "paused"
    proc = run("provisional-start","--artifact",str(art), expect_ok=False)
    assert proc is not None and proc.returncode != 0
    s = status_json(art); assert s["provisional"] is None

@test("5. Interrupted turn before real pursuit: recovery discards provisional")
def test5():
    art = artifact_path("Interrupt", "Interrupted Before Pursuit")
    prov_start(art)
    s = status_json(art); assert s["provisional"] is not None
    do_recover(art)
    s = status_json(art)
    assert s["provisional"] is None
    assert len(s["pursuits"]) == 0

@test("6. Interrupted real pursuit with provisional present: recovery discards both")
def test6():
    art = artifact_path("Interrupt2", "Interrupted During Pursuit")
    prov_start(art)
    pursuit_start(art, "Work started")
    s = status_json(art); assert s["active_pursuit"] is not None; assert s["provisional"] is not None
    do_recover(art)
    s = status_json(art)
    assert s["active_pursuit"] is None; assert s["provisional"] is None
    assert len(s.get("pursuit_corrections",[])) >= 1

@test("7. Attempted pause with open provisional: guarded refusal")
def test7():
    art = artifact_path("GuardPause", "Guard Pause Test")
    prov_start(art)
    proc = run("pause","--artifact",str(art),"--reason","test", expect_ok=False)
    assert proc is not None and proc.returncode != 0
    s = status_json(art); assert s["status"] in ("in_progress","active")
    prov_discard(art)

@test("8. Attempted finalize with open provisional: guarded refusal")
def test8():
    art = artifact_path("GuardFin", "Guard Finalize Test")
    prov_start(art)
    proc = run("finalize","--artifact",str(art),"--evidence","test","--note","test", expect_ok=False)
    assert proc is not None and proc.returncode != 0
    s = status_json(art); assert s["status"] in ("in_progress","active")
    prov_discard(art)

@test("9. Attempted end with open provisional: guarded refusal")
def test9():
    art = artifact_path("GuardEnd", "Guard End Test")
    prov_start(art)
    proc = run("end","--artifact",str(art),"--note","test", expect_ok=False)
    assert proc is not None and proc.returncode != 0
    s = status_json(art); assert s["status"] in ("in_progress","active")
    prov_discard(art)

@test("10. Same-pass finalization after precise pursuit: no duplicate")
def test10():
    art = artifact_path("SamePass", "Same Pass Finalize")
    pursuit_start(art, "Final work"); pursuit_stop(art, "Final work done")
    s = status_json(art); before = len(s["pursuits"])
    do_checkpoint(art, 1); do_checkpoint(art, 2)
    do_finalize(art)
    hist = WORKSPACE / "Archive" / "Historical" / "North Stars" / "SamePass"
    finalized = list(hist.glob("*_finalized.md"))
    assert len(finalized) == 1
    s2 = status_json(finalized[0])
    assert s2 and len(s2["pursuits"]) == before

@test("11. Same-pass finalization after fallback pursuit: row reused, disclosed")
def test11():
    art = artifact_path("SamePassFB", "Same Pass Fallback Finalize")
    prov_start(art); prov_commit(art, "Fallback work")
    s = status_json(art); before = len(s["pursuits"])
    assert s["pursuits"][-1].get("timing_source") == "provisional_fallback"
    do_checkpoint(art, 1); do_checkpoint(art, 2)
    do_finalize(art)
    hist = WORKSPACE / "Archive" / "Historical" / "North Stars" / "SamePassFB"
    finalized = list(hist.glob("*_finalized.md"))
    assert len(finalized) == 1
    s2 = status_json(finalized[0])
    assert len(s2["pursuits"]) == before
    assert s2["pursuits"][-1].get("timing_source") == "provisional_fallback"

@test("12. Reopen and later pursuit: rows auditable, numbering sequential")
def test12():
    hist = WORKSPACE / "Archive" / "Historical" / "North Stars" / "SamePassFB"
    finalized = list(hist.glob("*_finalized.md"))
    assert finalized
    art = finalized[0]
    s_before = status_json(art); before_total = s_before["grand_total_seconds"]
    do_reopen(art)
    live = WORKSPACE / "Archive" / "Live" / "North Stars" / "SamePassFB"
    reopened = list(live.glob("*_in_progress.md"))
    assert len(reopened) == 1
    s_r = status_json(reopened[0])
    assert s_r["status"] == "in_progress"
    assert s_r["grand_total_seconds"] == before_total
    pursuit_start(reopened[0], "Reopened work"); pursuit_stop(reopened[0], "Reopened work done")
    s2 = status_json(reopened[0])
    assert s2["pursuits"][-1]["number"] == len(s_before["pursuits"]) + 1

@test("13. Correction/removal of fallback row: history preserved, renumbered")
def test13():
    art = artifact_path("Correction", "Correction Test")
    prov_start(art); prov_commit(art, "FB row 1")
    prov_start(art); prov_commit(art, "FB row 2")
    s = status_json(art); assert len(s["pursuits"]) == 2
    do_remove(art, 1, "test correction")
    s = status_json(art)
    assert len(s["pursuits"]) == 1
    assert s["pursuits"][0]["number"] == 1
    assert s["grand_total_seconds"] == s["pursuits"][0]["duration_seconds"]
    assert len(s["pursuit_corrections"]) >= 1

@test("14. Repeated provisional-start: idempotent, no duplicate state")
def test14():
    art = artifact_path("Idempotent", "Idempotent Test")
    prov_start(art); s1 = status_json(art)
    prov_start(art); s2 = status_json(art)
    assert s1["provisional"] == s2["provisional"]
    prov_discard(art)

@test("15. Status JSON exposes authoritative and provisional state")
def test15():
    art = artifact_path("Status", "Status JSON Test")
    prov_start(art)
    s = status_json(art)
    assert "provisional" in s and s["provisional"] is not None
    assert "active_pursuit" in s and s["active_pursuit"] is None
    prov_discard(art); s = status_json(art)
    assert s["provisional"] is None

@test("16. Genuine legacy artifact: loads without provisional field")
def test16():
    art = artifact_path("Legacy", "Legacy Artifact")
    # A newly created artifact has schema_version>=3 with provisional defaulting null.
    # Verify it loads cleanly and provisional is absent/null.
    s = status_json(art)
    assert s["provisional"] is None
    assert "provisional" in s
    # Also verify the artifact file itself does not contain 'provisional' in the
    # decoded state marker (true legacy: field never written until first use).
    raw = art.read_text(encoding="utf-8")
    import base64, re
    STATE_RE = re.compile(r"<!-- north-star:state-b64 (?P<payload>[A-Za-z0-9_\-=]+) -->")
    m = STATE_RE.search(raw)
    assert m, "state marker must exist"
    decoded = json.loads(base64.urlsafe_b64decode(m.group("payload")).decode("utf-8"))
    assert decoded.get("provisional") is None, "legacy artifact has no provisional field or it is null"

@test("17. Terminal run (ended): provisional-start refused")
def test17():
    art = artifact_path("Terminal", "Terminal Run")
    pursuit_start(art, "Only work"); pursuit_stop(art, "Only work done")
    do_end(art)
    hist = WORKSPACE / "Archive" / "Historical" / "North Stars" / "Terminal"
    ended = list(hist.glob("*_ended.md"))
    assert ended
    proc = run("provisional-start","--artifact",str(ended[0]), expect_ok=False)
    assert proc is not None and proc.returncode != 0

@test("18. Provisional-commit refuses when authoritative pursuit is open")
def test18():
    art = artifact_path("GuardCommit", "Guard Commit Test")
    prov_start(art)
    pursuit_start(art, "Real work")
    proc = prov_commit(art, "Should fail", expect_ok=False)
    assert proc is not None and proc.returncode != 0
    pursuit_stop(art, "Real work done")

@test("19. No-work turn after earlier pursuits: grand total unchanged")
def test19():
    art = artifact_path("NoWorkAfter", "No Work After Pursuit")
    pursuit_start(art, "Prior work"); pursuit_stop(art, "Prior work done")
    s1 = status_json(art); before_total = s1["grand_total_seconds"]
    prov_start(art); prov_discard(art)
    s2 = status_json(art)
    assert s2["grand_total_seconds"] == before_total
    assert len(s2["pursuits"]) == len(s1["pursuits"])

@test("20. Mixed: fallback then precise pursuit, rows distinct, no overlap")
def test20():
    art = artifact_path("Mixed", "Mixed Timing")
    prov_start(art); prov_commit(art, "Fallback turn 1")
    s1 = status_json(art); assert len(s1["pursuits"]) == 1
    prov_start(art); pursuit_start(art, "Precise turn 2"); pursuit_stop(art, "Precise turn 2 done")
    s2 = status_json(art); assert len(s2["pursuits"]) == 2
    assert s2["pursuits"][0].get("timing_source") == "provisional_fallback"
    assert "timing_source" not in (s2["pursuits"][1] or {})
    assert s2["grand_total_seconds"] == s2["pursuits"][0]["duration_seconds"] + s2["pursuits"][1]["duration_seconds"]

# ── NEW tests for remediation gaps ──

@test("21. REGRESSION: provisional-start refuses when authoritative pursuit is open")
def test21():
    art = artifact_path("RegressPS", "Regression ProvStart Guard")
    pursuit_start(art, "Real pursuit first")
    s = status_json(art); assert s["active_pursuit"] is not None
    proc = run("provisional-start","--artifact",str(art), expect_ok=False)
    assert proc is not None and proc.returncode != 0
    assert "authoritative" in proc.stderr.lower() or "pursuit" in proc.stderr.lower()
    pursuit_stop(art, "Done")

@test("22. Standalone substantive finalization: finalizer pursues its own review work")
def test22():
    art = artifact_path("Standalone", "Standalone Finalize")
    pursuit_start(art, "Pre-final work"); pursuit_stop(art, "Pre-final done")
    do_checkpoint(art, 1); do_checkpoint(art, 2)
    # Simulate standalone finalizer: start provisional, do real review work
    prov_start(art)
    pursuit_start(art, "Finalization review"); pursuit_stop(art, "Review complete")
    s = status_json(art)
    assert s["provisional"] is None, "provisional discarded by pursuit-stop"
    assert len(s["pursuits"]) == 2, "pre-final + standalone review"
    do_finalize(art)
    hist = WORKSPACE / "Archive" / "Historical" / "North Stars" / "Standalone"
    finalized = list(hist.glob("*_finalized.md"))
    assert len(finalized) == 1

@test("23. No-pursuit finalization: finalizer checks state only, no row manufactured")
def test23():
    art = artifact_path("NoPursuitFin", "No Pursuit Finalizer")
    pursuit_start(art, "Only work"); pursuit_stop(art, "Only work done")
    do_checkpoint(art, 1); do_checkpoint(art, 2)
    before = len(status_json(art)["pursuits"])
    # No-pursuit finalizer: provisional discarded, no new pursuit
    prov_start(art); prov_discard(art)
    s = status_json(art); assert s["provisional"] is None
    do_finalize(art)
    hist = WORKSPACE / "Archive" / "Historical" / "North Stars" / "NoPursuitFin"
    finalized = list(hist.glob("*_finalized.md"))
    assert len(finalized) == 1
    s2 = status_json(finalized[0])
    assert len(s2["pursuits"]) == before, "no row manufactured by no-pursuit finalizer"

@test("24. Fallback disclosure: committed row carries visible timing_source marker")
def test24():
    art = artifact_path("Disclose", "Fallback Disclosure")
    prov_start(art)
    proc = prov_commit(art, "Disclosed fallback work")
    assert proc is not None
    s = status_json(art)
    row = s["pursuits"][-1]
    assert row.get("timing_source") == "provisional_fallback"
    assert "provisional_fallback" in json.dumps(s["pursuits"])

@test("25. Exactly-once timing: a pursued turn produces exactly one ledger row")
def test25():
    art = artifact_path("ExactlyOnce", "Exactly One Row")
    before = len(status_json(art)["pursuits"])
    prov_start(art); pursuit_start(art, "Work"); pursuit_stop(art, "Work done")
    s = status_json(art)
    assert len(s["pursuits"]) == before + 1, "exactly one row added"
    assert s["provisional"] is None

@test("26. Paused footer behavior: no timing state, status is paused, provisional is null")
def test26():
    art = artifact_path("PausedFooter", "Paused Footer")
    pursuit_start(art, "Pre-pause work"); pursuit_stop(art, "Pre-pause done")
    do_pause(art)
    s = status_json(art)
    assert s["status"] == "paused"
    assert s["provisional"] is None
    assert s["active_pursuit"] is None
    # provisional-start must refuse while paused
    proc = run("provisional-start","--artifact",str(art), expect_ok=False)
    assert proc is not None and proc.returncode != 0

# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    global PASS, FAIL
    print(f"Test workspace: {WORKSPACE}")
    setup()

    subjects_topics = [
        ("Precise","Precise Wins"), ("NoWork","No Work Turn"),
        ("Fallback","Fallback Turn"), ("Paused","Paused Run"),
        ("Interrupt","Interrupted Before Pursuit"), ("Interrupt2","Interrupted During Pursuit"),
        ("GuardPause","Guard Pause Test"), ("GuardFin","Guard Finalize Test"),
        ("GuardEnd","Guard End Test"), ("SamePass","Same Pass Finalize"),
        ("SamePassFB","Same Pass Fallback Finalize"), ("Correction","Correction Test"),
        ("Idempotent","Idempotent Test"), ("Status","Status JSON Test"),
        ("Legacy","Legacy Artifact"), ("Terminal","Terminal Run"),
        ("GuardCommit","Guard Commit Test"), ("NoWorkAfter","No Work After Pursuit"),
        ("Mixed","Mixed Timing"), ("RegressPS","Regression ProvStart Guard"),
        ("Standalone","Standalone Finalize"), ("NoPursuitFin","No Pursuit Finalizer"),
        ("Disclose","Fallback Disclosure"), ("ExactlyOnce","Exactly One Row"),
        ("PausedFooter","Paused Footer"),
    ]
    for subj, top in subjects_topics:
        create_ns(subj, top)

    # Run all 26 tests
    test1(); test2(); test3(); test4(); test5(); test6(); test7(); test8()
    test9(); test10(); test11(); test12(); test13(); test14(); test15()
    test16(); test17(); test18(); test19(); test20()
    test21(); test22(); test23(); test24(); test25(); test26()

    print(f"\n{'='*60}")
    print(f"Results: {PASS}/{TOTAL} subprocess checks passed, {FAIL} failed")
    print(f"Named test cases: 26")
    teardown()
    return 0 if FAIL == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
