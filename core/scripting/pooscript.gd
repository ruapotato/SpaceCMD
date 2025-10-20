## PooScript - Ship scripting language interpreter
## Actually uses GDScript as the execution engine (PooScript looks like GDScript/Python)
## Manages scripts as processes with PIDs, killable for hacking gameplay
class_name PooScript extends RefCounted

## Process state
enum ProcessState {
	CREATED,    # Just created, not started
	RUNNING,    # Currently running
	SLEEPING,   # Sleep() called
	WAITING,    # Waiting for I/O
	STOPPED,    # Killed or stopped
	ZOMBIE      # Finished but not reaped
}

## Process class - represents a running PooScript
class Process extends RefCounted:
	var pid: int = 0
	var script_path: String = ""
	var script_content: String = ""
	var state: ProcessState = ProcessState.CREATED
	var exit_code: int = -1

	# Execution context
	var script_instance: GDScript = null
	var script_obj: RefCounted = null

	# I/O streams
	var stdout: PackedByteArray = PackedByteArray()
	var stderr: PackedByteArray = PackedByteArray()
	var stdin: PackedByteArray = PackedByteArray()

	# Execution time
	var start_time: float = 0.0
	var cpu_time: float = 0.0

	# Owner
	var uid: int = 0
	var gid: int = 0

	# Parent
	var ppid: int = 1

	# Sleep state
	var sleep_until: float = 0.0

	func _init(p_pid: int, p_path: String) -> void:
		pid = p_pid
		script_path = p_path
		start_time = Time.get_ticks_msec() / 1000.0

## Process table
var processes: Dictionary = {}  # int (PID) -> Process
var next_pid: int = 2  # PID 1 is init

## Kernel interface reference
var kernel_interface: KernelInterface = null

## VFS reference
var vfs: VFS = null

signal process_started(pid: int)
signal process_exited(pid: int, exit_code: int)
signal process_killed(pid: int)

func _init(p_vfs: VFS) -> void:
	vfs = p_vfs

## Set kernel interface for syscalls
func set_kernel(p_kernel: KernelInterface) -> void:
	kernel_interface = p_kernel

## Spawn a new PooScript process
## Returns PID or -1 on error
func spawn(script_path: String, args: Array = [], env: Dictionary = {}, uid: int = 0, ppid: int = 1) -> int:
	# Read script from VFS
	var script_content = vfs.read_file(script_path, VFS.ROOT_INO)
	if script_content.is_empty():
		push_error("spawn: script not found: " + script_path)
		return -1

	# Create process
	var process = Process.new(next_pid, script_path)
	process.script_content = script_content.get_string_from_utf8()
	process.uid = uid
	process.ppid = ppid
	process.state = ProcessState.CREATED

	var pid = next_pid
	next_pid += 1

	processes[pid] = process

	# Start execution (in background)
	_start_process(process, args, env)

	process_started.emit(pid)
	return pid

## Start a process execution
func _start_process(process: Process, args: Array, env: Dictionary) -> void:
	process.state = ProcessState.RUNNING

	# Parse script content
	var script = GDScript.new()
	script.source_code = _wrap_pooscript(process.script_content, process.pid, args, env)

	# Compile
	var err = script.reload()
	if err != OK:
		push_error("PooScript compile error for PID " + str(process.pid))
		process.state = ProcessState.ZOMBIE
		process.exit_code = 1
		process_exited.emit(process.pid, 1)
		return

	process.script_instance = script

	# Create instance and run
	var obj = script.new()
	if obj == null:
		push_error("PooScript instantiation failed for PID " + str(process.pid))
		process.state = ProcessState.ZOMBIE
		process.exit_code = 1
		process_exited.emit(process.pid, 1)
		return

	process.script_obj = obj

	# Execute main() if exists
	if obj.has_method("main"):
		# Run in deferred mode (non-blocking)
		var result = obj.call("main")
		if result is int:
			_finish_process(process, result)
		else:
			_finish_process(process, 0)
	else:
		# No main(), just finish
		_finish_process(process, 0)

## Wrap PooScript code with runtime environment
func _wrap_pooscript(code: String, pid: int, args: Array, env: Dictionary) -> String:
	var wrapped = """
extends RefCounted

# PooScript runtime environment
var pid: int = %d
var args: Array = %s
var env: Dictionary = %s
var vfs = null
var kernel = null

# Built-in functions
func print_poo(msg: String) -> void:
	print("[PID %d] " + msg)

func sleep(seconds: float) -> void:
	OS.delay_msec(int(seconds * 1000))

# User code
func main() -> int:
%s
	return 0
""" % [pid, str(args), str(env), _indent_code(code, 1)]

	return wrapped

## Indent code by N tabs
func _indent_code(code: String, tabs: int) -> String:
	var lines = code.split("\n")
	var indent = "\t".repeat(tabs)
	var result = ""
	for line in lines:
		result += indent + line + "\n"
	return result

## Kill a process
func kill(pid: int, signal: int = 15) -> bool:
	if not processes.has(pid):
		return false

	var process: Process = processes[pid]

	if process.state == ProcessState.STOPPED or process.state == ProcessState.ZOMBIE:
		return false

	# Stop execution
	process.state = ProcessState.STOPPED
	process.exit_code = 128 + signal

	# Clean up script instance
	if process.script_obj:
		process.script_obj = null
	if process.script_instance:
		process.script_instance = null

	process_killed.emit(pid)
	return true

## Finish process execution
func _finish_process(process: Process, exit_code: int) -> void:
	process.state = ProcessState.ZOMBIE
	process.exit_code = exit_code
	process_exited.emit(process.pid, exit_code)

## Get process info
func get_process(pid: int) -> Process:
	return processes.get(pid)

## List all processes
func list_processes() -> Array[Process]:
	var result: Array[Process] = []
	for pid in processes:
		result.append(processes[pid])
	return result

## Wait for process to finish
func wait(pid: int, timeout: float = -1.0) -> int:
	if not processes.has(pid):
		return -1

	var process: Process = processes[pid]
	var start_time = Time.get_ticks_msec() / 1000.0

	while process.state != ProcessState.ZOMBIE and process.state != ProcessState.STOPPED:
		if timeout > 0 and (Time.get_ticks_msec() / 1000.0 - start_time) > timeout:
			return -1  # Timeout
		OS.delay_msec(10)

	return process.exit_code

## Reap zombie process (remove from table)
func reap(pid: int) -> bool:
	if not processes.has(pid):
		return false

	var process: Process = processes[pid]
	if process.state != ProcessState.ZOMBIE:
		return false

	processes.erase(pid)
	return true

## Update all running processes
func update(delta: float) -> void:
	for pid in processes:
		var process: Process = processes[pid]

		if process.state == ProcessState.RUNNING:
			process.cpu_time += delta

		elif process.state == ProcessState.SLEEPING:
			if Time.get_ticks_msec() / 1000.0 >= process.sleep_until:
				process.state = ProcessState.RUNNING

## Get process list for ps command
func ps() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for pid in processes:
		var process: Process = processes[pid]
		result.append({
			"pid": process.pid,
			"ppid": process.ppid,
			"uid": process.uid,
			"state": ProcessState.keys()[process.state],
			"time": "%.1f" % process.cpu_time,
			"cmd": process.script_path
		})
	return result
