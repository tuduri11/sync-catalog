import argparse
from .models.models import init_db

def main():
    parser = argparse.ArgumentParser(prog="catalog-sync", description="Sincronización de catálogo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("initdb", help="Crear tablas")

    args = parser.parse_args()
    if args.cmd == "initdb":
        init_db()

if __name__ == "__main__":
    main()