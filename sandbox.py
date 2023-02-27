import concurrent.futures

def process_item(key, value):
    # Do some processing on the key-value pair
    new_key = key.upper()
    new_value = value.lower()
    return new_key, new_value

input_dict = {'key1': 'VALUE1', 'key2': 'VALUE2', 'key3': 'VALUE3', 'key4': 'VALUE4', 'key5': 'VALUE5'}

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = dict(executor.map(process_item, input_dict.items()))

# output_dict = dict(results)

print(results)
