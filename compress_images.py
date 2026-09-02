#!/usr/bin/env python3
"""
Comprime todas as imagens da pasta imgs/ do site Studio Triz.
- Redimensiona para no máximo 1920px no lado maior (suficiente pra tela cheia).
- Reencoda como JPEG qualidade 78 (praticamente sem perda visível).
- Mantém .png só quando a imagem tem transparência real.
- Faz backup da pasta original antes de sobrescrever.

Uso:
    pip install Pillow --break-system-packages
    python3 compress_images.py /caminho/para/StudioTriz-main/imgs
"""
import sys, os, shutil
from PIL import Image

MAX_SIDE = 1920
JPEG_QUALITY = 78

def has_alpha(img):
    """True só se a imagem tem transparência de verdade (não apenas um canal alpha 100% opaco)."""
    if img.mode == "P" and "transparency" in img.info:
        return True
    if img.mode in ("RGBA", "LA"):
        alpha = img.split()[-1]
        lo, hi = alpha.getextrema()
        return lo < 255  # só é "transparência real" se algum pixel não for opaco
    return False

def compress_file(path):
    try:
        img = Image.open(path)
    except Exception as e:
        print(f"  [pulado] {path}: {e}")
        return 0, 0

    original_size = os.path.getsize(path)
    w, h = img.size
    scale = MAX_SIDE / max(w, h)
    if scale < 1:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    root, ext = os.path.splitext(path)

    if has_alpha(img):
        # mantém PNG (com transparência), mas otimizado
        img.save(path, format="PNG", optimize=True)
    else:
        img = img.convert("RGB")
        img.save(path, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)

    new_size = os.path.getsize(path)
    return original_size, new_size

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 compress_images.py /caminho/para/imgs")
        sys.exit(1)

    imgs_dir = sys.argv[1]
    backup_dir = imgs_dir.rstrip("/") + "_backup_original"

    if not os.path.exists(backup_dir):
        print(f"Fazendo backup em {backup_dir} ...")
        shutil.copytree(imgs_dir, backup_dir)
    else:
        print("Backup já existe, pulando essa etapa.")

    total_before = 0
    total_after = 0
    count = 0

    for dirpath, _, filenames in os.walk(imgs_dir):
        if backup_dir in dirpath:
            continue
        for fname in filenames:
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(dirpath, fname)
                before, after = compress_file(path)
                total_before += before
                total_after += after
                count += 1

    print(f"\n{count} imagens processadas.")
    print(f"Antes:  {total_before/1024/1024:.1f} MB")
    print(f"Depois: {total_after/1024/1024:.1f} MB")
    if total_before:
        print(f"Redução: {100*(1-total_after/total_before):.1f}%")
    print(f"\nOriginais preservados em: {backup_dir}")

if __name__ == "__main__":
    main()
