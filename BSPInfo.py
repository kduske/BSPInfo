#!/usr/bin/python

import sys, io, struct

def check_usage():
	if len(sys.argv) != 2:
		print("Invalid arguments")
		sys.exit(1)

def read_bsp_header(file):
	struct.unpack("")

sizeof_short_t     = 2
sizeof_ushort_t    = 2
sizeof_long_t      = 4
sizeof_ulong_t     = 4
sizeof_float_t     = 4
sizeof_scalar_t    = sizeof_float_t
sizeof_vec3_t      = 3 * sizeof_scalar_t
sizeof_plane_t     = sizeof_vec3_t + sizeof_scalar_t + sizeof_long_t
sizeof_miptex_t    = 16 + 6 * sizeof_ulong_t
sizeof_bboxshort_t = 2 * sizeof_short_t
sizeof_node_t      = sizeof_long_t + 4 * sizeof_ushort_t + sizeof_bboxshort_t

def is_whitespace(str):
	return 1 in [c in str for c in " \n\r\t\v"]

def skip_whitespace(bsp):
	while is_whitespace(bsp.read(1)):
		pass
	bsp.seek(-1, 1)

def expect(bsp, exp, act):
	if act != exp:
		raise RuntimeError("Error while parsing entities: expected '{:s}', but got '{:s}' at offset {:d}".format(exp, act, bsp.tell()))

class dentry_t:
	offset = None
	size = None
	sizeof = 8

	def __init__(self, bsp):
		self.offset, self.size = struct.unpack("=ll", bsp.read(self.sizeof))

class entity_t:
	properties = []
	classname = "UNKNOWN"

	def __init__(self, bsp):
		skip_whitespace(bsp)
		expect(bsp, '{', bsp.read(1))
		skip_whitespace(bsp)
		while bsp.peek(1)[0] != '}':
			property_name, property_value = self.read_property(bsp)
			self.properties.append((property_name, property_value))
			if (property_name == "classname"):
				self.classname = property_value
		bsp.read(1)

	def read_property(self, bsp):
		expect(bsp, '"', bsp.peek(1)[0])
		name = self.read_string(bsp)
		skip_whitespace(bsp)

		expect(bsp, '"', bsp.peek(1)[0])
		value = self.read_string(bsp)
		skip_whitespace(bsp)

		return name, value

	def read_string(self, bsp):
		expect(bsp, '"', bsp.read(1))
		str = []
		ch = bsp.read(1)
		while ch != '"':
			str.append(ch)
			ch = bsp.read(1)
		return "".join(str)



class bsp_directory:
	entities = None
	planes = None
	
	def __init__(self, bsp):
		self.entities  = dentry_t(bsp)
		self.planes    = dentry_t(bsp)
		self.miptex    = dentry_t(bsp)
		self.vertices  = dentry_t(bsp)
		self.visilist  = dentry_t(bsp)
		self.nodes     = dentry_t(bsp)
		self.texinfo   = dentry_t(bsp)
		self.faces     = dentry_t(bsp)
		self.lightmaps = dentry_t(bsp)
		self.clipnodes = dentry_t(bsp)
		self.leaves    = dentry_t(bsp)
		self.lface     = dentry_t(bsp)
		self.edges     = dentry_t(bsp)
		self.ledges    = dentry_t(bsp)
		self.models    = dentry_t(bsp)

class bspinfo:
	version = None
	size = None
	directory = None
	entities = []
	entities_by_class = {}
	
	def __init__(self, path):
		bspfile = io.open(sys.argv[1], "rb")

		bspfile.seek(0, 2)
		self.size = bspfile.tell()

		bspfile.seek(0, 0)
		self.version   = struct.unpack("=l", bspfile.read(4))[0]
		self.directory = bsp_directory(bspfile)
		self.read_entities(bspfile)

	def read_entities(self, bsp):
		bsp.seek(self.directory.entities.offset, 0)
		skip_whitespace(bsp)
		while (bsp.tell() < self.directory.entities.offset + self.directory.entities.size - 1):
			entity = entity_t(bsp)
			self.entities.append(entity)
			if (entity.classname in self.entities_by_class):
				self.entities_by_class[entity.classname] += 1
			else:
				self.entities_by_class[entity.classname] = 1
			skip_whitespace(bsp)

	def num_entities(self):
		return len(self.entities)

	def num_planes(self):
		return self.directory.planes.size / sizeof_plane_t

	def num_miptex(self):
		return 0

	def num_vertices(self):
		return self.directory.vertices.size / sizeof_vec3_t

	def num_nodes(self):
		return self.directory.nodes.size / sizeof_node_t

def main():
	check_usage()

	bsp = bspinfo(sys.argv[0])

	print("Total BSP size        : {:d} bytes".format(bsp.size))
	print("BSP version           : {:d}".format(bsp.version))
	print("Number of entities    : {:d}".format(bsp.num_entities()))
	print("Number of planes      : {:d}".format(bsp.num_planes()))
	print("Number of mip textures: {:d}".format(bsp.num_miptex()))
	print("Number of vertices    : {:d}".format(bsp.num_vertices()))
	print("Number of nodes       : {:d}".format(bsp.num_nodes()))
	print("")
	print("==== Entity Stats ====")
	classnames = bsp.entities_by_class.keys()
	classnames.sort()
	for classname in classnames:
		print("  {:>4} {:s}".format(bsp.entities_by_class[classname], classname))
	# print("Number of textures: {:d}".format(num_miptex))

if __name__ == "__main__":
    main()