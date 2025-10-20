## VFS - Virtual File System
## Unix-like filesystem with inodes, directories, devices
## Each ship has its own isolated VFS instance
class_name VFS extends RefCounted

## File type constants (mode bits)
const S_IFMT: int = 0xF000    # File type mask
const S_IFREG: int = 0x8000   # Regular file
const S_IFDIR: int = 0x4000   # Directory
const S_IFCHR: int = 0x2000   # Character device
const S_IFBLK: int = 0x6000   # Block device
const S_IFLNK: int = 0xA000   # Symbolic link

## Permission bits
const S_IRWXU: int = 0x1C0      # User RWX
const S_IRUSR: int = 0x100      # User read
const S_IWUSR: int = 0x80      # User write
const S_IXUSR: int = 0x40      # User execute

## Inode class - represents a file system object
class Inode extends RefCounted:
	var ino: int = 0
	var mode: int = 0
	var uid: int = 0
	var gid: int = 0
	var size: int = 0
	var nlink: int = 1
	var content: Variant = null  # PackedByteArray for files, Dictionary for dirs
	var atime: float = 0.0
	var mtime: float = 0.0
	var ctime: float = 0.0
	var device_name: String = ""  # For device files

	func _init() -> void:
		var time_now = Time.get_unix_time_from_system()
		atime = time_now
		mtime = time_now
		ctime = time_now

	func is_file() -> bool:
		return (mode & S_IFMT) == S_IFREG

	func is_dir() -> bool:
		return (mode & S_IFMT) == S_IFDIR

	func is_device() -> bool:
		return (mode & S_IFMT) == S_IFCHR or (mode & S_IFMT) == S_IFBLK

	func is_symlink() -> bool:
		return (mode & S_IFMT) == S_IFLNK

	func can_read(uid_check: int, gid_check: int) -> bool:
		if uid_check == 0:  # Root can always read
			return true
		if uid_check == uid and (mode & S_IRUSR):
			return true
		# TODO: Group and other permissions
		return false

	func can_write(uid_check: int, gid_check: int) -> bool:
		if uid_check == 0:  # Root can always write
			return true
		if uid_check == uid and (mode & S_IWUSR):
			return true
		return false

# Inode storage
var inodes: Dictionary = {}  # int -> Inode
var next_ino: int = 1

# Device handlers - Callable[size: int] -> PackedByteArray (read)
#                  Callable[data: PackedByteArray] -> int (write)
var device_handlers: Dictionary = {}  # String -> {read: Callable, write: Callable}

# Root directory inode number
const ROOT_INO: int = 1

func _init() -> void:
	_create_root()
	_create_base_directories()

## Create root directory
func _create_root() -> void:
	var root: Inode = Inode.new()
	root.ino = 1
	root.mode = S_IFDIR | 0x1ED
	root.uid = 0
	root.gid = 0
	root.content = {".": 1, "..": 1}
	inodes[1] = root
	next_ino = 2

## Create base Unix directories
func _create_base_directories() -> void:
	var dirs = [
		"/bin",
		"/dev",
		"/dev/ship",
		"/etc",
		"/home",
		"/proc",
		"/proc/ship",
		"/root",
		"/sys",
		"/sys/ship",
		"/sys/ship/systems",
		"/sys/ship/crew",
		"/sys/ship/rooms",
		"/tmp",
		"/usr",
		"/usr/local",
		"/var",
	]

	for dir_path in dirs:
		mkdir(dir_path, 0x1ED, 0, 0, ROOT_INO)

## Resolve path to inode number
## Returns inode number or -1 if not found
func _resolve_path(path: String, cwd_ino: int = ROOT_INO) -> int:
	# Handle absolute vs relative paths
	var start_ino: int = ROOT_INO if path.begins_with("/") else cwd_ino

	# Split path into components
	var parts: PackedStringArray = path.split("/", false)
	if parts.is_empty():
		return start_ino

	var current_ino: int = start_ino

	for part in parts:
		var current_inode: Inode = inodes.get(current_ino)
		if not current_inode or not current_inode.is_dir():
			return -1

		var dir_entries: Dictionary = current_inode.content
		if not dir_entries.has(part):
			return -1

		current_ino = dir_entries[part]

	return current_ino

