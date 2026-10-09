"""
OS Services Demonstrator  -  Micro Project (Operating System)
Author : G. Vikas Kumar | B.Tech CSE (AI/ML), Sandip University, Nashik

Shows the main services an Operating System provides to users and programs
(Silberschatz, "Operating System Concepts"), using Python's standard library:

  1. Program Execution        5. Communication (IPC)
  2. File-System Manipulation 6. Error Detection
  3. I/O Operations           7. Resource Allocation / Accounting
  4. System Calls (low-level) 8. Protection & Security

Used by app.py (Flask dashboard).
Works on Windows, Linux and macOS (no extra libraries needed).
"""

import os
import sys
import time
import shutil
import platform
import subprocess
import multiprocessing as mp

SANDBOX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sandbox")


def header(title):
    print("\n" + "=" * 62)
    print(f"  {title}")
    print("=" * 62)


# ---------------------------------------------------------------- 1
def program_execution():
    header("1. PROGRAM EXECUTION SERVICE")
    print("OS loads a program into memory, runs it and ends it (normally/abnormally).")
    print(f"This program's PID : {os.getpid()}   | Parent PID: {os.getppid()}")
    start = time.time()
    result = subprocess.run(
        [sys.executable, "-c", "import os; print('  child PID =', os.getpid())"],
        capture_output=True, text=True)
    print("Child process output:")
    print(result.stdout.rstrip())
    print(f"Child exit code    : {result.returncode}  (0 = normal termination)")
    print(f"Time taken         : {time.time() - start:.3f} s")
    bad = subprocess.run([sys.executable, "-c", "import sys; sys.exit(3)"])
    print(f"Abnormal exit demo : exit code = {bad.returncode}")


# ---------------------------------------------------------------- 2
def file_manipulation():
    header("2. FILE-SYSTEM MANIPULATION SERVICE")
    os.makedirs(SANDBOX, exist_ok=True)
    f = os.path.join(SANDBOX, "notes.txt")
    with open(f, "w") as fh:
        fh.write("Hello from the OS file service!\n")
    print("Created  :", f)
    with open(f, "a") as fh:
        fh.write("This line was appended.\n")
    print("Appended : 1 line")
    with open(f) as fh:
        print("Read     :", fh.read().replace("\n", " | "))
    renamed = os.path.join(SANDBOX, "notes_renamed.txt")
    os.rename(f, renamed)
    print("Renamed  : notes.txt -> notes_renamed.txt")
    shutil.copy(renamed, os.path.join(SANDBOX, "backup.txt"))
    print("Copied   : -> backup.txt")
    print("Directory listing of sandbox:")
    for name in sorted(os.listdir(SANDBOX)):
        print(f"   {name:<22}{os.path.getsize(os.path.join(SANDBOX, name)):>5} bytes")
    os.remove(renamed)
    print("Deleted  : notes_renamed.txt")


# ---------------------------------------------------------------- 3
def io_operations(interactive=False):
    header("3. I/O OPERATIONS SERVICE")
    print("User programs cannot touch devices directly; the OS does I/O for them.")
    print("Output device (screen)  -> sys.stdout.write()")
    sys.stdout.write("  Written to the screen via the OS.\n")
    total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
    gb = 1024 ** 3
    print(f"Storage device (disk)   -> total {total/gb:.1f} GB | used {used/gb:.1f} GB | free {free/gb:.1f} GB")
    if interactive and sys.stdin.isatty():
        name = input("Input device (keyboard)  -> type your name: ")
        print(f"  Hello, {name}! (read through the OS)")
    else:
        print("Input device (keyboard) -> skipped (non-interactive mode)")


# ---------------------------------------------------------------- 4
def system_calls():
    header("4. SYSTEM CALLS (low-level interface)")
    print("A system call is how a program requests a service from the kernel.")
    os.makedirs(SANDBOX, exist_ok=True)
    path = os.path.join(SANDBOX, "syscall.txt")
    fd = os.open(path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC)      # open()
    print(f"open()  -> file descriptor = {fd}")
    n = os.write(fd, b"written using os.write()\n")                  # write()
    print(f"write() -> {n} bytes written")
    os.close(fd)                                                    # close()
    print("close() -> descriptor released")
    fd = os.open(path, os.O_RDONLY)
    data = os.read(fd, 100)                                         # read()
    os.close(fd)
    print(f"read()  -> {data.decode().strip()!r}")
    print(f"getpid() = {os.getpid()}   |  getcwd() = {os.getcwd()}")
    os.remove(path)


