
def get_href_no_last_part(base_href: str):
    char_to_find = '/'

    # Use rfind() to get the index of the last occurrence of the character
    last_index = base_href.rfind(char_to_find)

    if last_index != -1:
        # Extract a substring from the start to a specific index (exclusive)
        index_to_extract_to = last_index
        substring = base_href[:index_to_extract_to]

        return substring
    
    raise Exception("Bad url")