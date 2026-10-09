# OS Services Dashboard (Flask Micro Project)

**Subject:** Operating System | **Author:** G. Vikas Kumar, B.Tech CSE (AI/ML), Sandip University, Nashik

## Aim
To demonstrate the services an operating system provides to programs and users, through a Flask web dashboard that executes real OS calls and shows the output live.

## Run
```
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 and click **Run** on any card, or **Run all services**.

## Structure
| File | Purpose |
|------|---------|
| `app.py` | Flask server: routes `/`, `/api/run/<id>`, `/api/run-all` |
| `services.py` | The 8 OS-service demos (Python `os`, `subprocess`, `shutil`, `multiprocessing`) |
| `templates/index.html` | Dashboard page (cards + JavaScript fetch) |
| `static/style.css` | Dark navy theme |

## OS services covered
Program execution, file-system manipulation, I/O operations, system calls, communication (IPC), error detection, resource allocation/accounting, protection and security.

## Reference
Silberschatz, Galvin, Gagne - *Operating System Concepts*, "Operating-System Services" and "System Calls".
