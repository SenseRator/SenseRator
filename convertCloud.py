"""
Copyright (c) 2021, Ouster, Inc.
All rights reserved.

Executable examples for using the pcap APIs.

This module has a rudimentary command line interface. For usage, run::

		$ python -m ouster.sdk.examples.pcap -h
"""
# RuntimeError: ftell error: errno 22 (line 64)

import os
import json
from ouster import client, pcap

# source: 	.pcap file
# metadata:	SensorInfo for .pcap
# num: 			Scan number
# pcd_dir: 	Directory to place .pcd
# pcd_base:	Base name for .pcd
# pcd_ext:	File extenstion

# Unpack .pcap to .pcd's
def pcap_to_pcd(source: client.PacketSource,
								metadata: client.SensorInfo,
								num: int = 0,
								pcd_dir: str = ".",
								pcd_base: str = "pcd_out",
								pcd_ext: str = "pcd") -> None:
		"Write scans from a pcap to pcd files (one per lidar scan)."

		metadata = client.SensorInfo(json.dumps(json.load(open(metadata, 'r'))))
		source = pcap.Pcap(source, metadata)

		if (metadata.format.udp_profile_lidar ==
						client.UDPProfileLidar.PROFILE_LIDAR_RNG19_RFL8_SIG16_NIR16_DUAL):
				print("Note: You've selected to convert a dual returns pcap. Second "
							"returns are ignored in this conversion by this example "
							"for clarity reasons.  You can modify the code as needed by "
							"accessing it through github or the SDK documentation.")

		from itertools import islice
		try:
				import open3d as o3d  # type: ignore
		except ModuleNotFoundError:
				print(
						"This example requires open3d, which may not be available on all "
						"platforms. Try running `pip3 install open3d` first.")
				exit(1)

		if not os.path.exists(pcd_dir):
				os.makedirs(pcd_dir)

		# precompute xyzlut to save computation in a loop
		xyzlut = client.XYZLut(metadata)

		# create an iterator of LidarScans from pcap and bound it if num is specified
		scans = iter(client.Scans(source))
		if num:
				scans = islice(scans, num)

		for idx, scan in enumerate(scans):

				xyz = xyzlut(scan.field(client.ChanField.RANGE))

				pcd = o3d.geometry.PointCloud()  # type: ignore

				pcd.points = o3d.utility.Vector3dVector(xyz.reshape(-1, 3))  # type: ignore

				pcd_path = os.path.join(pcd_dir, f'{pcd_base}_{idx:06d}.{pcd_ext}')
				print(f'write frame #{idx} to file: {pcd_path}')

				o3d.io.write_point_cloud(pcd_path, pcd)  # type: ignore

# Unpack .pcap to .ply's
def pcap_to_ply(source: client.PacketSource,
								metadata: client.SensorInfo,
								num: int = 0,
								ply_dir: str = ".",
								ply_base: str = "ply_out",
								ply_ext: str = "ply") -> None:
		"Write scans from a pcap to ply files (one per lidar scan)."

		# Don't need to print warning about dual returns since this leverages pcap_to_pcd

		# We are reusing the same Open3d File IO function to write the PLY file out
		pcap_to_pcd(source,
								metadata,
								num=num,
								pcd_dir=ply_dir,
								pcd_base=ply_base,
								pcd_ext=ply_ext)