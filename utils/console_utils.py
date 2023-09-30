from typing import List
from pick import pick

def start_choise_console(title: str, inputs: List[str], is_multi_choice: bool = False):
    return pick(inputs, title, multiselect=is_multi_choice)
        