# ---------------------------------------------------------------- 5
def _child(conn):
    msg = conn.recv()
    conn.send(f"Child received '{msg}' and replies: Hi parent!")
    conn.close()


def communication():
    header("5. COMMUNICATION SERVICE (Inter-Process Communication)")
    print("Processes exchange information using message passing (a pipe here).")
    parent, child = mp.Pipe()
    p = mp.Process(target=_child, args=(child,))
    p.start()
    parent.send("Hello child")
    print("Parent sent    : Hello child")
    print("Parent got     :", parent.recv())
    p.join()
    print(f"Child finished with exit code {p.exitcode}")


# ---------------------------------------------------------------- 6
def error_detection():
    header("6. ERROR DETECTION & HANDLING")
    print("The OS detects errors in hardware, I/O and programs and reports them.")
    tests = [
        ("Open a missing file", lambda: open(os.path.join(SANDBOX, "nope.txt"))),
        ("Divide by zero", lambda: 1 / 0),
        ("Read a directory as a file", lambda: open(os.getcwd()).read()),
        ("Run a missing program", lambda: subprocess.run(["no_such_program_xyz"])),
    ]
    for label, action in tests:
        try:
            action()
        except Exception as e:
            code = getattr(e, "errno", None)
            print(f"  {label:<28}-> {type(e).__name__}" + (f" (errno {code})" if code else ""))


# ---------------------------------------------------------------- 7
def resource_accounting():
    header("7. RESOURCE ALLOCATION & ACCOUNTING")
    print(f"OS            : {platform.system()} {platform.release()}")
    print(f"CPU cores     : {os.cpu_count()} (allocated among processes by the OS)")
    t0, c0 = time.time(), time.process_time()
    sum(i * i for i in range(2_000_000))                 # burn some CPU
    print(f"Wall time     : {time.time() - t0:.3f} s")
    print(f"CPU time used : {time.process_time() - c0:.3f} s  (accounting)")
    try:
        import resource                                   # Unix only
        mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        print(f"Peak memory   : {mem} (ru_maxrss, from kernel accounting)")
    except ImportError:
        print("Peak memory   : (resource module not available on Windows)")


# ---------------------------------------------------------------- 8
def protection_security():
    header("8. PROTECTION & SECURITY")
    print("The OS controls who may read / write / execute each resource.")
    os.makedirs(SANDBOX, exist_ok=True)
    f = os.path.join(SANDBOX, "secret.txt")
    with open(f, "w") as fh:
        fh.write("confidential")
    os.chmod(f, 0o400)                                   # read-only for owner
    print("Permissions set to read-only (chmod 400)")
    print(f"  readable? {os.access(f, os.R_OK)} | writable? {os.access(f, os.W_OK)}")
    try:
        with open(f, "w") as fh:
            fh.write("hack")
        print("  Write allowed (e.g. running as administrator/root)")
    except PermissionError as e:
        print(f"  Write blocked -> PermissionError (errno {e.errno}) : protection works!")
    if hasattr(os, "getuid"):
        print(f"  Current user id = {os.getuid()}  (0 = root)")
    else:
        print(f"  Current user    = {os.environ.get('USERNAME', 'unknown')}")
    os.chmod(f, 0o600)
    os.remove(f)


# ---------------------------------------------------------------- registry
SERVICES = [
    {"id": "execution",  "title": "Program Execution",          "icon": "▶",  "desc": "Load, run and terminate programs (processes).",        "fn": program_execution},
    {"id": "files",      "title": "File-System Manipulation",   "icon": "📁", "desc": "Create, read, rename, copy and delete files.",         "fn": file_manipulation},
    {"id": "io",         "title": "I/O Operations",             "icon": "⌨",  "desc": "Access to screen, keyboard and storage devices.",      "fn": io_operations},
    {"id": "syscalls",   "title": "System Calls",               "icon": "⚙",  "desc": "open / read / write / close through the kernel.",      "fn": system_calls},
    {"id": "ipc",        "title": "Communication (IPC)",        "icon": "⇄",  "desc": "Processes exchange data using a pipe.",                "fn": communication},
    {"id": "errors",     "title": "Error Detection",            "icon": "⚠",  "desc": "OS detects and reports errors with codes.",            "fn": error_detection},
    {"id": "resources",  "title": "Resource Allocation",        "icon": "📊", "desc": "CPU, memory and time accounting.",                     "fn": resource_accounting},
    {"id": "security",   "title": "Protection & Security",      "icon": "🔒", "desc": "Permissions decide who can read or write.",            "fn": protection_security},
]


def cleanup():
    shutil.rmtree(SANDBOX, ignore_errors=True)
