def process_ids(file_path):
    with open(file_path, 'r') as file:
        ids = file.read().split(',')

    # Remove spaces
    ids = [id.strip() for id in ids]

    # Remove duplicates
    unique_ids = list(set(ids))

    # Print the results in one line separated by commas
    print(','.join(unique_ids))


if __name__ == "__main__":
    file_path = "C:/Users/#####/Documents/blacklist ids/blacklist_ids.txt"
    process_ids(file_path)
