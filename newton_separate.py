def gcd (x,y):

    if x%y == 0:
        return y

    return gcd(y,x%y)

def check (deg,terms,x,y):

    check_saperate = 0

    reply = ""

    sum = 0
    root = x/y*(-1)

    for i4 in range (0,deg+1):
        sum += terms[i4]*root**i4
    if sum == 0:
        if x==1:
            reply += "(x+{})".format(y)
        else:
            reply += "({}x+{})".format(x,y)
        check_saperate += 1

    sum = 0
    root*=(-1)

    for i5 in range (0,deg+1):
        sum += terms[i5]*root**i4
    if sum == 0:
        if x==1:
            reply += "(x-{})".format(y)
        else:
            reply += "({}x-{})".format(x,y)
        check_saperate += 1
    
    return check_saperate, reply


def run_main(input_terms):
    #input_terms = input('Please input the terms of each degree, and saperate by commmas => ')
    terms_temp = input_terms.split(',')

    deg = len(terms_temp)-1

    can_it_separate = 0

    terms = []

    reply = ""

    for i1 in range (0,deg+1):
        terms.append(terms_temp[deg-i1])
        terms[i1] = int(terms[i1])

    print('=>')

    terms_constant = abs(terms[0])
    terms_highest = abs(terms[deg])

    for i2 in range (1,terms_highest+1):
        if terms_highest%i2 == 0:
            for i3 in range (1,terms_constant+1):
                if terms_constant%i3 == 0:
                    if gcd(i2,i3) == 1:
                        temp, reply_temp = check(deg,terms,i2,i3)
                        can_it_separate += temp
                        reply += reply_temp

    if can_it_separate == 0:
        print('Sorry, there is no result.')