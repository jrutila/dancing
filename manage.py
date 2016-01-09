#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dancing.settings")
    os.environ.setdefault("DATABASE_URL", "sqlite:///dancing.sqlite")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
