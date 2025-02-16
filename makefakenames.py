import csv
import sys
from random import choice

import faker
from faker import Faker


def main(i: int) -> None:
    with open("fake_names.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["name", "address_1", "address_2"])
        fake = Faker()
        for _ in range(i):
            writer.writerow(
                [
                    fake.name(),
                    fake.street_address(),
                    f"{fake.city()}, {choice(['MA', 'NH', 'ME', 'Massachusetts', 'New Hampshire', 'Maine'])}  {fake.zipcode()}",
                ]
            )


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500)
