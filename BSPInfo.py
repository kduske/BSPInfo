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
sizeof_bbox_t      = 2 * sizeof_vec3_t
sizeof_plane_t     = sizeof_vec3_t + sizeof_scalar_t + sizeof_long_t
sizeof_miptex_t    = 16 + 6 * sizeof_ulong_t
sizeof_bboxshort_t = 2 * sizeof_short_t
sizeof_node_t      = sizeof_long_t + 4 * sizeof_ushort_t + sizeof_bboxshort_t
sizeof_surface_t   = 2 * sizeof_vec3_t + 2 * sizeof_scalar_t + 2 * sizeof_ulong_t
sizeof_model_t     = sizeof_bbox_t + sizeof_vec3_t + 7 * sizeof_long_t

def is_whitespace(str):
	return 1 in [c in str for c in " \n\r\t\v"]

def skip_whitespace(bsp):
	while is_whitespace(bsp.read(1)):
		pass
	bsp.seek(-1, 1)

def skip_comments(bsp):
	while bsp.peek(2)[:2] == "//":
		while bsp.read(1) != "\n":
			pass
		skip_whitespace(bsp)

def expect(bsp, exp, act):
	if act != exp:
		raise RuntimeError("Error while parsing entities: expected '{:s}', but got '{:s}' at offset {:d}".format(exp, act, bsp.tell()))

class vec3_t:
	x = 0.0
	y = 0.0
	z = 0.0

	def __init__(self, x = 0.0, y = 0.0, z = 0.0):
		self.x = x
		self.y = y
		self.z = z

	def parse(self, bsp):
		self.x, self.y, self.z = struct.unpack("=fff", bsp.read(sizeof_vec3_t))
		return self

	def min(self, vec):
		return vec3_t(min(self.x, vec.x), min(self.y, vec.y), min(self.z, vec.z))

	def max(self, vec):
		return vec3_t(max(self.x, vec.x), max(self.y, vec.y), max(self.z, vec.z))

	def __str__(self):
		return "({:g} {:g} {:g})".format(self.x, self.y, self.z)

	def __abs__(a):
		return vec3_t(abs(a.x), abs(a.y), abs(a.z))

	def __pos__(a):
		return vec3_t(+a.x, +a.y, +a.z)

	def __neg__(a):
		return vec3_t(-a.x, -a.y, -a.z)

	def __add__(a, b):
		return vec3_t(a.x + b.x, a.y + b.y, a.z + b.z)

	def __sub__(a, b):
		return vec3_t(a.x - b.x, a.y - b.y, a.z - b.z)

