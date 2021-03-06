import os
from utils import *
import config
from arch_generic_helper import *

class arch_x86_helper(arch_generic_helper):
	"""
	Class for containing arch specific stuff for x86/x86_64
	"""
	registers = {
		8 : [ "al", "ah", "bl", "bh", "cl", "ch", "dl", "dh"],
		16: ["ax", "bx", "cx", "dx"],
		32: ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eip"],
		64: ["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "rip",
			"r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
}

	returnval_expr = None

	flags_register = "eflags"
	flags_names = {"carry": "CF", "parity": "PF", "adjust": "AF", "zero": "ZF", "sign": "SF",
			"trap": "TF", "interrupt": "IF", "direction": "DF", "overflow": "OF"}

	flag_CF = 1 << 0
	flag_PF = 1 << 2
	flag_AF = 1 << 4
	flag_ZF = 1 << 6
	flag_SF = 1 << 7
	flag_TF = 1 << 8
	flag_IF = 1 << 9
	flag_DF = 1 << 10
	flag_OF = 1 << 11

	conditions = {
			"o" : "OF",
			"no" : "not OF",
			"c" : "CF",		"b" : "CF",		"nae" : "CF",
			"nc" : "not CF",	"nb" : "not CF",	"ae" : "not CF",
			"e" : "ZF",		"z" : "ZF",
			"ne" : "not ZF",	"nz" : "not ZF",
			"be" : "CF or ZF",	"na" : "CF or ZF",
			"a" : "not CF and not ZF", "nbe" : "not CF and not ZF",
			"s" : "SF",
			"ns" : "not SF",
			"p" : "PF",		"pe" : "PF",
			"np": "not PF",		"po" : "not PF",
			"l" : "SF != OF",	"nge" : "SF != OF",
			"ge" : "SF == OF",	"nl" : "SF == OF",
			"le" : "ZF or (SF != OF)",	"ng" : "ZF or (SF != OF)",
			"g" : "not ZF and (SF == OF)" ,	"nle" : "not ZF and (SF == OF)",
		}

	compare_base = []
	call_base = []
	jump_base = ["j"]
	syscall_base = []


	compare_instrs = [ "test", "cmp"]
	call_instrs = [ "call"]
	jump_uncond = ["jmp"]
	jump_instrs = []
	return_regexes = ["ret"]
	syscall_instrs = ["sysenter", "int"]
	
	gdb_setup_cmds = [ "set disassembly-flavor intel" ]

	def __init__(self, archname, bitness):
		super(arch_x86_helper,self).__init__(archname, bitness)

	def gen_call_instrs(self):
		for cond in self.conditions.keys():
			for call in self.call_base:
				self.call_instrs.append(call + cond)
		

	def gen_jump_instrs(self):
		for cond in self.conditions.keys():
			for jump in self.jump_base:
				self.jump_instrs.append(jump + cond)
		for i in self.jump_uncond:
			self.jump_instrs.append(i)

	def gen_return_regexes(self):
		pass




	def get_cpuflags(self,val):
		flags = dict()
		for i in self.flags_names.values() :
			flags[i] = 0
                eflags = val
		if not eflags:
			return None
                flags["CF"] = bool(eflags & self.flag_CF)
                flags["PF"] = bool(eflags & self.flag_PF)
                flags["AF"] = bool(eflags & self.flag_AF)
                flags["ZF"] = bool(eflags & self.flag_ZF)
                flags["SF"] = bool(eflags & self.flag_SF)
                flags["TF"] = bool(eflags & self.flag_TF)
                flags["IF"] = bool(eflags & self.flag_IF)
                flags["DF"] = bool(eflags & self.flag_DF)
                flags["OF"] = bool(eflags & self.flag_OF)
		return flags

	def get_cpuflags_update_cmd(self, flagname, value, current_flags):
		if flagname not in self.flags_names.keys():
			return False

		if current_flags & eval("self.flag_%s" % self.flags_names[flagname]) == 0 and value == True:
	                current_flags ^= eval("self.flag_%s" % self.flags_names[flagname])

		if current_flags & eval("self.flag_%s" % self.flags_names[flagname]) != 0 and value == False:
	                current_flags ^= eval("self.flag_%s" % self.flags_names[flagname])

                cmd = "set $eflags = 0x%x" % current_flags
		return cmd


	def test_conditional(self, opcode, flags):

		if opcode == "jmp":
			return True

		for cond in self.conditions.keys():
			if opcode == "j" + cond:
				expr = self.conditions[cond]
				print "Eval-ing %s to %s" % (expr, eval(expr))
				return eval(expr)

	def get_returnval_expr(self):
		if "64" in self.archname:
			return "$rax"
		else:
			return "$eax"

if __name__ == "__main__":
	current_arch = arch_x86_helper("x86", 32)
	print current_arch.conditions
	print current_arch.get_register_list()

	print current_arch.get_register_altname("r15")
	
	print current_arch.get_compare_instrs()
	print current_arch.get_jump_instrs()
	print current_arch.get_call_instrs()
	print current_arch.get_return_regexes()
	print current_arch.get_syscall_instrs()
	print current_arch.get_returnval_expr()
