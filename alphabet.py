import itertools

uppercase = [chr(c) for c in range(ord('C'), ord('Z')+1)]
lowercase = [chr(c) for c in range(ord('c'), ord('z')+1)]
numbers   = [str(n) for n in range(0, 10)]
symbols   = list("!$")

base_chars = uppercase + lowercase + numbers + symbols

output_file = "C_only_wordlist.txt"

length = 6   # total length
prefix = "C"

with open(output_file, "w") as f:
    for combo in itertools.product(base_chars, repeat=length - 1):
        f.write(prefix + "".join(combo) + "\n")

