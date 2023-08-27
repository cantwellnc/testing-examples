# Task: write a string reversal algorithm


# (INTENTIONALLY FLAWED) first try (think new programmers)
def rev(input_str: str) -> str:
    return [input_str[i] for i in range(len(input_str) - 1, 0, -1)]
    # their story: give all the characters back, starting from the
    # end of the string, stepping by -1 to the beginning.
