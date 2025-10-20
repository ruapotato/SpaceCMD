## Test suite for VFS
extends GutTest

func test_vfs_has_root():
	var vfs = VFS.new()
	var root_inode = vfs.inodes.get(1)
	assert_not_null(root_inode, "Root inode should exist")
	assert_true(root_inode.is_dir(), "Root should be a directory")

func test_mkdir():
	var vfs = VFS.new()
	var success = vfs.mkdir("/test", 0o755, 0, 0, 1)
	# assert_true(success, "mkdir should succeed")  # TODO: implement

# Add more tests...
