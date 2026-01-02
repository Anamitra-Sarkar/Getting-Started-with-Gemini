"""Simple DB management helpers for Vaelis backend.

Usage:
  python backend/manage_db.py init   # initialize DB (creates tables)
  python backend/manage_db.py inspect # print list of tables
"""
import sys
from sqlmodel import SQLModel, create_engine
from .models import engine


def init():
    print("Initializing database and creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Done.")


def inspect():
    # sqlite: list tables
    try:
        with engine.connect() as conn:
            res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            rows = res.fetchall()
            print("Tables:")
            for r in rows:
                print(" - ", r[0])
    except Exception as e:
        print("Inspect failed:", e)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'init':
        init()
    elif cmd == 'inspect':
        inspect()
    else:
        print('Unknown command')
        sys.exit(2)
