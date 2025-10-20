## Core Systems Test
## Tests VFS, PooScript, and Kernel without 3D
extends Node

func _ready() -> void:
	print("=" .repeat(60))
	print("SPACECMD CORE SYSTEMS TEST")
	print("=" .repeat(60))

	test_vfs()
	test_pooscript()
	test_kernel()

	print("=" .repeat(60))
	print("ALL TESTS COMPLETE")
	print("=" .repeat(60))

	# Exit after tests
	get_tree().quit()

func test_vfs() -> void:
	print("\n[TEST 1: VFS]")

	var vfs = VFS.new()
	assert(vfs != null, "VFS should be created")
	print("✓ VFS created")

	# Check root exists
	var root = vfs.stat("/", VFS.ROOT_INO)
	assert(root != null, "Root directory should exist")
	assert(root.is_dir(), "Root should be a directory")
	print("✓ Root directory exists")

	# Create a directory
	var success = vfs.mkdir("/test", 0o755, 0, 0, VFS.ROOT_INO)
	assert(success, "mkdir should succeed")
	print("✓ Created /test directory")

	# Create a file
	var content = "Hello from VFS!".to_utf8_buffer()
	var inode = vfs.create_file("/test/hello.txt", 0o644, 0, 0, content, VFS.ROOT_INO)
	assert(inode != null, "File creation should succeed")
	print("✓ Created /test/hello.txt")

	# Read the file
	var read_content = vfs.read_file("/test/hello.txt", VFS.ROOT_INO)
	assert(read_content.get_string_from_utf8() == "Hello from VFS!", "File content should match")
	print("✓ Read file contents: ", read_content.get_string_from_utf8())

	# List directory
	var entries = vfs.list_dir("/test", VFS.ROOT_INO)
	assert(entries.size() > 0, "Directory should have entries")
	print("✓ Listed directory, found ", entries.size(), " entries")

	# Create device file
	vfs.register_device("test_device",
		func(size): return "Device data".to_utf8_buffer(),
		func(data): return data.size()
	)
	vfs.create_device("/dev/test", true, 0, 0, "test_device", VFS.ROOT_INO)
	var device_data = vfs.read_file("/dev/test", VFS.ROOT_INO)
	assert(device_data.get_string_from_utf8() == "Device data", "Device read should work")
	print("✓ Device file works: ", device_data.get_string_from_utf8())

	print("✅ VFS: ALL TESTS PASSED")

func test_pooscript() -> void:
	print("\n[TEST 2: PooScript]")

	var vfs = VFS.new()
	var pooscript = PooScript.new(vfs)
	assert(pooscript != null, "PooScript should be created")
	print("✓ PooScript created")

	# Create a simple script
	var script_content = """
print_poo("Hello from PooScript!")
var x = 10
var y = 20
print_poo("Sum: " + str(x + y))
return 0
""".to_utf8_buffer()

	vfs.create_file("/test_script.poo", 0o755, 0, 0, script_content, VFS.ROOT_INO)
	print("✓ Created test script")

	# Spawn the script
	var pid = pooscript.spawn("/test_script.poo", [], {}, 0, 1)
	assert(pid > 0, "Script should spawn successfully")
	print("✓ Spawned script with PID: ", pid)

	# Wait a bit for script to execute
	await get_tree().create_timer(0.5).timeout

	# Check process exists
	var process = pooscript.get_process(pid)
	assert(process != null, "Process should exist")
	print("✓ Process found in table")

	# List processes
	var ps_output = pooscript.ps()
	assert(ps_output.size() > 0, "Should have at least one process")
	print("✓ ps() returned ", ps_output.size(), " process(es)")
	for p in ps_output:
		print("  PID: ", p.pid, " CMD: ", p.cmd, " STATE: ", p.state)

	# Test kill
	var killed = pooscript.kill(pid, 15)
	assert(killed, "Kill should succeed")
	print("✓ Killed process ", pid)

	# Verify process is stopped
	process = pooscript.get_process(pid)
	assert(process.state == PooScript.ProcessState.STOPPED, "Process should be STOPPED")
	print("✓ Process state is STOPPED")

	print("✅ PooScript: ALL TESTS PASSED")

func test_kernel() -> void:
	print("\n[TEST 3: Kernel]")

	var vfs = VFS.new()
	var kernel = KernelInterface.new(vfs)
	assert(kernel != null, "Kernel should be created")
	print("✓ Kernel created")

	# Create test file
	var test_content = "Kernel test data".to_utf8_buffer()
	vfs.create_file("/kernel_test.txt", 0o644, 0, 0, test_content, VFS.ROOT_INO)

	var pid = 100  # Fake PID for testing

	# Test open
	var fd = kernel.sys_open(pid, "/kernel_test.txt", kernel.O_RDONLY)
	assert(fd >= 0, "sys_open should succeed")
	print("✓ Opened file with FD: ", fd)

	# Test read
	var data = kernel.sys_read(pid, fd, 1024)
	assert(data.get_string_from_utf8() == "Kernel test data", "Read should return correct data")
	print("✓ Read data: ", data.get_string_from_utf8())

	# Test close
	var close_result = kernel.sys_close(pid, fd)
	assert(close_result == 0, "Close should succeed")
	print("✓ Closed file")

	# Test write
	var new_content = "New data".to_utf8_buffer()
	var write_fd = kernel.sys_open(pid, "/kernel_test.txt", kernel.O_WRONLY)
	var bytes_written = kernel.sys_write(pid, write_fd, new_content)
	assert(bytes_written > 0, "Write should succeed")
	print("✓ Wrote ", bytes_written, " bytes")
	kernel.sys_close(pid, write_fd)

	# Verify write
	var verify_data = vfs.read_file("/kernel_test.txt", VFS.ROOT_INO)
	assert(verify_data.get_string_from_utf8() == "New data", "Write should modify file")
	print("✓ Verified written data: ", verify_data.get_string_from_utf8())

	# Test stat
	var stat_info = kernel.sys_stat(pid, "/kernel_test.txt")
	assert(stat_info.has("size"), "Stat should return size")
	print("✓ stat() returned size: ", stat_info.size)

	# Test mkdir
	var mkdir_result = kernel.sys_mkdir(pid, "/kernel_dir", 0o755)
	assert(mkdir_result == 0, "mkdir should succeed")
	print("✓ Created directory via kernel")

	# Test readdir
	var dir_contents = kernel.sys_readdir(pid, "/")
	assert(dir_contents.size() > 0, "readdir should return entries")
	print("✓ readdir() returned ", dir_contents.size(), " entries")

	print("✅ Kernel: ALL TESTS PASSED")
