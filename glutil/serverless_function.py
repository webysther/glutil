from .partitioner import Partitioner
from .utils import print_batch_errors
import sys


def create_found_partitions(partitioner, dry_run=False):
    print(f"Running Partitioner for {partitioner.database}.{partitioner.table}")
    print(f"\tLooking for partitions in s3://{partitioner.bucket}/{partitioner.prefix}")

    found_partitions = set(partitioner.partitions_on_disk())
    existing_partitions = set(partitioner.existing_partitions())
    to_create = sorted(found_partitions - existing_partitions)

    print(f"\tFound {len(to_create)} new partitions to create")

    # break early
    if len(to_create) == 0:
        sys.exit(0)

    if len(to_create) <= 50:
        print("\t{}".format(", ".join(map(str, to_create))))

    if not dry_run:
        errors = partitioner.create_partitions(to_create)
        if errors:
            print_batch_errors(errors, action="create")
            sys.exit(1)


def handle(event, context):
    database = event["database"]
    table = event["table"]

    if "profile" in event:
        profile = event["profile"]
    else:
        profile = None

    partitioner = Partitioner(database, table, profile)
    create_found_partitions(partitioner)
