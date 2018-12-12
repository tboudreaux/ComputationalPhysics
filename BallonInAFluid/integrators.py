def rk4(f, y0, t, h, args):
    k1 = h*f(y0, t, args)
    k2 = h*f(y0+k1/2, t+(h/2), args)
    k3 = h*f(y0+k2/2, t+(h/2), args)
    k4 = h*f(y0+k3, t+h, args)
    return y0 + (k1/6)+(k2/3)+(k3/3)+(k4/6)

def rk2(f, y0, t, h, args):
    k1 = h*f(y0, t, args)
    k2 = h*f(y0 + (k1/2), t+(h/2), args)
    return y0 + k2

def euler(f, y0, t, h, args):
    return  y0 + f(y0, t, args)*h
