"""Reverse Engineering Module - Symbolic analysis of binaries"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from enum import Enum
import struct


class Architecture(Enum):
    """Supported architectures"""
    X86_64 = "x86_64"
    X86 = "x86"
    ARM64 = "arm64"
    ARM32 = "arm32"


class OperandType(Enum):
    """X86 operand types"""
    REGISTER = "register"
    IMMEDIATE = "immediate"
    MEMORY = "memory"
    LABEL = "label"


@dataclass
class Operand:
    """An instruction operand"""
    type: OperandType
    value: Any  # register name, immediate value, memory address, label
    size: int = 0  # in bits
    
    def __repr__(self):
        return f"{self.type.value}:{self.value}"


@dataclass
class Instruction:
    """A disassembled instruction"""
    address: int
    mnemonic: str
    operands: List[Operand] = field(default_factory=list)
    raw_bytes: bytes = field(default_factory=bytes)
    
    def __repr__(self):
        ops = ", ".join(str(o) for o in self.operands)
        return f"0x{self.address:08x}: {self.mnemonic} {ops}"


@dataclass
class BasicBlock:
    """A basic block of instructions"""
    start: int
    end: int
    instructions: List[Instruction] = field(default_factory=list)
    successors: List[int] = field(default_factory=list)  # addresses
    predecessors: List[int] = field(default_factory=list)
    
    def __repr__(self):
        return f"BasicBlock(0x{self.start:08x}-0x{self.end:08x}, {len(instructions)} instr)"


@dataclass
class Function:
    """A disambiguated function"""
    address: int
    name: str
    basic_blocks: List[BasicBlock] = field(default_factory=list)
    arguments: List[str] = field(default_factory=list)
    return_type: str = "unknown"
    calls: List[str] = field(default_factory=list)  # called function names
    
    def __repr__(self):
        return f"Function({self.name} @ 0x{self.address:08x})"


@dataclass
class CFGNode:
    """Control Flow Graph node"""
    address: int
    block: Optional[BasicBlock] = None
    edges: List[int] = field(default_factory=list)  # successor addresses


@dataclass
class SymbolicValue:
    """A symbolic value (for symbolic execution)"""
    expr: str  # symbolic expression
    concrete: Optional[Any] = None  # concrete value if known
    
    def __repr__(self):
        if self.concrete is not None:
            return f"{self.expr} (={self.concrete})"
        return self.expr


class Disassembler:
    """
    Simple disassembler for common architectures.
    
    Note: This is a simplified mock for demonstration.
    Real implementation would use capstone or radare2.
    """
    
    # Simple x86_64 instruction patterns (simplified)
    OPCODES = {
        0x90: ("nop", []),
        0x50: ("push", [OperandType.REGISTER]),  # push rax, etc
        0x58: ("pop", [OperandType.REGISTER]),
        0xb8: ("mov", [OperandType.REGISTER, OperandType.IMMEDIATE]),  # mov eax, imm32
        0x48: ("rex", []),  # REX prefix - needs more decoding
        0xc3: ("ret", []),
        0xe9: ("jmp", [OperandType.LABEL]),  # relative offset
        0x74: ("je", [OperandType.LABEL]),
        0x75: ("jne", [OperandType.LABEL]),
        0xe8: ("call", [OperandType.LABEL]),  # relative offset
    }
    
    def __init__(self, arch: Architecture = Architecture.X86_64):
        self.arch = arch
        self.functions: Dict[int, Function] = {}
    
    def disassemble_bytes(
        self, 
        data: bytes, 
        base_address: int = 0x1000
    ) -> List[Instruction]:
        """Disassemble bytes to instructions"""
        instructions = []
        offset = 0
        address = base_address
        
        while offset < len(data):
            # Simple single-byte lookup (very incomplete)
            opcode = data[offset]
            
            if opcode in self.OPCODES:
                mnem, operand_types = self.OPCODES[opcode]
                operands = []
                
                # Very simplified operand parsing
                if OperandType.IMMEDIATE in operand_types and offset + 4 <= len(data):
                    imm = struct.unpack("<I", data[offset+1:offset+5])[0]
                    operands.append(Operand(OperandType.IMMEDIATE, imm, 32))
                    offset += 4
                
                instructions.append(Instruction(
                    address=address,
                    mnemonic=mnem,
                    operands=operands,
                    raw_bytes=data[offset:offset+1]
                ))
            else:
                # Unknown opcode - skip
                instructions.append(Instruction(
                    address=address,
                    mnemonic="db",
                    operands=[Operand(OperandType.IMMEDIATE, hex(opcode), 8)]
                ))
            
            offset += 1
            address += 1
        
        return instructions
    
    def find_functions(self, instructions: List[Instruction]) -> List[Function]:
        """Identify functions in instruction stream"""
        functions = []
        current_func = None
        current_block = None
        
        for instr in instructions:
            # Simple heuristic: function prologues
            if instr.mnemonic == "push" and instr.operands:
                if not current_func:
                    current_func = Function(
                        address=instr.address,
                        name=f"sub_{instr.address:08x}"
                    )
                    current_block = BasicBlock(instr.address, instr.address)
            
            # Function end
            elif instr.mnemonic == "ret":
                if current_func and current_block:
                    current_block.end = instr.address
                    current_func.basic_blocks.append(current_block)
                    functions.append(current_func)
                    current_func = None
                    current_block = None
            
            # Track block
            if current_block:
                current_block.instructions.append(instr)
                
                # Branch = new block
                if instr.mnemonic.startswith("j"):
                    current_block.end = instr.address
                    current_func.basic_blocks.append(current_block)
                    current_block = BasicBlock(instr.address + 1, instr.address + 1)
        
        return functions


class CFGBuilder:
    """Build Control Flow Graph from disassembly"""
    
    def __init__(self):
        self.nodes: Dict[int, CFGNode] = {}
    
    def build(self, functions: List[Function]) -> Dict[int, CFGNode]:
        """Build CFG from functions"""
        for func in functions:
            for block in func.basic_blocks:
                node = CFGNode(block.start, block)
                
                # Add edges based on jumps/branches
                for instr in block.instructions:
                    if instr.mnemonic in ("jmp", "je", "jne", "ja", "jb"):
                        # Extract target from operand
                        for op in instr.operands:
                            if op.type == OperandType.LABEL or op.type == OperandType.IMMEDIATE:
                                target = op.value if isinstance(op.value, int) else 0
                                node.edges.append(target)
                
                self.nodes[block.start] = node
        
        return self.nodes
    
    def find_dominators(self, start: int) -> Dict[int, Set[int]]:
        """Find dominators for each node"""
        # Simplified - would use proper algorithm
        return {addr: {start} for addr in self.nodes}
    
    def find_loops(self) -> List[Tuple[int, int]]:
        """Detect natural loops"""
        loops = []
        
        for addr, node in self.nodes.items():
            # Back edge = potential loop
            for edge in node.edges:
                if edge <= addr:
                    loops.append((edge, addr))
        
        return loops


class SymbolicExecutor:
    """
    Symbolic execution engine for binary analysis.
    
    Tracks symbolic values instead of concrete ones.
    """
    
    def __init__(self):
        self.registers: Dict[str, SymbolicValue] = {}
        self.memory: Dict[int, SymbolicValue] = {}
        self.path_constraints: List[str] = []
        self.pc: int = 0
    
    def set_register(self, name: str, value: SymbolicValue) -> None:
        """Set symbolic value of register"""
        self.registers[name] = value
    
    def get_register(self, name: str) -> SymbolicValue:
        """Get symbolic value of register"""
        return self.registers.get(name, SymbolicValue(name, 0))
    
    def read_memory(self, address: int) -> SymbolicValue:
        """Read from memory"""
        return self.memory.get(address, SymbolicValue(f"mem[0x{address:x}]"))
    
    def write_memory(self, address: int, value: SymbolicValue) -> None:
        """Write to memory"""
        self.memory[address] = value
    
    def add_constraint(self, constraint: str) -> None:
        """Add path constraint"""
        self.path_constraints.append(constraint)
    
    def execute(self, instruction: Instruction) -> None:
        """Execute one instruction symbolically"""
        if instruction.mnemonic == "mov":
            # mov dest, src
            if len(instruction.operands) >= 2:
                dest = instruction.operands[0]
                src = instruction.operands[1]
                
                if dest.type == OperandType.REGISTER:
                    if src.type == OperandType.REGISTER:
                        self.set_register(dest.value, self.get_register(src.value))
                    elif src.type == OperandType.IMMEDIATE:
                        self.set_register(dest.value, SymbolicValue(str(src.value), src.value))
        
        elif instruction.mnemonic == "add":
            if len(instruction.operands) >= 2:
                dest = instruction.operands[0]
                src = instruction.operands[1]
                
                if dest.type == OperandType.REGISTER:
                    if src.type == OperandType.IMMEDIATE:
                        current = self.get_register(dest.value)
                        self.set_register(
                            dest.value,
                            SymbolicValue(f"({current.expr} + {src.value})")
                        )
        
        elif instruction.mnemonic == "cmp":
            # Compare - add constraint
            if len(instruction.operands) >= 2:
                left = instruction.operands[0]
                right = instruction.operands[1]
                
                if left.type == OperandType.REGISTER:
                    if right.type == OperandType.IMMEDIATE:
                        self.add_constraint(f"{left.value} == {right.value}")
    
    def __repr__(self):
        return f"SymbolicExecutor(registers={list(self.registers.keys())})"


class BinaryAnalyzer:
    """
    High-level binary analysis interface.
    """
    
    def __init__(self, arch: Architecture = Architecture.X86_64):
        self.arch = arch
        self.disasm = Disassembler(arch)
        self.cfg_builder = CFGBuilder()
        self.functions: Dict[int, Function] = {}
    
    def load_binary(self, data: bytes, base_address: int = 0x1000) -> None:
        """Load and disassemble binary"""
        instructions = self.disasm.disassemble_bytes(data, base_address)
        self.functions = {f.address: f for f in self.disasm.find_functions(instructions)}
    
    def analyze(self) -> Dict[str, Any]:
        """Run full analysis"""
        # Build CFG
        all_blocks = []
        for func in self.functions.values():
            all_blocks.extend(func.basic_blocks)
        
        cfg = self.cfg_builder.build(list(self.functions.values()))
        loops = self.cfg_builder.find_loops()
        
        return {
            "num_functions": len(self.functions),
            "num_blocks": len(all_blocks),
            "num_loops": len(loops),
            "loops": [(hex(s), hex(e)) for s, e in loops],
        }
    
    def find_crypto(self) -> List[str]:
        """Find potential cryptographic code"""
        crypto_signatures = [
            "aes", "sha", "md5", "rc4", "des",
            "encrypt", "decrypt", "cipher"
        ]
        
        findings = []
        for func in self.functions.values():
            name_lower = func.name.lower()
            if any(sig in name_lower for sig in crypto_signatures):
                findings.append(func.name)
        
        return findings
    
    def find_string_references(self, data: bytes, strings: List[str]) -> Dict[str, List[int]]:
        """Find references to strings in binary"""
        references = {s: [] for s in strings}
        
        for i, s in enumerate(strings):
            pattern = s.encode()
            offset = 0
            while True:
                pos = data.find(pattern, offset)
                if pos == -1:
                    break
                references[s].append(pos)
                offset = pos + 1
        
        return references
    
    def __repr__(self):
        return f"BinaryAnalyzer(arch={self.arch.value}, functions={len(self.functions)})"
