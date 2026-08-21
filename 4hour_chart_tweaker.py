import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import os
import shutil
from pathlib import Path

INPUT_IMAGE = "aapl_4hour_cnn.png"
OUTPUT_DIR = "chart_variations"

def create_variations():
    print("=" * 60)
    print("Chart Variation Generator (CNN Training Augmentation)")
    print("=" * 60)
    
    # Clean output directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
        print(f"✓ Cleared existing {OUTPUT_DIR}/")
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    # Load original
    original = Image.open(INPUT_IMAGE).convert('RGB')
    orig_w, orig_h = original.size
    print(f"Original: {orig_w}x{orig_h}\n")
    
    var_idx = 0
    
    def save_variation(img, name):
        nonlocal var_idx
        var_idx += 1
        filename = f"var_{var_idx:02d}_{name}.png"
        img.save(f"{OUTPUT_DIR}/{filename}")
        print(f"  [{var_idx:02d}/50] {filename}")
    
    # 1-8: Horizontal stretch/compress (candle width changes)
    for scale in [0.6, 0.75, 0.85, 0.92, 1.08, 1.15, 1.25, 1.4]:
        new_w = int(orig_w * scale)
        img = original.resize((new_w, orig_h), Image.LANCZOS)
        if scale > 1:
            img = img.crop(((new_w - orig_w)//2, 0, (new_w + orig_w)//2, orig_h))
        else:
            bg = Image.new('RGB', (orig_w, orig_h), 'white')
            bg.paste(img, ((orig_w - new_w)//2, 0))
            img = bg
        save_variation(img, f"candle_width_x{str(scale).replace('.', '_')}")
    
    # 9-14: Vertical stretch/compress (candle height changes)
    for scale in [0.7, 0.85, 0.93, 1.07, 1.2, 1.4]:
        new_h = int(orig_h * scale)
        img = original.resize((orig_w, new_h), Image.LANCZOS)
        if scale > 1:
            img = img.crop((0, (new_h - orig_h)//2, orig_w, (new_h + orig_h)//2))
        else:
            bg = Image.new('RGB', (orig_w, orig_h), 'white')
            bg.paste(img, (0, (orig_h - new_h)//2))
            img = bg
        save_variation(img, f"candle_height_x{str(scale).replace('.', '_')}")
    
    # 15-22: Shift chart around on canvas
    for h, v, desc in [(-40, 0, 'left'), (40, 0, 'right'), (-20, 0, 'slight_left'), 
                        (20, 0, 'slight_right'), (0, -40, 'up'), (0, 40, 'down'), 
                        (0, -20, 'slight_up'), (0, 20, 'slight_down')]:
        bg = Image.new('RGB', (orig_w, orig_h), 'white')
        bg.paste(original, (h, v))
        save_variation(bg, f"shift_{desc}")
    
    # 23-30: Crop and zoom (different whitespace amounts)
    for crop_pct in [0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60]:
        crop_w = int(orig_w * crop_pct)
        crop_h = int(orig_h * crop_pct)
        left = (orig_w - crop_w) // 2
        top = (orig_h - crop_h) // 2
        img = original.crop((left, top, left + crop_w, top + crop_h))
        img = img.resize((orig_w, orig_h), Image.LANCZOS)
        save_variation(img, f"zoom_{str(crop_pct).replace('.', '_')}")
    
    # 31-35: Brightness variations
    for factor in [0.6, 0.8, 1.15, 1.3, 0.45]:
        enhancer = ImageEnhance.Brightness(original)
        img = enhancer.enhance(factor)
        save_variation(img, f"brightness_{str(factor).replace('.', '_')}")
    
    # 36-40: Contrast variations
    for factor in [0.6, 0.8, 1.2, 1.4, 0.4]:
        enhancer = ImageEnhance.Contrast(original)
        img = enhancer.enhance(factor)
        save_variation(img, f"contrast_{str(factor).replace('.', '_')}")
    
    # 41-44: Combo width+height stretch
    for h_scale, v_scale in [(0.9, 1.1), (0.8, 1.2), (1.1, 0.9), (1.2, 0.8)]:
        new_w = int(orig_w * h_scale)
        new_h = int(orig_h * v_scale)
        img = original.resize((new_w, new_h), Image.LANCZOS)
        bg = Image.new('RGB', (orig_w, orig_h), 'white')
        bg.paste(img, ((orig_w - new_w)//2, (orig_h - new_h)//2))
        save_variation(bg, f"combo_w{str(h_scale).replace('.', '_')}_h{str(v_scale).replace('.', '_')}")
    
    # 45-48: Right-side crop (narrower screens)
    for crop_pct in [0.95, 0.90, 0.85, 0.80]:
        new_w = int(orig_w * crop_pct)
        img = original.crop((0, 0, new_w, orig_h))
        img = img.resize((orig_w, orig_h), Image.LANCZOS)
        save_variation(img, f"narrow_{str(crop_pct).replace('.', '_')}")
    
    # 49-50: Top/bottom crop (less data shown)
    for crop_pct in [0.90, 0.80]:
        new_h = int(orig_h * crop_pct)
        img = original.crop((0, 0, orig_w, new_h))
        img = img.resize((orig_w, orig_h), Image.LANCZOS)
        save_variation(img, f"short_{str(crop_pct).replace('.', '_')}")
    
    # Save original for reference
    original.save(f"{OUTPUT_DIR}/original.png")
    
    print(f"\n{'='*60}")
    print(f"✓ Complete! {var_idx} variations + original in {OUTPUT_DIR}/")
    print(f"{'='*60}")

if __name__ == "__main__":
    create_variations()