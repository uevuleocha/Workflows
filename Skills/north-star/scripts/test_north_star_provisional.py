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
ACTOR_COMMANDS = {"reopen","pursuit-stop","pursuit-remove","provisional-commit","checkpoint","refine","pause","resume","recover","finalize","end","feedback-add"}

def run(*args, expect_ok=True, inject_actor=True):
    global PASS, FAIL, TOTAL; TOTAL += 1
    command_args=list(args)
    if inject_actor and command_args and command_args[0] in ACTOR_COMMANDS and "--acting-agent" not in command_args:
        command_args += ["--acting-agent","Codex Agent"]
    cmd = [sys.executable, "-X", "utf8", str(SCRIPT), *command_args]
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
    return run("create","--workspace-root",str(WORKSPACE),"--subject",subject,"--topic",topic,"--writing-agent","Codex Agent","--goal",objective,"--pursuit","Test","--mode","full","--constraint","Stay in scope","--format","Produce the requested result","--definition-of-done","Check 1","--definition-of-done","Check 2","--failure","Unsupported completion")

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
    if phase: args += ["--batch",phase]
    return run(*args, expect_ok=expect_ok)
def pursuit_start(art, summary, phase=None):
    args = ["pursuit-start","--artifact",str(art),"--summary",summary]
    if phase: args += ["--batch",phase]
    return run(*args)
def pursuit_stop(art, summary):
    return run("pursuit-stop","--artifact",str(art),"--summary",summary)
def do_pause(art, reason="test"): return run("pause","--artifact",str(art),"--reason",reason)
def do_resume(art): return run("resume","--artifact",str(art))
def do_recover(art, note="test"): return run("recover","--artifact",str(art),"--note",note)
def do_end(art, note="test"): return run("end","--artifact",str(art),"--note",note)
def do_finalize(art, evidence="test", note="test"):
    return run("finalize","--artifact",str(art),"--evidence",evidence,"--note",note,"--verify-complete","1","--verify-complete","2","--constraints-verified","--format-verified","--failure-reviewed")
def do_reopen(art, phase="Reopened", next_action="Continue"):
    return run("reopen","--artifact",str(art),"--batch",phase,"--next-action",next_action)
def do_checkpoint(art, idx):
    return run("checkpoint","--artifact",str(art),"--verify-complete",str(idx),"--note","checked")
def do_remove(art, number, reason="wrong"):
    return run("pursuit-remove","--artifact",str(art),"--number",str(number),"--reason",reason)
def assert_terminal_state_block(art):
    text=art.read_text(encoding="utf-8")
    lines=[line for line in text.splitlines() if line.strip()]
    assert lines[-1]=="<!-- north-star:run-end -->", "run-end must be the final nonblank line"
    assert lines[-2].startswith("<!-- north-star:state-b64 "), "Base64 state must immediately precede run-end"
    lifecycle=text.index("North Star lifecycle:")
    provenance=text.index("## Agent Provenance")
    north=text.index("## North Star")
    change_log=text.index("## Agent Change Log")
    state=text.index("<!-- north-star:state-b64 ")
    assert lifecycle < provenance < north < change_log < state
    lifecycle_line_end=text.index("\n",lifecycle)
    assert not text[lifecycle_line_end:provenance].strip(), "Agent Provenance must immediately follow lifecycle"
    assert text.count("## Agent Provenance")==1 and text.count("## Agent Change Log")==1
    assert "| Field" in text and "| Value" in text
    for field in ("Content owner","Original writing agent","Created","Artifact role"):
        assert f"| {field}" in text
    assert not any(line.startswith("#") for line in text[change_log:state].splitlines()[1:]), "Agent Change Log must be the final human-readable section"

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

