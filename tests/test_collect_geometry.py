############# INPUT ##############
collection = []

                

new_x = [2.0, 1.0, 2.0]
new_y = [3.3, 4.023, 9.342]



############ METHOD #############
def collect_geometry(new_x : list, new_y : list, collection : list):
    id = len(collection) + 1
    i = 0
    for element in new_x:
        entry = "GRID,%d,%.10g,%.10g,0.0"%(id, new_x[i], new_y[i])
        entry = format_nastran_line(entry) + "\n"
        collection.append(entry)
        id += 1
        i += 1

    return collection
def format_nastran_line(input_string: str) -> str:
    # Split exactly by commas
    parts = input_string.split(",")
    
    formatted_parts = []
    for part in parts:
        # Cut down to 8 characters maximum if it is too long
        trimmed = part[:8]
        # Pad with trailing spaces to ensure it is exactly 8 characters wide
        padded = trimmed.ljust(8)
        formatted_parts.append(padded)
        
    # Join everything back together with zero spaces or commas between fields
    return "".join(formatted_parts)
############ OUTPUT #############
output = collect_geometry(new_x, new_y, collection)
result = output
print(result)
