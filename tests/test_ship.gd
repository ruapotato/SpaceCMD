## Test suite for Ship class
extends GutTest

func test_ship_creation():
	var ship = Ship.new("Nautilus", "Kestrel")
	assert_eq(ship.ship_name, "Nautilus")
	assert_eq(ship.hull, 30.0)
	assert_eq(ship.reactor_power, 8)

func test_ship_takes_damage():
	var ship = Ship.new("TestShip", "Test")
	ship.hull = 100.0
	ship.take_damage(25.0)
	assert_eq(ship.hull, 75.0, "Ship should have 75 hull after taking 25 damage")

# Add more tests...
