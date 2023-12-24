"""
Copyright (c) 2021, Ouster, Inc.
All rights reserved.

Executable examples for using the pcap APIs.

This module has a rudimentary command line interface. For usage, run::

		$ python -m ouster.sdk.examples.pcap -h
"""

import json
from ouster import client, pcap
from utils.file_utils import check_path_exists, join_paths, make_directory

def pcap_to_pcd(source: client.PacketSource,
								metadata: client.SensorInfo,
								num: int = 0,
								pcd_dir: str = ".",
								pcd_base: str = "pcd_out",
								pcd_ext: str = "pcd") -> None:
		"""
		Converts LiDAR data from a pcap file to Point Cloud Data (.pcd) files, one file per LiDAR scan.

		Parameters:
			source (client.PacketSource): The source pcap file containing LiDAR data.
			metadata (client.SensorInfo): Sensor information for the pcap file.
			num (int, optional): Number of scans to process. Default is 0, which processes all scans.
			pcd_dir (str, optional): Directory to place output .pcd files. Defaults to the current directory.
			pcd_base (str, optional): Base name for output .pcd files. Defaults to 'pcd_out'.
			pcd_ext (str, optional): File extension for output files. Defaults to 'pcd'.

		Returns:
			None: This function writes output directly to files and does not return any value.
		"""

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

		if not check_path_exists(pcd_dir):
				make_directory(pcd_dir)

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

				pcd_path = join_paths(pcd_dir, f'{pcd_base}_{idx:06d}.{pcd_ext}')
				print(f'write frame #{idx} to file: {pcd_path}')

				o3d.io.write_point_cloud(pcd_path, pcd)  # type: ignore

def pcap_to_ply(source: client.PacketSource,
								metadata: client.SensorInfo,
								num: int = 0,
								ply_dir: str = ".",
								ply_base: str = "ply_out",
								ply_ext: str = "ply") -> None:
		"""
		Converts LiDAR data from a pcap file to Polygon File Format (.ply) files, one file per LiDAR scan.

		This function internally calls pcap_to_pcd to perform the conversion, changing only the output file format to .ply.

		Parameters:
			source (client.PacketSource): The source pcap file containing LiDAR data.
			metadata (client.SensorInfo): Sensor information for the pcap file.
			num (int, optional): Number of scans to process. Default is 0, which processes all scans.
			ply_dir (str, optional): Directory to place output .ply files. Defaults to the current directory.
			ply_base (str, optional): Base name for output .ply files. Defaults to 'ply_out'.
			ply_ext (str, optional): File extension for output files. Defaults to 'ply'.

		Returns:
			None: This function writes output directly to files and does not return any value.
    	"""

		# Don't need to print warning about dual returns since this leverages pcap_to_pcd

		# We are reusing the same Open3d File IO function to write the PLY file out
		pcap_to_pcd(source,
								metadata,
								num=num,
								pcd_dir=ply_dir,
								pcd_base=ply_base,
								pcd_ext=ply_ext)