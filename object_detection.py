import torch
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights
from PIL import Image
import numpy as np

def detect_objects(image_path, score_threshold=0.7):
    """
    Detect objects in an image using a pretrained Faster R-CNN model.
    
    Args:
        image_path (str): Path to the input image.
        score_threshold (float): Confidence score threshold.
        
    Returns:
        list: List of dictionaries containing detection results with format:
             [{'label': label_name, 'score': confidence_score, 'box': [x1, y1, x2, y2]}, ...]
    """
    # Load the pretrained model
    weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
    model = fasterrcnn_resnet50_fpn_v2(weights=weights, box_score_thresh=score_threshold)
    model.eval()
    
    # Load and transform the image
    image = Image.open(image_path).convert("RGB")
    transform = weights.transforms()
    img_tensor = transform(image)
    
    # Perform inference
    with torch.no_grad():
        prediction = model([img_tensor])
    
    # Get the results
    boxes = prediction[0]['boxes'].cpu().numpy()
    scores = prediction[0]['scores'].cpu().numpy()
    labels = prediction[0]['labels'].cpu().numpy()
    
    # Convert to list of dictionaries
    results = []
    for box, score, label in zip(boxes, scores, labels):
        label_name = weights.meta["categories"][label]
        results.append({
            'label': label_name,
            'score': float(score),
            'box': box.tolist()  # [x1, y1, x2, y2]
        })
    
    return results

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
            print(f"     Box coordinates: {detection['box']}")
    else:
        print("Usage: python object_detection.py <path_to_image>") 