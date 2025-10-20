extends SceneTree

func _init():
	print("=== MINIMAL TEST ===")
	print("Creating a ship...")

	var ship = Ship.new("Test", "TestClass")
	print("Ship created: %s" % ship.ship_name)

	print("Creating VFS...")
	var vfs = VFS.new()
	print("VFS created")

	print("=== TEST COMPLETE ===")
	quit(0)
