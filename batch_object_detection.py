import os
import argparse
import json
import numpy as np
from tqdm import tqdm

# Import detection functions from both implementations
try:
    from object_detection import detect_objects as torch_detect
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    
try:
    from cpu_mmdet_object_detection import detect_objects as mmdet_detect
    MMDET_AVAILABLE = True
except ImportError:
    MMDET_AVAILABLE = False

def process_images(input_dir, output_file, implementation='torch', threshold=0.5, device='cpu', extensions=('.jpg', '.jpeg', '.png')):
    """
    Process all images in a directory and save detection results to a JSON file.
    
    Args:
        input_dir (str): Directory containing images to process
        output_file (str): Path to save JSON results
        implementation (str): 'torch' or 'mmdet'
        threshold (float): Detection confidence threshold
        device (str): Device to run on ('cpu' or 'cuda:0')
        extensions (tuple): File extensions to process
    """
    # Select implementation
    if implementation == 'torch':
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch implementation not available. Make sure 'object_detection.py' is in the current directory.")
        detect_fn = torch_detect
    else:
        if not MMDET_AVAILABLE:
            raise ImportError("MMDetection implementation not available. Make sure 'cpu_mmdet_object_detection.py' is in the current directory.")
        detect_fn = lambda img_path: mmdet_detect(img_path, score_threshold=threshold, device=device)
    
    # Get list of image files
    image_files = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                image_files.append(os.path.join(root, file))
    
    results = {}
    print(f"Processing {len(image_files)} images using {implementation} implementation...")
    
    # Process each image
    for img_path in tqdm(image_files):
        try:
            detections = detect_fn(img_path)
            rel_path = os.path.relpath(img_path, input_dir)
            results[rel_path] = detections
        except Exception as e:
            print(f"Error processing {img_path}: {str(e)}")
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {output_file}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch object detection on multiple images')
    parser.add_argument('input_dir', help='Directory containing images to process')
    parser.add_argument('--output', default='detection_results.json', help='Output JSON file')
    parser.add_argument('--implementation', choices=['torch', 'mmdet'], default='torch', 
                      help='Detection implementation to use')
    parser.add_argument('--threshold', type=float, default=0.5, help='Detection confidence threshold')
    parser.add_argument('--device', choices=['cpu', 'cuda:0'], default='cpu', help='Device to run on')
    
    args = parser.parse_args()
    
    process_images(
        args.input_dir, 
        args.output, 
        implementation=args.implementation,
        threshold=args.threshold,
        device=args.device
    ) 