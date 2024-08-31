import base64, io, os
import requests
from fastapi import FastAPI, UploadFile
from PIL import Image

print("Importing Transformers... ", end="")
from transformers import AutoProcessor, AutoModelForCausalLM 
print("done!\nImporting torch f32... ", end="")
from torch import float32
print("done!")

#workaround for unnecessary flash_attn requirement (https://huggingface.co/microsoft/Florence-2-base/discussions/4#6673ffb9436907f83a8aaf2d)
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports

def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    if not str(filename).endswith("modeling_florence2.py"):
        return get_imports(filename)
    imports = get_imports(filename)
    imports.remove("flash_attn")
    return imports

# Model params
device = "cpu"
torch_dtype = float32
model_path = "Florence-2-base"

# Load model
print("Loading model... ", end="")
with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports): #workaround for unnecessary flash_attn requirement (https://huggingface.co/microsoft/Florence-2-base/discussions/4#6673ffb9436907f83a8aaf2d)
    model = AutoModelForCausalLM.from_pretrained(model_path, attn_implementation="sdpa", torch_dtype=torch_dtype, trust_remote_code=True, device_map=device).to(device)
processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True, local_files_only=True)
print(f"done! Model is currently using {model.get_memory_footprint() * 1e-9} Gb of RAM")

def caption_img(img: Image):
    # Process image and caption prompt
    prompt = "<MORE_DETAILED_CAPTION>"
    inputs = processor(text=prompt, images=img, return_tensors="pt").to(device, torch_dtype)

    # Begin generation
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=1024,
        do_sample=False,
        num_beams=3,
    )
    
    # Decode and parse generation
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    parsed_answer = processor.post_process_generation(generated_text, task=prompt, image_size=(img.width, img.height))

    return parsed_answer[prompt]

app = FastAPI()
@app.post("/caption")
async def caption_route(img: UploadFile):
    # Convert image URI to bytes
    img = base64.b64decode((await img.read()).decode())
    
    # Open image as pillow object
    img = Image.open(io.BytesIO(img)).convert("RGB")
    
    # Caption!
    caption = caption_img(img)
    return {"caption": caption}
