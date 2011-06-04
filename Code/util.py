def menu(question, options, cancel=False):
  while True:
    c = 0
    print question
    for option in options:
      print "\t{0}: {1}".format(c,option)
      c += 1
    if cancel:
      print "\t{0}: Cancel".format(c)
    inp = raw_input("?: ")
    max = len(options)
    if cancel: max += 1
    try:
      choice = int(inp)
    except:
      continue
    if choice < 0 or choice >= max:
      continue
    break
  if choice == c: choice = -1
  return choice
