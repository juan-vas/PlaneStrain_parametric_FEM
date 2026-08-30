############ INPUT ##############
# 1) QI-8   : [45/0/-45/90]s
# 2) QI-16  : [45/0/-45/90/0/-45/0/45]s
# 3) ±45 sesgado (14): [45/0/-45/90/45/0/-45]s
# 4) 0° dominante (14): [0/45/-45/0/90/0/45]s
# 5) 90° reforzado (16): [45/0/90/0/-45/0/90/0]s
# 6) Spread-tow (16): [45/0/-45/90/-45/0/45/90]s


############ METHOD #############
def choose_laminate(choice):
    match choice:
        case 1:
            sequence = [45, 0, -45, 90]
        case 2:
            sequence = [45, 0, -45, 90, 0, -45, 0, 45]
        case 3:
            sequence = [45, 0, -45, 90, 45, 0, -45]
        case 4:
            sequence = [0, 45, -45, 0, 90, 0, 45]
        case 5:
            sequence = [45, 0, 90, 0, -45, 0, 90, 0]
        case 6: 
            sequence = [45, 0, -45, 90, -45, 0, 45, 90]

    sequence = sequence + sequence[::-1]
    return sequence



