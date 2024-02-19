import pandas as pd 
import csv

file_path_in = '../etl/data/articles.csv'
file_path_out = '../etl/data/articles_formatted.csv'

data = []
with open(file_path_in, "r") as f: 
    reader = csv.reader(f)
    header = next(reader)
    for row in reader: 
        data.append(row)

df = pd.DataFrame(data, columns=["title", "abstract", "paragraph", "pub_date"])


#df = pd.read_csv(file_path)

def find_nearest_space(text, midpoint):
    # Check if 'text' is a string and is not empty
    if isinstance(text, str) and text:
        left_index = text.rfind(' ', 0, midpoint)
        right_index = text.find(' ', midpoint)
        
        if left_index == -1 and right_index == -1:
            # If no spaces are found, return some default index or handle as needed
            return 0  # or midpoint, or any other logic you see fit
        elif left_index == -1:
            return right_index
        elif right_index == -1:
            return left_index
        else:
            return left_index if midpoint - left_index <= right_index - midpoint else right_index
    else:
        # Handle non-string or empty 'text' inputs here
        return 0  # Or whatever default index makes sense in your context


# Calculate the approximate midpoint index for each paragraph
midpoints = df['paragraph'].apply(lambda x: len(x) // 2 if isinstance(x, str) else 0)

# Find the nearest space before the midpoint for each paragraph
nearest_spaces = df.apply(lambda row: find_nearest_space(row['paragraph'], midpoints[row.name]), axis=1)

# Split the 'paragraph' column into two columns
df['sentence1'] = df.apply(lambda row: row['paragraph'][:nearest_spaces[row.name]] if isinstance(row['paragraph'], str) else '', axis=1)
df['sentence2'] = df.apply(lambda row: row['paragraph'][nearest_spaces[row.name]:] if isinstance(row['paragraph'], str) else '', axis=1)


num_rows = len(df)
# Print the number of rows with a message
print(f"Number of rows in csv file: {num_rows}")
df = df.drop_duplicates()
num_rows = len(df)
# Print the number of rows with a message
print(f"Number of rows without duplicates: {num_rows}")

# Convert 'pub_date' to datetime format
df['pub_date'] = pd.to_datetime(df['pub_date'])

# Define the cutoff date
cutoff_date = pd.Timestamp('2021-09-01', tz='UTC')

# Now you can perform the comparison without a TypeError
df = df[df['pub_date'] < cutoff_date]

num_rows = len(df)
# Print the number of rows with a message
print(f"Number of rows before 2021: {num_rows}")

# Define a function to check if the paragraph meets the removal criteria
def check_paragraph_criteria(paragraph):
    if pd.isnull(paragraph) or paragraph.strip() == "" or paragraph == "To the Editor: " or len(paragraph.split()) < 20:
        return False
    return True

# Apply the function to filter rows based on 'paragraph'
df = df[df['paragraph'].apply(check_paragraph_criteria)]
num_rows = len(df)
# Print the number of rows with a message
print(f"Number of rows filtered: {num_rows}")


df.to_csv(file_path_out, index=True)