## Get path string from inode number (for debugging)
func _inode_to_path(ino: int, visited: Dictionary = {}) -> String:
	if ino == ROOT_INO:
		return "/"

	if visited.has(ino):
		return "???"

	visited[ino] = true

	# Search all directories for this inode
	for parent_ino in inodes:
		var parent_inode: Inode = inodes[parent_ino]
		if not parent_inode.is_dir():
			continue

		var entries: Dictionary = parent_inode.content
		for name in entries:
			if entries[name] == ino and name not in [".", ".."]:
				var parent_path = _inode_to_path(parent_ino, visited)
				if parent_path == "/":
					return "/" + name
				return parent_path + "/" + name

	return "???"

## stat - Get inode for path
func stat(path: String, cwd_ino: int = ROOT_INO) -> Inode:
	var ino = _resolve_path(path, cwd_ino)
	if ino < 0:
		return null
	return inodes.get(ino)

## path_exists - Check if path exists
func path_exists(path: String, cwd_ino: int = ROOT_INO) -> bool:
	return _resolve_path(path, cwd_ino) >= 0

## mkdir - Create directory
func mkdir(path: String, mode: int, uid: int, gid: int, cwd_ino: int = ROOT_INO) -> bool:
	# Split path into parent and name
	var parts = path.rsplit("/", true, 1)
	var parent_path = "/" if parts[0] == "" else parts[0]
	var dir_name = parts[-1] if parts.size() > 1 else path

	# Resolve parent directory
	var parent_ino = _resolve_path(parent_path, cwd_ino)
	if parent_ino < 0:
		push_error("mkdir: parent directory not found: " + parent_path)
		return false

	var parent_inode: Inode = inodes.get(parent_ino)
	if not parent_inode or not parent_inode.is_dir():
		push_error("mkdir: parent is not a directory")
		return false

	# Check if already exists
	var dir_entries: Dictionary = parent_inode.content
	if dir_entries.has(dir_name):
		push_error("mkdir: directory already exists: " + dir_name)
		return false

	# Create new directory inode
	var new_inode: Inode = Inode.new()
	new_inode.ino = next_ino
	next_ino += 1
	new_inode.mode = S_IFDIR | (mode & 0x1FF)
	new_inode.uid = uid
	new_inode.gid = gid
	new_inode.content = {
		".": new_inode.ino,
		"..": parent_ino
	}

	# Add to inode table
	inodes[new_inode.ino] = new_inode

	# Add to parent directory
	dir_entries[dir_name] = new_inode.ino
	parent_inode.nlink += 1

	return true

## create_file - Create a regular file
func create_file(path: String, mode: int, uid: int, gid: int, content: PackedByteArray, cwd_ino: int = ROOT_INO) -> Inode:
	# Split path into parent and name
	var parts = path.rsplit("/", true, 1)
	var parent_path = "/" if parts[0] == "" else parts[0]
	var file_name = parts[-1] if parts.size() > 1 else path

	# Resolve parent directory
	var parent_ino = _resolve_path(parent_path, cwd_ino)
	if parent_ino < 0:
		push_error("create_file: parent directory not found: " + parent_path)
		return null

	var parent_inode: Inode = inodes.get(parent_ino)
	if not parent_inode or not parent_inode.is_dir():
		push_error("create_file: parent is not a directory")
		return null

	# Check if already exists
	var dir_entries: Dictionary = parent_inode.content
	if dir_entries.has(file_name):
		push_error("create_file: file already exists: " + file_name)
		return null

	# Create new file inode
	var new_inode: Inode = Inode.new()
	new_inode.ino = next_ino
	next_ino += 1
	new_inode.mode = S_IFREG | (mode & 0x1FF)
	new_inode.uid = uid
	new_inode.gid = gid
	new_inode.content = content
	new_inode.size = content.size()

	# Add to inode table
	inodes[new_inode.ino] = new_inode

	# Add to parent directory
	dir_entries[file_name] = new_inode.ino

	return new_inode

