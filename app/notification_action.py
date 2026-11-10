from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.notifications import process_notification_action_argument


def main():
    for argument in sys.argv[1:]:
        if process_notification_action_argument(argument):
            return


if __name__ == "__main__":
    main()
