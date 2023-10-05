from gcd import gcd

def test_gcd():
    ax = 42
    bx = 30
    v = gcd(ax, bx)
    assert(v == 6)

def test_gcd2():
    ax = 6
    bx = 6
    v = gcd(ax, bx)
    assert(v == 6)
    
def test_gcd3():
    ax = 42
    bx = -30
    try:
        v = gcd(ax, bx)
        assert(False)
    except ArithmeticError as e:
        assert("Must be positive int." in str(e))
    except:
        assert(False)
    finally:
        assert(True)