## create_device - Create a device file
func create_device(path: String, char_device: bool, uid: int, gid: int, device_name: String, cwd_ino: int = ROOT_INO) -> bool:
	# Split path
	var parts = path.rsplit("/", true, 1)
	var parent_path = "/" if parts[0] == "" else parts[0]
	var dev_name = parts[-1] if parts.size() > 1 else path

	# Resolve parent
	var parent_ino = _resolve_path(parent_path, cwd_ino)
	if parent_ino < 0:
		return false

	var parent_inode: Inode = inodes.get(parent_ino)
	if not parent_inode or not parent_inode.is_dir():
		return false

	# Create device inode
	var new_inode: Inode = Inode.new()
	new_inode.ino = next_ino
	next_ino += 1
	new_inode.mode = (S_IFCHR if char_device else S_IFBLK) | 0x1B6
	new_inode.uid = uid
	new_inode.gid = gid
	new_inode.device_name = device_name
	new_inode.content = null  # Devices have no content

	inodes[new_inode.ino] = new_inode
	parent_inode.content[dev_name] = new_inode.ino

	return true

## read_file - Read file contents
func read_file(path: String, cwd_ino: int = ROOT_INO) -> PackedByteArray:
	var ino = _resolve_path(path, cwd_ino)
	if ino < 0:
		return PackedByteArray()

	var inode: Inode = inodes.get(ino)
	if not inode:
		return PackedByteArray()

	# Handle device files
	if inode.is_device():
		if device_handlers.has(inode.device_name):
			var handler = device_handlers[inode.device_name]
			if handler.has("read"):
				return handler.read.call(4096)
		return PackedByteArray()

	# Regular file
	if inode.is_file():
		inode.atime = Time.get_unix_time_from_system()
		return inode.content

	return PackedByteArray()

## write_file - Write to existing file
func write_file(path: String, content: PackedByteArray, cwd_ino: int = ROOT_INO) -> bool:
	var ino = _resolve_path(path, cwd_ino)
	if ino < 0:
		return false

	var inode: Inode = inodes.get(ino)
	if not inode:
		return false

	# Handle device files
	if inode.is_device():
		if device_handlers.has(inode.device_name):
			var handler = device_handlers[inode.device_name]
			if handler.has("write"):
				var bytes_written = handler.write.call(content)
				return bytes_written >= 0
		return false

	# Regular file
	if inode.is_file():
		inode.content = content
		inode.size = content.size()
		var time_now = Time.get_unix_time_from_system()
		inode.mtime = time_now
		inode.ctime = time_now
		return true

	return false

## list_dir - List directory contents
func list_dir(path: String, cwd_ino: int = ROOT_INO) -> Array:
	var ino = _resolve_path(path, cwd_ino)
	if ino < 0:
		return []

	var inode: Inode = inodes.get(ino)
	if not inode or not inode.is_dir():
		return []

	var result: Array = []
	var dir_entries: Dictionary = inode.content

	for name in dir_entries:
		var child_ino = dir_entries[name]
		result.append([name, child_ino])

	return result

## unlink - Remove file or empty directory
func unlink(path: String, cwd_ino: int = ROOT_INO) -> bool:
	# Split path
	var parts = path.rsplit("/", true, 1)
	var parent_path = "/" if parts[0] == "" else parts[0]
	var name = parts[-1] if parts.size() > 1 else path

	# Resolve parent
	var parent_ino = _resolve_path(parent_path, cwd_ino)
	if parent_ino < 0:
		return false

	var parent_inode: Inode = inodes.get(parent_ino)
	if not parent_inode or not parent_inode.is_dir():
		return false

	# Get target inode
	var dir_entries: Dictionary = parent_inode.content
	if not dir_entries.has(name):
		return false

	var target_ino = dir_entries[name]
	var target_inode: Inode = inodes.get(target_ino)

	# Can't unlink . or ..
	if name in [".", ".."]:
		return false

	# If directory, must be empty
	if target_inode.is_dir():
		var target_entries: Dictionary = target_inode.content
		if target_entries.size() > 2:  # More than just . and ..
			return false

	# Remove from parent
	dir_entries.erase(name)

	# Decrease link count
	target_inode.nlink -= 1

	# If no more links, remove inode
	if target_inode.nlink <= 0:
		inodes.erase(target_ino)

	return true

## Register device handler
func register_device(device_name: String, read_handler: Callable, write_handler: Callable) -> void:
	device_handlers[device_name] = {
		"read": read_handler,
		"write": write_handler
	}
