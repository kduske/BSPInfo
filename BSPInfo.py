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

class dentry_t:
	offset = None
	size = None
	sizeof = 8

	def __init__(self, bsp, offset):
		self.offset, self.size = struct.unpack("=ll", bsp[offset:offset + self.sizeof])

class bsp_directory:
	entities = None
	planes = None
	
	def __init__(self, bsp):
		self.entities  = dentry_t(bsp,   4)
		self.planes    = dentry_t(bsp,  12)
		self.miptex    = dentry_t(bsp,  20)
		self.vertices  = dentry_t(bsp,  28)
		self.visilist  = dentry_t(bsp,  36)
		self.nodes     = dentry_t(bsp,  44)
		self.texinfo   = dentry_t(bsp,  52)
		self.faces     = dentry_t(bsp,  60)
		self.lightmaps = dentry_t(bsp,  68)
		self.clipnodes = dentry_t(bsp,  76)
		self.leaves    = dentry_t(bsp,  84)
		self.lface     = dentry_t(bsp,  92)
		self.edges     = dentry_t(bsp, 100)
		self.ledges    = dentry_t(bsp, 108)
		self.models    = dentry_t(bsp, 116)

class bspinfo:
	version = None
	size = None
	directory = None
	
	def __init__(self, path):
		bspfile = io.open(sys.argv[1], "rb").read() # read file into array bsp
		self.version   = struct.unpack("=l", bspfile[:4])[0]
		self.size 	   = len(bspfile)
		self.directory = bsp_directory(bspfile)

	def num_entities(self):
		return 0

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

	'''	
	planes    = struct.unpack(dentry_t, bsp[ 12: 20])
	miptex    = struct.unpack(dentry_t, bsp[ 20: 28])
	vertices  = struct.unpack(dentry_t, bsp[ 28: 36])
	visilist  = struct.unpack(dentry_t, bsp[ 36: 44])
	nodes     = struct.unpack(dentry_t, bsp[ 44: 52])
	texinfo   = struct.unpack(dentry_t, bsp[ 52: 60])
	faces     = struct.unpack(dentry_t, bsp[ 60: 68])
	lightmaps = struct.unpack(dentry_t, bsp[ 68: 76])
	clipnodes = struct.unpack(dentry_t, bsp[ 76: 84])
	leaves    = struct.unpack(dentry_t, bsp[ 84: 92])
	lface     = struct.unpack(dentry_t, bsp[ 92:100])
	edges     = struct.unpack(dentry_t, bsp[100:108])
	ledges    = struct.unpack(dentry_t, bsp[108:116])
	models    = struct.unpack(dentry_t, bsp[116:124])
    '''
	# num_miptex = miptex[1] / sizeof_miptex_t # this is wrong

	print("Total BSP size        : {:d} bytes".format(bsp.size))
	print("Number of entities    : {:d}".format(bsp.num_entities()))
	print("Number of planes      : {:d}".format(bsp.num_planes()))
	print("Number of mip textures: {:d}".format(bsp.num_miptex()))
	print("Number of vertices    : {:d}".format(bsp.num_vertices()))
	print("Number of nodes       : {:d}".format(bsp.num_nodes()))
	# print("Number of textures: {:d}".format(num_miptex))

if __name__ == "__main__":
    main()