@test("16. Genuine legacy artifact: key absent before helper loads it")
def test16():
    import base64, re
    art = artifact_path("Legacy", "Legacy Artifact")
    # Strip the provisional key from the encoded state marker so the fixture
    # genuinely lacks it — not merely defaults to null.
    raw = art.read_text(encoding="utf-8")
    STATE_RE = re.compile(r"<!-- north-star:state-b64 (?P<payload>[A-Za-z0-9_\-=]+) -->")
    m = STATE_RE.search(raw)
    assert m, "state marker must exist"
    payload = m.group("payload")
    decoded = json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
    # Remove the provisional key if present (it is in current-format artifacts)
    decoded.pop("provisional", None)
    # Re-encode and write back
    new_payload = base64.urlsafe_b64encode(json.dumps(decoded, ensure_ascii=False, separators=(",",":")).encode("utf-8")).decode("ascii")
    new_raw = raw.replace(payload, new_payload)
    art.write_text(new_raw, encoding="utf-8")
    # Now re-read and assert the key is genuinely absent BEFORE the helper touches it
    raw2 = art.read_text(encoding="utf-8")
    m2 = STATE_RE.search(raw2)
    decoded2 = json.loads(base64.urlsafe_b64decode(m2.group("payload")).decode("utf-8"))
    assert "provisional" not in decoded2, "legacy fixture must genuinely lack the provisional key"
    # The current helper must load it safely and normalize with provisional: null
    s = status_json(art)
    assert s["provisional"] is None, "helper exposes provisional: null for legacy fixture"
    assert "provisional" in s, "provisional key present in normalized status output"

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

@test("24. Fallback disclosure: format-receipt outputs exact disclosure sentence")
def test24():
    art = artifact_path("Disclose", "Fallback Disclosure")
    prov_start(art)
    prov_commit(art, "Disclosed fallback work")
    # State: timing_source marker present
    s = status_json(art)
    assert s["pursuits"][-1].get("timing_source") == "provisional_fallback"
    # Production output: the literal disclosure sentence
    proc = run("format-receipt", "--artifact", str(art), "--type", "fallback-disclosure")
    assert proc is not None
    expected = "Full-turn fallback scoping was used for this pursuit — precise authoritative timing was missed."
    assert proc.stdout.strip() == expected, f"expected exact disclosure sentence, got: {proc.stdout.strip()}"

@test("25. Exactly-once timing: format-receipt outputs exact contract-shape statement")
def test25():
    art = artifact_path("ExactlyOnce", "Exactly One Row")
    before = len(status_json(art)["pursuits"])
    prov_start(art); pursuit_start(art, "Work"); pursuit_stop(art, "Work done")
    s = status_json(art)
    assert len(s["pursuits"]) == before + 1, "exactly one row added to ledger"
    assert s["provisional"] is None
    # Production output: the exact timing statement in contract shape
    proc = run("format-receipt", "--artifact", str(art), "--type", "timing-statement")
    assert proc is not None
    stdout = proc.stdout.strip()
    assert stdout.startswith("Pursuit "), f"timing statement must start with 'Pursuit', got: {stdout[:50]}"
    assert " — " in stdout, "timing statement must contain ' — ' separator"
    assert ". Grand total: " in stdout, "timing statement must contain '. Grand total: '"
    assert stdout.endswith("."), "timing statement must end with '.'"

@test("26. Paused footer: format-receipt outputs exact paused footer text")
def test26():
    art = artifact_path("PausedFooter", "Paused Footer")
    pursuit_start(art, "Pre-pause work"); pursuit_stop(art, "Pre-pause done")
    do_pause(art)
    s = status_json(art)
    assert s["status"] == "paused"
    assert s["provisional"] is None
    assert s["active_pursuit"] is None
    # Production output: the exact paused footer text
    proc = run("format-receipt", "--artifact", str(art), "--type", "mode-footer")
    assert proc is not None
    stdout = proc.stdout.strip()
    assert "Mode = " in stdout, "paused footer must start with 'Mode = '"
    assert "PAUSED" in stdout, "paused footer must contain 'PAUSED'"
    assert 'say "resume North Star" to continue' in stdout, "paused footer must contain resume instruction"
    # provisional-start must refuse while paused
    proc2 = run("provisional-start","--artifact",str(art), expect_ok=False)
    assert proc2 is not None and proc2.returncode != 0

