"""Runner: keeps one GitHub Actions job alive for up to LOOP_MINUTES and runs the whole analysis every 5 minutes.

Why: GitHub delays free scheduled workflows. A "*/5" schedule actually ran about once an hour, so alerts could be
an hour late. Inside one long job the timing is ours: a cycle every 5 minutes, on the clock (:00, :05, :10 ...).
The workflow schedule only restarts the runner when a job ends (jobs are capped at 6 hours).

Each cycle runs the same steps as before. Results are committed every PUSH_EVERY cycles (default 2 = every
10 minutes) so the website stays fresh without going over GitHub Pages' build limit. Telegram alerts go out on
every cycle and do not wait for the commit.
Env: LOOP_MINUTES (default 330), PUSH_EVERY (default 2). Outside market hours it runs one cycle and stops.
"""
import os
import subprocess
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

CORE = ["levels.py", "ict.py", "confluence.py"]
OPTIONAL = ["chart.py", "news.py", "macro.py", "quality.py", "grade.py", "spot.py", "track.py", "pips_report.py", "live_models.py", "postnews.py", "notify.py", "session.py", "guide.py", "poll.py", "academy.py", "cot.py", "breaking.py"]
LOOP_MIN = float(os.environ.get("LOOP_MINUTES", 330))
PUSH_EVERY = int(os.environ.get("PUSH_EVERY", 2))
STEP_TIMEOUT = 240
BRANCH = os.environ.get("GITHUB_REF_NAME") or "main"


def market_open():   # gold: Sunday 18:00 to Friday 17:00 New York, daily break 17:00-18:00
    ny = datetime.now(ZoneInfo("America/New_York"))
    wd, h = ny.weekday(), ny.hour
    return not (wd == 5 or (wd == 4 and h >= 17) or (wd == 6 and h < 18))


def run(script):
    t = time.time()
    try:
        r = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=STEP_TIMEOUT)
        out = (r.stdout.strip().splitlines() or [""])[-1][:160]
        ok = r.returncode == 0
        if not ok:
            out = (r.stderr.strip().splitlines() or ["failed"])[-1][:200]
    except subprocess.TimeoutExpired:
        ok, out = False, f"timed out after {STEP_TIMEOUT}s"
    print(f"  {'ok ' if ok else 'ERR'} {script:14} {time.time() - t:5.1f}s  {out}", flush=True)
    return ok


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True)


def push():
    git("add", "--", "*.json")
    if git("diff", "--staged", "--quiet").returncode == 0:
        return
    git("commit", "-m", "Update analysis live data")
    for attempt in range(3):
        pull = git("pull", "--rebase", "-X", "theirs", "origin", BRANCH)
        if pull.returncode != 0:
            git("rebase", "--abort")
        if git("push", "origin", f"HEAD:{BRANCH}").returncode == 0:
            print("  pushed results", flush=True)
            return
        time.sleep(5 * (attempt + 1))
    print("  push failed, will retry next cycle", flush=True)


def cycle(n):
    print(f"cycle {n} at {datetime.now(ZoneInfo('Asia/Phnom_Penh')):%a %H:%M} Phnom Penh", flush=True)
    if n > 1:   # pick up backtest.json and other changes made by the daily backtest job
        git("pull", "--rebase", "-X", "theirs", "origin", BRANCH)
    run("scalp.py")   # first: the COMBO scalp needs the just-closed candle within ~1 minute
    core_ok = all([run(s) for s in CORE])
    if core_ok:
        for s in OPTIONAL:
            run(s)
    env = dict(os.environ, JOB_STATUS="success" if core_ok else "failure")
    subprocess.run([sys.executable, "status.py"], env=env, timeout=60)
    return core_ok


def main():
    start = time.time()
    n = 0
    while True:
        n += 1
        cycle(n)
        if n % PUSH_EVERY == 0 or not market_open():
            push()
        if not market_open():
            print("market closed: stopping until the next scheduled start")
            break
        nxt = (int(time.time() // 300) + 1) * 300 + 20   # next 5-minute mark, +20s so the candle has closed
        if (nxt - start) / 60 > LOOP_MIN:
            break
        try:   # answer member commands (/check ...) while waiting for the next cycle
            import listener
            listener.serve(nxt)
        except Exception as e:
            print("listener stopped:", e, flush=True)
            time.sleep(max(0, nxt - time.time()))
    push()
    if market_open():
        os.makedirs("data/cache", exist_ok=True)
        open("data/cache/next_shift", "w").write(str(time.time()))
    print(f"runner finished after {n} cycles, {(time.time() - start) / 60:.0f} min")


if __name__ == "__main__":
    main()
