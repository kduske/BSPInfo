#!/usr/bin/python

import sys, io, struct

def check_usage():
	if len(sys.argv) != 2:
		print("Invalid arguments")
		sys.exit(1)

def read_bsp_header(file):
	struct.unpack("")

def main():
	check_usage()
	bsp = io.open(sys.argv[1], "rb").read() # read file into array bsp
	
	version = struct.unpack("=l", bsp[:4])[0]

	dentry_t  = "=ll"
	sizeof_long     = 4
	sizeof_ulong    = 4
	sizeof_float    = 4
	sizeof_scalar   = sizeof_float
	sizeof_vec3     = 3 * sizeof_scalar
	sizeof_plane_t  = sizeof_vec3 + sizeof_scalar + sizeof_long
	sizeof_miptex_t = 16 + 6 * sizeof_ulong

	entities  = struct.unpack(dentry_t, bsp[  4: 12])
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

	num_planes = planes[1] / sizeof_plane_t
	num_miptex = miptex[1] / sizeof_miptex_t # this is wrong

	print("Total BSP size    : {:d} bytes".format(len(bsp)))
	print("Number of planes  : {:d}".format(num_planes))
	print("Number of textures: {:d}".format(num_miptex))

if __name__ == "__main__":
    main()