@test("27. format-receipt timing-statement refuses when authoritative pursuit is open")
def test27():
    art = artifact_path("FmtGuard1", "Format Guard Auth")
    pursuit_start(art, "Open work")
    proc = run("format-receipt", "--artifact", str(art), "--type", "timing-statement", expect_ok=False)
    assert proc is not None and proc.returncode != 0
    assert "pursuit" in proc.stderr.lower() or "authoritative" in proc.stderr.lower()
    pursuit_stop(art, "Done")

@test("28. format-receipt timing-statement refuses when provisional is open")
def test28():
    art = artifact_path("FmtGuard2", "Format Guard Prov")
    prov_start(art)
    proc = run("format-receipt", "--artifact", str(art), "--type", "timing-statement", expect_ok=False)
    assert proc is not None and proc.returncode != 0
    assert "provisional" in proc.stderr.lower()
    prov_discard(art)

@test("29. Finalizer-receipt: forward-slash link, exact number and path")
def test29():
    art = artifact_path("FinRcpt", "Finalizer Receipt Test")
    pursuit_start(art, "Final work"); pursuit_stop(art, "Final work done")
    do_checkpoint(art, 1); do_checkpoint(art, 2)
    do_finalize(art)
    hist = WORKSPACE / "Archive" / "Historical" / "North Stars" / "FinRcpt"
    finalized = list(hist.glob("*_finalized.md"))
    assert len(finalized) == 1
    final_path = finalized[0].resolve()
    # Permanent number from filename
    import re
    m = re.match(r"^(\d+)\.\) ", final_path.name)
    assert m, "finalized artifact must have permanent N.) prefix"
    perm_num = m.group(1)
    expected_dest = final_path.as_posix()
    # Production finalizer receipt
    proc = run("format-receipt", "--artifact", str(final_path), "--type", "finalizer-receipt", "--subject", "FinRcpt")
    assert proc is not None
    stdout = proc.stdout.strip()
    # Contract shape
    assert f"North Star {perm_num} was verified and finalized." in stdout, f"wrong number or shape: {stdout[:80]}"
    assert ". Pursuit " in stdout
    assert ". Grand total: " in stdout
    # Exact forward-slash link with subject and number
    expected_link = f"[FinRcpt North Star {perm_num}](<{expected_dest}>)"
    assert expected_link in stdout, f"expected link: {expected_link}\ngot: {stdout}"
    # Reject prohibited forms
    assert "file:///" not in stdout, "must not contain file:// URI"
    assert "\\" not in stdout.split("](<")[1].split(">)")[0] if "](<" in stdout else True, "destination must not contain backslashes"

@test("30. format-receipt mode-footer refuses when timing is open")
def test30():
    art = artifact_path("PFGuard", "Paused Footer Guard")
    pursuit_start(art, "Work"); pursuit_stop(art, "Work done")
    do_pause(art)
    # Normal paused footer still works
    proc = run("format-receipt", "--artifact", str(art), "--type", "mode-footer", "--subject", "PFGuard")
    assert proc is not None
    assert "PAUSED" in proc.stdout
    # Now test: mode-footer refuses with open authoritative pursuit
    art2 = artifact_path("PFGuard2", "Paused Footer Guard 2")
    pursuit_start(art2, "Open work")
    proc2 = run("format-receipt", "--artifact", str(art2), "--type", "mode-footer", "--subject", "PFGuard2", expect_ok=False)
    assert proc2 is not None and proc2.returncode != 0
    pursuit_stop(art2, "Done")
    # And: mode-footer refuses with open provisional
    art3 = artifact_path("PFGuard3", "Paused Footer Guard 3")
    prov_start(art3)
    proc3 = run("format-receipt", "--artifact", str(art3), "--type", "mode-footer", "--subject", "PFGuard3", expect_ok=False)
    assert proc3 is not None and proc3.returncode != 0
    prov_discard(art3)

