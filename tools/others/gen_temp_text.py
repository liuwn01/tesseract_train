import argparse
import re
import os
import random

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process text with filters and sliding windows.")
    parser.add_argument("-sourcetxt", type=str, default="testdata-utf8.txt" ,required=False, help="Path to source text file.")
    parser.add_argument("-filtertxt", type=str, default="simsun.ttc.txt", help="Path to filter text file.")
    parser.add_argument("-slides", type=str, required=False, default="1,2,3,5,7,9,10,12", help="Comma-separated slide lengths, e.g., '1,2,3,4,5'")
    parser.add_argument("-leng", type=int, required=False, default="10000000", help="Length of text to generate.")
    parser.add_argument("-model", type=str, required=False, default="gb5", help="Model name to save results.")
    return parser.parse_args()
#return ''.join([char if char in filtertxt or char in '\r\n' or char in '\r' or char in '\n' else '' for char in sourcetxt])

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def filter_source_text(sourcetxt, filtertxt):
    # If no filtertxt is provided, return the original sourcetxt
    if not filtertxt:
        return sourcetxt
    # Keep characters in sourcetxt only if they are also in filtertxt or are line breaks/carriage returns
    return ''.join([char if char in filtertxt or char in '\r\n' or char in '\r' or char in '\n' else '' for char in sourcetxt])

def create_word_list(sourcetxt, slides):
    wordlist = []
    for line in sourcetxt:
        line = line.strip()  # Remove trailing newline/carriage return for easier handling
        if not line:  # Skip empty lines
            continue
        for slide in slides:
            pos = 0
            while pos + slide <= len(line):
                # Take `slide` characters starting from `pos`
                wordlist.append(line[pos:pos + slide])
                pos += 1  # Move one character over for sliding effect
    return list(set(wordlist))

def generate_random_strings(wordlist, count, min_length=10, max_length=20):
    random_strings = []
    for _ in range(count):
        current_string = ""
        while len(current_string) < random.randint(min_length, max_length):
            current_string += random.choice(wordlist)
        random_strings.append(current_string[:max_length])  # Trim if it exceeds max_length
    return random_strings

def main():
    args = parse_arguments()

    # Read the source text
    sourcetxt = read_file(args.sourcetxt)

    # Read the filter text if provided
    filtertxt = read_file(args.filtertxt) if args.filtertxt else None

    # Filter source text
    filtered_text = filter_source_text(sourcetxt, filtertxt)

    # Write filtered text to temp.txt
    with open('temp.txt', 'w', encoding='utf-8') as temp_file:
        temp_file.write(filtered_text)

    # Parse slides and generate word list
    slides = [int(x.strip()) for x in args.slides.split(',')]
    wordlist = create_word_list(filtered_text.splitlines(), slides)

    # Write the result to the model-specific output file
    output_file = f"{args.model}.wordlist"
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(wordlist))

    print(f"Word list generated and saved to {output_file}")

    # Generate random strings from wordlist
    random_strings = generate_random_strings(wordlist, args.leng)

    # Write the result to the model-specific output file
    output_file = f"{args.model}.txt"
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(random_strings))

    print(f"Random strings generated and saved to {output_file}")

if __name__ == '__main__':
    main()