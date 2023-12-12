from semseg import segment
from lidar_utils import readFile
from object_detection import detect_objects

def process_images_and_pcap(folder, frames, model, seg_model, progress_bar):
    # Stores object detections information as YOLO results objects
    object_results = []
    seg_image_paths = []
    # Process each frame, performing segmentation and object detection.
    for i, frame_name in enumerate(frames):
        # Segment and save masks to file.
        seg_path = segment(frame_name, folder, seg_model)
        seg_image_paths.append(seg_path)

        # Object detection on frames, return as object_results
        detection_results = detect_objects(frame_name, folder, model)
        object_results.append(detection_results[0])

        # Read Lidar 
        readFile(i)
        
        # Update progress bar
        progress_bar.update(current_count=i+1)
    
    return object_results, seg_image_paths
