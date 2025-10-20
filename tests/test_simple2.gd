extends Node

func _ready() -> void:
	print("Testing different numeric notations...")
	var test_decimal = 493  # 0o755 in decimal
	print("Decimal 493 (0o755) = ", test_decimal)

	var test_hex = 0x1ED  # 0o755 in hex
	print("Hex 0x1ED (0o755) = ", test_hex)

	print("Test complete")
	get_tree().quit()
