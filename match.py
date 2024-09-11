import csv
import logging
import optparse
import os
import re
import dedupe


output_file = "matches.csv"
settings_file = "matching_settings"
training_file = "matching_training.json"

left_file = "pa_preprocessed.csv"
right_file = "nb_preprocessed.csv"

def preProcess(column):

    column = re.sub("\n", " ", column)
    column = re.sub("-", "", column)
    column = re.sub("/", " ", column)
    column = re.sub("'", "", column)
    column = re.sub(",", "", column)
    column = re.sub(":", " ", column)
    column = re.sub("  +", " ", column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column:
        column = None
    return column


def readData(filename):
    """
    Read in our data from a CSV file and create a dictionary of records,
    where the key is a unique record ID.
    """

    data_d = {}

    with open(filename) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            clean_row = {k: preProcess(v) for (k, v) in row.items()}
            #if clean_row["price"]:
            #    clean_row["price"] = float(clean_row["price"][1:])
            data_d[filename + str(i)] = dict(clean_row)

    return data_d


if __name__ == "__main__":

    # ## Logging

    # dedupe uses Python logging to show or suppress verbose output. Added for convenience.
    # To enable verbose logging, run `python examples/csv_example/csv_example.py -v`
    optp = optparse.OptionParser()
    optp.add_option(
        "-v",
        "--verbose",
        dest="verbose",
        action="count",
        help="Increase verbosity (specify multiple times for more)",
    )
    (opts, args) = optp.parse_args()
    log_level = logging.WARNING
    if opts.verbose:
        if opts.verbose == 1:
            log_level = logging.INFO
        elif opts.verbose >= 2:
            log_level = logging.DEBUG
    logging.getLogger().setLevel(log_level)

    # ## Setup

    print("importing data ...")
    data_1 = readData(left_file)
    data_2 = readData(right_file)

    def descriptions():
        for dataset in (data_1, data_2):
            for record in dataset.values():
                yield record["email"]

    # ## Training

    if os.path.exists(settings_file):
        print("reading from", settings_file)
        with open(settings_file, "rb") as sf:
            linker = dedupe.StaticRecordLink(sf)

    else:
        # Define the fields the linker will pay attention to
        fields = [
            dedupe.variables.String("first_name"),
            dedupe.variables.String("middle_name"),
            dedupe.variables.String("last_name"),
            dedupe.variables.Exact("email"),
            dedupe.variables.Exact("email1"),
            dedupe.variables.Exact("email2"),
            dedupe.variables.Exact("email3"),
            dedupe.variables.Exact("email4"),
            dedupe.variables.Exact("phone_number"),
            dedupe.variables.Exact("mobile_number"),
            dedupe.variables.ShortString("primary_address1"),
            dedupe.variables.ShortString("primary_address2"),
            dedupe.variables.ShortString("primary_address3"),
            dedupe.variables.ShortString("primary_city"),
            dedupe.variables.ShortString("primary_county"),
            dedupe.variables.ShortString("primary_state"),
            dedupe.variables.Exact("primary_zip"),
            dedupe.variables.ShortString("primary_country_code"),
            dedupe.variables.Exact("sex"),
            dedupe.variables.Exact("born_at") # use DateTime type?
        ]

        # Create a new linker object and pass our data model to it.
        linker = dedupe.RecordLink(fields)

        # If we have training data saved from a previous run of linker,
        # look for it an load it in.
        # __Note:__ if you want to train from scratch, delete the training_file
        if os.path.exists(training_file):
            print("reading labeled examples from ", training_file)
            with open(training_file) as tf:
                linker.prepare_training(
                    data_1, data_2, training_file=tf, sample_size=15000
                )
        else:
            linker.prepare_training(data_1, data_2, sample_size=15000)

        # ## Active learning
        # Dedupe will find the next pair of records
        # it is least certain about and ask you to label them as matches
        # or not.
        # use 'y', 'n' and 'u' keys to flag duplicates
        # press 'f' when you are finished
        print("starting active labeling...")

        dedupe.console_label(linker)

        linker.train()

        # When finished, save our training away to disk
        with open(training_file, "w") as tf:
            linker.write_training(tf)

        # Save our weights and predicates to disk.  If the settings file
        # exists, we will skip all the training and learning next time we run
        # this file.
        with open(settings_file, "wb") as sf:
            linker.write_settings(sf)

    # ## Blocking

    # ## Clustering

    # Find the threshold that will maximize a weighted average of our
    # precision and recall.  When we set the recall weight to 2, we are
    # saying we care twice as much about recall as we do precision.
    #
    # If we had more data, we would not pass in all the blocked data into
    # this function but a representative sample.

    print("clustering...")
    linked_records = linker.join(data_1, data_2, 0.0)

    print("# duplicate sets", len(linked_records))
    # ## Writing Results

    # Write our original data back out to a CSV with a new column called
    # 'Cluster ID' which indicates which records refer to each other.

    cluster_membership = {}
    for cluster_id, (cluster, score) in enumerate(linked_records):
        for record_id in cluster:
            cluster_membership[record_id] = {
                "Cluster ID": cluster_id,
                "Link Score": score,
            }

    with open(output_file, "w") as f:

        header_unwritten = True

        for fileno, filename in enumerate((left_file, right_file)):
            with open(filename) as f_input:
                reader = csv.DictReader(f_input)

                if header_unwritten:

                    fieldnames = [
                        "Cluster ID",
                        "Link Score",
                        "source file",
                    ] + reader.fieldnames

                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    header_unwritten = False

                for row_id, row in enumerate(reader):

                    record_id = filename + str(row_id)
                    cluster_details = cluster_membership.get(record_id, {})
                    row["source file"] = fileno
                    row.update(cluster_details)

                    writer.writerow(row)