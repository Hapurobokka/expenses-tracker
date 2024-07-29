import core

def validate_fields(fields: list):
    f = lambda x: len(x) != 0
    return all(f(x) for x in fields)

def add_slime(name, value, label):
    if not validate_fields([name, value]):
        label["text"] = "Both fields are required"
        return

    label["text"] = "Everything is alright"