@test("31. Full Mode creation embeds the five-part contract and terminal state")
def test31():
    art=artifact_path("FullCreate","Full Contract Creation"); s=status_json(art)
    assert s["initial_mode"]=="full" and s["current_mode"]=="full"
    assert set(s["prompt_contract"])=={"goal","constraints","format","definition_of_done","failure"}
    text=art.read_text(encoding="utf-8")
    for heading in ("##### GOAL","##### CONSTRAINTS","##### FORMAT","##### DEFINITION OF DONE","##### FAILURE"): assert heading in text
    assert text.index("North Star lifecycle:") < text.index("## Agent Provenance") < text.index("## North Star")
    assert text.index("## Agent Change Log") < text.index("<!-- north-star:state-b64 ")
    assert_terminal_state_block(art)

@test("32. Full and Batch active footers and opt-in Prompt Contract output")
def test32():
    full=artifact_path("FullFooter","Full Footer")
    proc=run("format-receipt","--artifact",str(full),"--type","mode-footer"); assert proc and "North Star (FULL)" in proc.stdout
    contract_out=run("format-receipt","--artifact",str(full),"--type","prompt-contract"); assert contract_out
    for label in ("GOAL:","CONSTRAINTS:","FORMAT:","DEFINITION OF DONE:","FAILURE:"): assert label in contract_out.stdout
    batch=artifact_path("BatchFooter","Batch Footer")
    proc2=run("format-receipt","--artifact",str(batch),"--type","mode-footer"); assert proc2 and "North Star (BATCH)" in proc2.stdout

@test("33. Known iteration after pursuit 1 transitions immediately to Batch")
def test33():
    art=artifact_path("KnownIteration","Known Iteration")
    pursuit_start(art,"First pass"); pursuit_stop(art,"First pass done")
    run("checkpoint","--artifact",str(art),"--another-iteration","A corrective iteration is required.","--note","Iteration known")
    s=status_json(art); assert s["initial_mode"]=="full" and s["current_mode"]=="batch"
    assert len(s["mode_transitions"])==1 and s["mode_transitions"][0]["reason"]=="A corrective iteration is required."
    assert_terminal_state_block(art)

@test("34. Pursuit 2 cannot begin while current mode remains Full")
def test34():
    art=artifact_path("AutoIteration","Automatic Iteration")
    pursuit_start(art,"First pass"); pursuit_stop(art,"First done")
    assert status_json(art)["current_mode"]=="full"
    pursuit_start(art,"Second pass")
    s=status_json(art); assert s["current_mode"]=="batch" and len(s["mode_transitions"])==1
    assert s["active_pursuit"]["number"]==2
    pursuit_stop(art,"Second done"); assert_terminal_state_block(art)

@test("35. Material refinement updates the contract; evidence-only checkpoint does not")
def test35():
    art=artifact_path("Refinement","Contract Refinement")
    pursuit_start(art,"Initial work"); pursuit_stop(art,"Initial done")
    before=status_json(art)["prompt_contract"]
    do_checkpoint(art,1); after_checkpoint=status_json(art)["prompt_contract"]
    assert before==after_checkpoint
    run("refine","--artifact",str(art),"--goal","Refined goal","--constraint","New scope","--format","New format","--definition-of-done","New DoD","--failure","New failure","--note","User expanded scope")
    s=status_json(art); assert s["prompt_contract"]["goal"]=="Refined goal"
    assert s["definition_of_done_complete"]==[] and s["current_mode"]=="batch"
    assert_terminal_state_block(art)

