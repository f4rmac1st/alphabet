import random

def load_words(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

def generate_combinations(
    file1,
    file2,
    output_file,
    total=10000,
    separator="",
    capitalize=True
):
    list1 = load_words(file1)
    list2 = load_words(file2)

    with open(output_file, "w") as out:
        for i in range(total):
            w1 = random.choice(list1)
            w2 = random.choice(list2)

            if capitalize:
                w1 = w1.capitalize()
                w2 = w2.capitalize()

            num = f"{random.randint(0, 999):03d}"  # <-- ALWAYS 3 digits: 00-999

            combo = f"{w1}{separator}{w2}{separator}{num}"
            out.write(combo + "\n")

            if (i + 1) % 1000 == 0:
                print(f"Generated {i + 1} entries")

if __name__ == "__main__":
    generate_combinations(
        "adjectives.txt",
        "nouns.txt",
        "output.txt",
        total=5000000,
        separator="",
        capitalize=True
    )
