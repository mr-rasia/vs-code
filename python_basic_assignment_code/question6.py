import csv

def csv_to_table(file_name):
    rows = []

    # Read CSV file
    with open(file_name, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    # Find maximum width of each column
    col_widths = []
    for i in range(len(rows[0])):
        max_width = max(len(row[i]) for row in rows)
        col_widths.append(max_width)

    # Function to print border line
    def print_border():
        print("+", end="")
        for w in col_widths:
            print("-" * (w + 2) + "+", end="")
        print()

    # Function to print row
    def print_row(row):
        print("|", end="")
        for i, value in enumerate(row):
            print(" " + value.ljust(col_widths[i]) + " |", end="")
        print()

    # Print formatted table
    print_border()
    print_row(rows[0])  # Header
    print_border()

    for row in rows[1:]:
        print_row(row)

    print_border()


# Run the function
csv_to_table("data.csv")