@test("36. Finalization is gated by DoD evidence, Failure review, Format, and Constraints")
def test36():
    art=artifact_path("ContractGate","Contract Finalization Gate")
    pursuit_start(art,"Complete work"); pursuit_stop(art,"Work complete")
    proc=run("finalize","--artifact",str(art),"--verify-complete","1","--constraints-verified","--format-verified","--failure-reviewed",expect_ok=False)
    assert proc and "unchecked Definition of Done" in proc.stderr
    run("checkpoint","--artifact",str(art),"--failure-active","1")
    proc2=run("finalize","--artifact",str(art),"--verify-complete","1","--verify-complete","2","--constraints-verified","--format-verified","--failure-reviewed",expect_ok=False)
    assert proc2 and "active Failure" in proc2.stderr
    run("checkpoint","--artifact",str(art),"--clear-failures")
    proc3=run("finalize","--artifact",str(art),"--verify-complete","1","--verify-complete","2",expect_ok=False)
    assert proc3 and "constraints" in proc3.stderr
    do_finalize(art,"Direct completion evidence")
    final=list((WORKSPACE/"Archive"/"Historical"/"North Stars"/"ContractGate").glob("*_finalized.md"))[0]
    s=status_json(final); assert s["contract_review"] and s["status"]=="finalized"
    footer=run("format-receipt","--artifact",str(final),"--type","mode-footer"); assert footer and "FINALIZED THIS TURN" in footer.stdout
    assert_terminal_state_block(final)

@test("37. Terminal state placement survives lifecycle mutations")
def test37():
    art=artifact_path("TerminalPlacement","Terminal Placement")
    assert_terminal_state_block(art); prov_start(art); prov_discard(art); assert_terminal_state_block(art)
    pursuit_start(art,"Work"); pursuit_stop(art,"Done"); assert_terminal_state_block(art)
    do_pause(art); assert_terminal_state_block(art); do_resume(art); assert_terminal_state_block(art)
    run("refine","--artifact",str(art),"--pursuit","Refined approach","--note","Approach only"); assert_terminal_state_block(art)
    do_checkpoint(art,1); do_checkpoint(art,2); do_finalize(art)
    final=list((WORKSPACE/"Archive"/"Historical"/"North Stars"/"TerminalPlacement").glob("*_finalized.md"))[0]; assert_terminal_state_block(final)
    do_reopen(final); live=artifact_path("TerminalPlacement","Terminal Placement"); assert_terminal_state_block(live)

@test("38. Batch Mode creation remains Batch without a synthetic transition")
def test38():
    art=artifact_path("BatchFooter","Batch Footer"); s=status_json(art)
    assert s["initial_mode"]=="batch" and s["current_mode"]=="batch" and s["mode_transitions"]==[]
    pursuit_start(art,"Batch one"); pursuit_stop(art,"Batch one done")
    pursuit_start(art,"Batch two"); pursuit_stop(art,"Batch two done")
    assert status_json(art)["mode_transitions"]==[]
    assert_terminal_state_block(art)

@test("39. Provenance and change-log structure are mandatory and actor-owned")
def test39():
    art=artifact_path("FullCreate","Full Contract Creation")
    before=art.read_bytes()
    refused=run("checkpoint","--artifact",str(art),"--note","No actor supplied",expect_ok=False,inject_actor=False)
    assert refused and "--acting-agent" in refused.stderr
    assert art.read_bytes()==before
    do_checkpoint(art,1)
    text=art.read_text(encoding="utf-8")
    assert text.count("## Agent Provenance")==1 and text.count("## Agent Change Log")==1
    assert text.count("## Feedback Section")==1
    # Change log is a five-column table, not a bullet list.
    assert "| Date and Time" in text and "| Model " in text and "| Scope" in text
    assert "Created the North Star artifact" in text
    assert "Checkpointed North Star progress and verification state" in text
    for field in ("Content owner","Original writing agent","Original writing LLM","Created","Artifact role"):
        assert f"| {field}" in text, field
    # Mandatory section order: provenance -> content -> feedback -> change log -> state.
    assert text.index("## Agent Provenance")<text.index("## North Star")<text.index("## Feedback Section")<text.index("## Agent Change Log")
    # Feedback is helper-owned, numbered, and appended by any acting agent.
    run("feedback-add","--artifact",str(art),"--descriptor","Independent verification",
        "--body","Verified the five-row provenance table.")
    text=art.read_text(encoding="utf-8")
    assert "### Feedback 1 — " in text and "Independent verification" in text
    assert text.index("## Feedback Section")<text.index("## Agent Change Log")
    assert_terminal_state_block(art)

