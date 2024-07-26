from data.game_info import Ship, ShipAndHits, TurnResult

test_ship2 = Ship(((0, 0), (0, 1)))
test_ship5 = Ship(((0, 0), (0, 1), (0, 2), (0, 3), (0, 4)))

def test_ship_miss():
    ship = ShipAndHits(test_ship2)

    res = ship.turn(0, 5)

    assert res == TurnResult.MISS

def test_ship_hit():
    ship = ShipAndHits(test_ship2)

    res = ship.turn(0, 0)
    
    assert res == TurnResult.HIT

def test_ship_kill_type_2():
    ship = ShipAndHits(test_ship2)

    res = ship.turn(0, 0)
    assert res == TurnResult.HIT

    res = ship.turn(0, 1)
    assert res == TurnResult.KILL

def test_ship_kill_type_5():
    ship = ShipAndHits(test_ship5)

    assert ship.turn(0, 0) == TurnResult.HIT
    assert ship.turn(0, 1) == TurnResult.HIT
    assert ship.turn(0, 2) == TurnResult.HIT
    assert ship.turn(0, 3) == TurnResult.HIT
    assert ship.turn(0, 4) == TurnResult.KILL