class bbox3_t:
	min = vec3_t()
	max = vec3_t()

	def __init__(self, min = vec3_t(), max = vec3_t()):
		self.min = min.min(max)
		self.max = max.max(min)

	def merge(self, vec):
		return bbox3_t(self.min.min(vec), self.max.max(vec))

	def size(self):
		return self.max - self.min

	def __str__(self):
		return "min{:s} max{:s} size{:s}".format(self.min, self.max, self.size())

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
		skip_comments(bsp)
		skip_comments(bsp)
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
	textures = []
	bounds = bbox3_t()
	
	def __init__(self, path):
		bspfile = io.open(sys.argv[1], "rb")

		bspfile.seek(0, 2)
		self.size = bspfile.tell()

		bspfile.seek(0, 0)
		self.version   = struct.unpack("=l", bspfile.read(4))[0]
		self.directory = bsp_directory(bspfile)
		self.read_entities(bspfile)
		self.read_textures(bspfile)
		self.read_texture_usage(bspfile)
		self.compute_bounds(bspfile)

	def read_entities(self, bsp):
		bsp.seek(self.directory.entities.offset, 0)
		skip_whitespace(bsp)
		while (bsp.tell() < self.directory.entities.offset + self.directory.entities.size - 1 and
			   bsp.peek()[0] != "\x00"):
			self.entities.append(entity_t(bsp))
			skip_whitespace(bsp)

	def read_textures(self, bsp):
		bsp.seek(self.directory.miptex.offset, 0)
		numtex = struct.unpack("=l", bsp.read(4))[0]
		offsets = []
		for i in range(numtex):
			offsets.append(struct.unpack("=l", bsp.read(4))[0])
		for o in offsets:
			bsp.seek(self.directory.miptex.offset + o, 0)
			texture_name = struct.unpack("=16s", bsp.read(16))[0]
			self.textures.append((texture_name, 0))

	def read_texture_usage(self, bsp):
		bsp.seek(self.directory.texinfo.offset, 0)
		for i in range(self.num_surfaces()):
			bsp.seek(sizeof_vec3_t + sizeof_scalar_t + sizeof_vec3_t + sizeof_scalar_t, 1)
			texture_index = struct.unpack("=L", bsp.read(4))[0]
			bsp.seek(sizeof_ulong_t, 1)
			self.textures[texture_index] = (self.textures[texture_index][0], self.textures[texture_index][1] + 1)


	def compute_bounds(self, bsp):
		bsp.seek(self.directory.vertices.offset, 0)
		if (bsp.tell() < self.directory.vertices.offset + self.directory.vertices.size):
			vertex = vec3_t().parse(bsp)
			self.bounds.min = vertex
			self.bounds.max = vertex
			
			while (bsp.tell() < self.directory.vertices.offset + self.directory.vertices.size):
				self.bounds = self.bounds.merge(vec3_t().parse(bsp))

	def num_entities(self):
		return len(self.entities)

	def num_planes(self):
		return self.directory.planes.size / sizeof_plane_t

	def num_miptex(self):
		return len(self.textures)

	def num_vertices(self):
		return self.directory.vertices.size / sizeof_vec3_t

	def num_nodes(self):
		return self.directory.nodes.size / sizeof_node_t

	def num_surfaces(self):
		return self.directory.texinfo.size / sizeof_surface_t

	def num_models(self):
		return self.directory.models.size / sizeof_model_t

	def entity_stats(self):
		stats = {}
		for entity in self.entities:
			if (entity.classname in stats):
				stats[entity.classname] += 1
			else:
				stats[entity.classname] = 1
		return stats

	def texture_stats(self):
		stats = {}
		for texturename, usage in self.textures:
			stats[texturename] = usage
		return stats

def main():
	check_usage()

	bsp = bspinfo(sys.argv[0])

	print("")
	print("==== General Information ====")
	print("Total BSP size        : {:d} bytes".format(bsp.size))
	print("BSP version           : {:d}".format(bsp.version))
	print("Number of entities    : {:d}".format(bsp.num_entities()))
	print("Number of planes      : {:d}".format(bsp.num_planes()))
	print("Number of mip textures: {:d}".format(bsp.num_miptex()))
	print("Number of surfaces    : {:d}".format(bsp.num_surfaces()))
	print("Number of vertices    : {:d}".format(bsp.num_vertices()))
	print("Number of nodes       : {:d}".format(bsp.num_nodes()))
	print("Number of models      : {:d}".format(bsp.num_nodes()))

	print("")
	print("==== Geometry ====")
	print("Total bounds          : {:s}".format(bsp.bounds))

	print("")
	print("==== Textures ====")
	texture_stats = bsp.texture_stats()
	texture_names = texture_stats.keys()
	texture_names.sort()
	for texture_name in texture_names:
		print("{:5} {:16s}".format(texture_stats[texture_name], texture_name))


	print("")
	print("==== Entities ====")
	entity_stats = bsp.entity_stats()
	classnames = entity_stats.keys()
	classnames.sort()
	for classname in classnames:
		print("{:5} {:s}".format(entity_stats[classname], classname))
	# print("Number of textures: {:d}".format(num_miptex))

if __name__ == "__main__":
    main()