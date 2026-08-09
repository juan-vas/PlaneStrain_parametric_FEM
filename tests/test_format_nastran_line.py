################## INPUT ######################
collection = ["GRID,1,0,0.0,0.0,0.0", 
              "dffg, fgerg, efgeg, efg",
              "grfgr, gegeg, gtgsg, egerg, ergerg"]

################## METHOD #####################
def format_nastran_line(collection: list) -> list:
    formatted_lines = []
    for element in collection:
    # Split exactly by commas
        parts = element.split(",")
        
        formatted_parts = []
        for part in parts:
            # Cut down to 8 characters maximum if it is too long
            trimmed = part[:8]
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