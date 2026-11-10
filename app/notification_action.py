import sys

from .notifications import process_notification_action_argument


def main():
    for argument in sys.argv[1:]:
        if process_notification_action_argument(argument):
            return


if __name__ == "__main__":
    main()
