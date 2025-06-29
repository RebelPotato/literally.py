import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DOCTEST = "uv run python -m doctest dok.py"
MAKE_DOC = 'uv run dok.py -m README.md -H index.html -c # -b """ """ dok.py'
MAKE_EXE = "uvx pyinstaller -F --paths=.venv\Lib\site-packages dok.py"


def run():
    """
    Run and catch exceptions from the dok.py script.
    """
    try:
        print(f"Running '{DOCTEST}'...")
        subprocess.run(
            DOCTEST.split(" "),
            check=True,
        )
        print(f"Running '{MAKE_DOC}'...")
        subprocess.run(
            MAKE_DOC.split(" "),
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running dok.py: {e}")


def watch():
    watched = ["dok.py", "dok.css", "template.html"]
    message = f"Watching {', '.join(watched)} for changes (Ctrl+C to stop)..."
    print(message)

    class LiterallyHandler(FileSystemEventHandler):
        def on_modified(self, event):
            for file in watched:
                if event.src_path.endswith(file):
                    print(f"{file} changed. Rebuilding...")
                    run()
                    print(message)
                    return

    # Initial run
    run()

    # Set up the file watcher
    event_handler = LiterallyHandler()
    observer = Observer()
    for file in watched:
        observer.schedule(
            event_handler,
            path=os.path.dirname(os.path.abspath(file)),
            recursive=False,
        )
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    if "-w" in sys.argv:
        watch()
    else:
        run()


if __name__ == "__main__":
    main()
