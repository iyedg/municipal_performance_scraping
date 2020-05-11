from models import reset_db
from loaders import (
    load_governorates,
    load_municipalities,
    load_performance_criteria,
    load_evaluations,
)


def main():
    reset_db()
    load_governorates()
    load_municipalities()
    load_performance_criteria()
    load_evaluations()


if __name__ == "__main__":
    main()
