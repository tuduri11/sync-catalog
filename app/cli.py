import argparse
from .models.models import init_db
from .services.importer import *

def main():
    parser = argparse.ArgumentParser(prog="catalog-sync", description="Sincronización de catálogo")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("initdb", help="Crear tablas")

    p_imp = sub.add_parser("import", help="Importar feed CSV")
    p_imp.add_argument("csv_path")

    args = parser.parse_args()
    if args.cmd == "initdb":
        init_db()
    elif args.cmd == "import":
        import_feed(args.csv_path)

if __name__ == "__main__":
    main()