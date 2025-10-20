## HackingSystem - Network-based combat
class_name HackingSystem extends RefCounted

enum ExploitType {
	BUFFER_OVERFLOW,
	SQL_INJECTION,
	ZERO_DAY,
	BACKDOOR,
	DOS,
	PRIVILEGE_ESCALATION
}

enum MalwareType {
	VIRUS,
	WORM,
	TROJAN,
	RANSOMWARE,
	ROOTKIT,
	LOGIC_BOMB
}

func scan_target(attacker: Ship, target: Ship) -> Array[String]:
	# TODO: Return vulnerabilities
	return []

func deploy_malware(target: Ship, malware_type: MalwareType) -> void:
	# TODO
	pass