@test("40. Exact model attribution accepts full identities and rejects family labels")
def test40():
    accepted = run(
        "create", "--workspace-root", str(WORKSPACE), "--subject", "ExactModel",
        "--topic", "Exact Model", "--writing-agent", "Codex Agent",
        "--writing-llm", "GPT-5.6 Sol", "--goal", "Exact model test",
        "--pursuit", "Test", "--mode", "batch", "--constraint", "Stay in scope",
        "--format", "Produce result", "--definition-of-done", "Check 1",
        "--failure", "Ambiguous model",
    )
    assert accepted is not None
    art = artifact_path("ExactModel", "Exact Model")
    assert status_json(art)["provenance"]["original_writing_llm"] == "GPT-5.6 Sol"
    for model in ("GPT-5", "GPT-5.6", "Claude", "Codex Agent"):
        rejected = run(
            "create", "--workspace-root", str(WORKSPACE), "--subject", f"Bad{model[:2]}",
            "--topic", f"Bad {model}", "--writing-agent", "Codex Agent",
            "--writing-llm", model, "--goal", "Reject model", "--pursuit", "Test",
            "--mode", "batch", "--constraint", "Stay in scope", "--format", "Result",
            "--definition-of-done", "Check", "--failure", "Ambiguous model",
            expect_ok=False,
        )
        assert rejected and "full exact model name" in rejected.stderr
    # Omitted identity remains the honest fallback; no exact identity is guessed.
    fallback = create_ns("UnknownModel", "Unknown Model")
    assert fallback is not None
    assert status_json(artifact_path("UnknownModel", "Unknown Model"))["provenance"]["original_writing_llm"] == "Not recorded"

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
        ("PausedFooter","Paused Footer"), ("FmtGuard1","Format Guard Auth"),
        ("FmtGuard2","Format Guard Prov"), ("FinRcpt","Finalizer Receipt Test"),
        ("PFGuard","Paused Footer Guard"), ("PFGuard2","Paused Footer Guard 2"),
        ("PFGuard3","Paused Footer Guard 3"),
        ("FullCreate","Full Contract Creation"), ("FullFooter","Full Footer"),
        ("KnownIteration","Known Iteration"), ("AutoIteration","Automatic Iteration"),
        ("Refinement","Contract Refinement"), ("ContractGate","Contract Finalization Gate"),
        ("TerminalPlacement","Terminal Placement"),
    ]
    for subj, top in subjects_topics:
        create_ns(subj, top)
    run("create","--workspace-root",str(WORKSPACE),"--subject","BatchFooter","--topic","Batch Footer","--writing-agent","Codex Agent","--goal","Batch objective","--pursuit","Test","--mode","batch","--constraint","Stay in scope","--format","Produce result","--definition-of-done","Check 1","--definition-of-done","Check 2","--failure","Unsupported completion")

    # Run all named tests
    test1(); test2(); test3(); test4(); test5(); test6(); test7(); test8()
    test9(); test10(); test11(); test12(); test13(); test14(); test15()
    test16(); test17(); test18(); test19(); test20()
    test21(); test22(); test23(); test24(); test25(); test26()
    test27(); test28(); test29(); test30(); test31(); test32(); test33()
    test34(); test35(); test36(); test37(); test38(); test39(); test40()

    print(f"\n{'='*60}")
    print(f"Results: {PASS}/{TOTAL} subprocess checks passed, {FAIL} failed")
    print(f"Named test cases: 40")
    teardown()
    return 0 if FAIL == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
