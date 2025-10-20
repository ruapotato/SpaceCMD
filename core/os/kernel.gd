## Kernel - System call interface for PooScript processes
## Provides safe access to VFS, devices, and ship systems
class_name KernelInterface extends RefCounted

## VFS reference
var vfs: VFS

## File descriptor table (per-process)
## Format: {pid: {fd: {path: String, mode: int, offset: int}}}
var file_descriptors: Dictionary = {}
var next_fd: int = 3  # 0=stdin, 1=stdout, 2=stderr

## Open flags (matching Python/C)
const O_RDONLY: int = 0
const O_WRONLY: int = 1
const O_RDWR: int = 2
const O_CREAT: int = 0x100
const O_APPEND: int = 0x200
const O_TRUNC: int = 0x400

func _init(p_vfs: VFS) -> void:
	vfs = p_vfs

## sys_open - Open file and return file descriptor
func sys_open(pid: int, path: String, flags: int = O_RDONLY, mode: int = 0o644) -> int:
	# Ensure process has fd table
	if not file_descriptors.has(pid):
		file_descriptors[pid] = {
			0: {"path": "/dev/stdin", "mode": O_RDONLY, "offset": 0},
			1: {"path": "/dev/stdout", "mode": O_WRONLY, "offset": 0},
			2: {"path": "/dev/stderr", "mode": O_WRONLY, "offset": 0}
		}

	# Check if file exists
	var inode = vfs.stat(path, VFS.ROOT_INO)

	if not inode:
		# File doesn't exist
		if flags & O_CREAT:
			# Create new file
			inode = vfs.create_file(path, mode, 0, 0, PackedByteArray(), VFS.ROOT_INO)
			if not inode:
				return -1  # ENOENT
		else:
			return -1  # ENOENT

	# Allocate file descriptor
	var fd = next_fd
	next_fd += 1

	file_descriptors[pid][fd] = {
		"path": path,
		"mode": flags & 0x3,  # Extract R/W/RW bits
		"offset": 0 if not (flags & O_APPEND) else inode.size
	}

	return fd

## sys_read - Read from file descriptor
func sys_read(pid: int, fd: int, count: int) -> PackedByteArray:
	if not file_descriptors.has(pid) or not file_descriptors[pid].has(fd):
		return PackedByteArray()  # EBADF

	var fd_info = file_descriptors[pid][fd]
	var path = fd_info["path"]
	var offset = fd_info["offset"]

	# Read file content
	var content = vfs.read_file(path, VFS.ROOT_INO)
	if content.is_empty():
		return PackedByteArray()

	# Extract requested bytes from offset
	var end_pos = min(offset + count, content.size())
	var result = content.slice(offset, end_pos)

	# Update offset
	fd_info["offset"] = end_pos

	return result

## sys_write - Write to file descriptor
func sys_write(pid: int, fd: int, data: PackedByteArray) -> int:
	if not file_descriptors.has(pid) or not file_descriptors[pid].has(fd):
		return -1  # EBADF

	var fd_info = file_descriptors[pid][fd]
	var path = fd_info["path"]
	var mode = fd_info["mode"]

	if mode == O_RDONLY:
		return -1  # EACCES

	# For append mode or normal write
	if vfs.write_file(path, data, VFS.ROOT_INO):
		return data.size()
	else:
		return -1  # EIO

## sys_close - Close file descriptor
func sys_close(pid: int, fd: int) -> int:
	if not file_descriptors.has(pid) or not file_descriptors[pid].has(fd):
		return -1  # EBADF

	file_descriptors[pid].erase(fd)
	return 0

## sys_stat - Get file status
func sys_stat(pid: int, path: String) -> Dictionary:
	var inode = vfs.stat(path, VFS.ROOT_INO)
	if not inode:
		return {}

	return {
		"ino": inode.ino,
		"mode": inode.mode,
		"uid": inode.uid,
		"gid": inode.gid,
		"size": inode.size,
		"nlink": inode.nlink,
		"atime": inode.atime,
		"mtime": inode.mtime,
		"ctime": inode.ctime
	}

## sys_mkdir - Create directory
func sys_mkdir(pid: int, path: String, mode: int = 0o755) -> int:
	if vfs.mkdir(path, mode, 0, 0, VFS.ROOT_INO):
		return 0
	else:
		return -1  # EEXIST or ENOENT

## sys_unlink - Remove file/directory
func sys_unlink(pid: int, path: String) -> int:
	if vfs.unlink(path, VFS.ROOT_INO):
		return 0
	else:
		return -1  # ENOENT

## sys_readdir - Read directory contents
func sys_readdir(pid: int, path: String) -> Array:
	var entries = vfs.list_dir(path, VFS.ROOT_INO)
	var result: Array = []

	for entry in entries:
		result.append(entry[0])  # Just names

	return result

## sys_chdir - Change working directory (not implemented yet)
func sys_chdir(pid: int, path: String) -> int:
	# TODO: Track per-process CWD
	return 0

## sys_getcwd - Get current working directory
func sys_getcwd(pid: int) -> int:
	# TODO: Return CWD inode
	return VFS.ROOT_INO

## Cleanup process file descriptors
func cleanup_process(pid: int) -> void:
	if file_descriptors.has(pid):
		file_descriptors.erase(pid)
