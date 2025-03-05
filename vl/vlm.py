import re 
import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
from config import max_pixels, min_pixels
import json

# 设置显存占用比例为 50%
torch.cuda.set_per_process_memory_fraction(0.5, device=0)  # 0.5表示50%显存


qwen_model = Qwen2_5_VLForConditionalGeneration.from_pretrained("/data/llm/models/Qwen2.5-VL-7B-Instruct", torch_dtype="auto", device_map="auto", offload_buffers=True)
processor = AutoProcessor.from_pretrained("/data/llm/models/Qwen2.5-VL-7B-Instruct", min_pixels=min_pixels, max_pixels=max_pixels)

def qwen2_vl(messages, json_pattern):
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[text],
                       images=image_inputs,
                       videos=video_inputs,
                       padding=True,
                       return_tensors="pt", )
    inputs = inputs.to("cuda")
    generated_ids = qwen_model.generate(**inputs, max_new_tokens=1024)
    generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
    output_text = processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True,
                                         clean_up_tokenization_spaces=False)

    matches = re.findall(json_pattern,output_text[0], re.DOTALL)
    print("AAA", matches)
    res = json.loads(matches[0])
    return res