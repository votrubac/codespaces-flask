from data.game_info import Ship, TurnResult

test_ship2 = Ship({(0, 0), (0, 1)})
test_ship5 = Ship({(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)})

def test_ship_miss():
    assert test_ship2.turn(0, 5) == TurnResult.MISS

def test_ship_hit():
    assert test_ship2.turn(0, 0) == TurnResult.HIT

def test_ship_kill_type_2():
    assert test_ship2.turn(0, 0) == TurnResult.HIT
    assert test_ship2.turn(0, 1) == TurnResult.KILL

def test_ship_kill_type_5():
    assert test_ship5.turn(0, 0) == TurnResult.HIT
    assert test_ship5.turn(0, 1) == TurnResult.HIT
    assert test_ship5.turn(0, 2) == TurnResult.HIT
    assert test_ship5.turn(0, 3) == TurnResult.HIT
    assert test_ship5.turn(0, 4) == TurnResult.KILL