def menu(question, options, cancel=False):
    while True:
        c = 1
        print(question)
        if cancel:
            print("\t0: Cancel")
        for option in options:
            print("\t{0}: {1}".format(c,option))
            c += 1
        inp = input("?: ")
        try:
            choice = int(inp)
        except:
            continue
        if choice < 0 or choice > len(options):
            continue
        if choice == 0 and not cancel:
            continue
        break
    return choice - 1
