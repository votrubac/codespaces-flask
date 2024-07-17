from data.game_info import Ship, TurnResult

def test_ship_miss():
    ship = Ship(5, 0, 0, 90)

    res = ship.turn(0, 5)

    assert res == TurnResult.MISS

def test_ship_hit_90():
    ship = Ship(5, 0, 0, 90)

    res = ship.turn(0, 4)
    
    assert res == TurnResult.HIT

def test_ship_hit_0():
    ship = Ship(5, 0, 0, 0)

    res = ship.turn(4, 0)
    
    assert res == TurnResult.HIT

def test_ship_kill_type_2():
    ship = Ship(2, 0, 0, 0)

    res = ship.turn(0, 0)
    assert res == TurnResult.HIT    

    res = ship.turn(1, 0)
    assert res == TurnResult.KILL

def test_ship_kill_type_5():
    ship = Ship(5, 0, 0, 90)

    assert ship.turn(0, 0) == TurnResult.HIT
    assert ship.turn(0, 1) == TurnResult.HIT
    assert ship.turn(0, 2) == TurnResult.HIT
    assert ship.turn(0, 3) == TurnResult.HIT
    assert ship.turn(0, 4) == TurnResult.KILL