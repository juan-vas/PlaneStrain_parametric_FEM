################## INPUT ######################
collection = ["MAT8,1004,9240.0,127300.0,0.021920,4830.0,3600.0,1.6e-9", 
              "dffg, fgerg, efgeg, efg",
              "grfgr, gegeg, gtgsg, egerg, ergerg"]

################## METHOD #####################
def format_nastran_line(collection: list) -> list:
    formatted_lines = []
    for element in collection:
        if element.startswith("$"): 
            formatted_lines.append(element + "\n")
            continue
    # Split exactly by commas
        parts = element.split(",")
        
        formatted_parts = []
        for part in parts:
            # Cut down to 7 characters maximum if it is too long
            trimmed = part[:7]
            # Pad with trailing spaces to ensure it is exactly 8 characters wide
            padded = trimmed.ljust(8)
            formatted_parts.append(padded)
            
        # Join everything back together with zero spaces or commas between fields
        formatted_line = "".join(formatted_parts) + "\n"
        formatted_lines.append(formatted_line) 
    return formatted_lines

############## OUTPUT ###################
result = format_nastran_line(collection)
print(result)