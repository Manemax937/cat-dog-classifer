import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from PIL import Image
import io

NUM_CLASSES  =2
CLASS_NAMES = ["cats","dogs"]
class_names = CLASS_NAMES

def create_model():

    model = resnet18(weights = ResNet18_Weights.DEFAULT)

    for param in model.parameters():
        param.requires_grad = False

    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, NUM_CLASSES)

    return model


def load_trained_model(model_path):
    model = create_model()

    checkpoint = torch.load(model_path, map_location="cpu")

    if isinstance(checkpoint,dict) and 'state_dict' in checkpoint:
        model.load_state_dict(checkpoint['state_dict'])
    elif isinstance(checkpoint,dict) and 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint)

    model.eval()
    return model


inference_transforms = transforms.Compose([
    transforms.Resize(size=(244,244)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def process_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))

    if image.mode != 'RGB':
        image = image.convert('RGB')
    input_tensor  =  inference_transforms(image)    
    input_batch = input_tensor.unsqueeze(0)

    return input_batch

def predict(model, image_bytes, class_names=None):
    
    input_batch = process_image(image_bytes)

    with torch.no_grad():
        outputs = model(input_batch)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence_score = probabilities[0].cpu().numpy().tolist()
        predicted_class_idx = int(torch.argmax(probabilities, dim=1).cpu().item())
        confidence = float(confidence_score[predicted_class_idx])

    result = {
        'predicted_class_idx': predicted_class_idx,
        'confidence': confidence,
        'probabilities': confidence_score  
    }    

    if class_names and len(class_names) > predicted_class_idx:
        result['predicted_class_name'] = class_names[predicted_class_idx]

    return result    