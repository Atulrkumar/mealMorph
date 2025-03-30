import numpy as np
import cv2
from mmdet.apis import init_detector, inference_detector
import mmcv

def detect_objects(image_path, config_file=None, checkpoint_file=None, score_threshold=0.5):
    """
    Detect objects in an image using MMDetection's pretrained Faster R-CNN model.
    
    Args:
        image_path (str): Path to the input image.
        config_file (str, optional): Path to config file. If None, uses a default Faster R-CNN.
        checkpoint_file (str, optional): Path to checkpoint file. If None, uses a default Faster R-CNN.
        score_threshold (float): Confidence score threshold.
        
    Returns:
        list: List of dictionaries containing detection results with format:
             [{'label': label_name, 'score': confidence_score, 'bbox': [x1, y1, x2, y2]}, ...]
    """
    # Use default Faster R-CNN model if not specified
    if config_file is None:
        config_file = 'configs/faster_rcnn/faster_rcnn_r50_fpn_1x_coco.py'
    if checkpoint_file is None:
        checkpoint_file = 'checkpoints/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth'

    # Initialize the detector
    model = init_detector(config_file, checkpoint_file, device='cuda:0')
    
    # Load the image
    image = mmcv.imread(image_path)
    
    # Perform inference
    result = inference_detector(model, image)
    
    # Process results
    if isinstance(result, tuple):
        bbox_result, segm_result = result
    else:
        bbox_result, segm_result = result, None
        
    # Get class names from the model
    class_names = model.CLASSES
    
    # Initialize list to store detection results
    detections = []
    
    # Process bounding box results
    for class_id, bboxes in enumerate(bbox_result):
        for bbox in bboxes:
            x1, y1, x2, y2, score = bbox.tolist()
            if score >= score_threshold:
                detections.append({
                    'label': class_names[class_id],
                    'score': float(score),
                    'bbox': [float(x1), float(y1), float(x2), float(y2)]
                })
    
    return detections

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        detections = detect_objects(image_path)
        
        # Print detection results
        print(f"Found {len(detections)} objects:")
        for i, detection in enumerate(detections):
            print(f"  {i+1}. {detection['label']} (confidence: {detection['score']:.2f})")
            print(f"     Box coordinates: {detection['bbox']}")
        
        # Also return as array
        print("\nDetection Array:")
        print(np.array(detections))
    else:
        print("Usage: python mmdet_object_detection.py <path_to_image>")
        print("\nNote: Before running, make sure to install MMDetection and download the model checkpoint:")
        print("pip install mmdet mmcv-full")
        print("mkdir -p checkpoints")
        print("wget -P checkpoints https://download.openmmlab.com/mmdetection/v2.0/faster_rcnn/faster_rcnn_r50_fpn_1x_coco/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth") 