extends Node

func _ready() -> void:
	print("Testing octal notation...")
	var test_octal = 0o755
	print("Octal 0o755 = ", test_octal)

	print("Testing class instantiation...")
	var vfs = VFS.new()
	print("VFS created: ", vfs != null)

	print("Test complete")
	get_tree().quit()
