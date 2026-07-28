"""Central tool registry."""


TOOL_CATEGORIES = {
    "ai_image": {"name": "AI Image Tools", "icon": "🤖"},
    "image_edit": {"name": "Image Editing", "icon": "🖌️"},
    "image_util": {"name": "Image Utilities", "icon": "🛠️"},
    "video": {"name": "Video Tools", "icon": "🎬"},
    "design": {"name": "Design Maker", "icon": "🎨"},
    "utilities": {"name": "Utilities", "icon": "⚙️"},
}

TOOLS = [
    {"id": "ai_enhancer", "name": "AI Image Enhancer", "category": "ai_image", "icon": "✨",
     "description": "Auto-enhance sharpness, contrast and denoise", "accepted": ("image",), "batch": True,
     "settings": {"strength": {"type": "slider", "min": 0.1, "max": 3.0, "default": 1.0, "step": 0.1}}},
    {"id": "hd_enhancer", "name": "HD Image Enhancer", "category": "ai_image", "icon": "📺",
     "description": "Boost image to HD quality with stronger pipeline", "accepted": ("image",), "batch": True,
     "settings": {"strength": {"type": "slider", "min": 0.5, "max": 3.0, "default": 1.5, "step": 0.1}}},
    {"id": "upscale_4k", "name": "4K Image Upscaler", "category": "ai_image", "icon": "🔮",
     "description": "Upscale images to 4K resolution", "accepted": ("image",), "batch": True, "settings": {}},
    {"id": "upscale_8k", "name": "8K Image Upscaler", "category": "ai_image", "icon": "🌌",
     "description": "Upscale to ultra-high 8K quality", "accepted": ("image",), "batch": True, "settings": {}},
    {"id": "object_remover", "name": "Object Remover", "category": "ai_image", "icon": "🧹",
     "description": "Remove unwanted objects seamlessly", "accepted": ("image",), "batch": True, "settings": {}},
    {"id": "watermark_remover", "name": "Watermark Remover", "category": "ai_image", "icon": "💧",
     "description": "Remove watermarks while preserving quality", "accepted": ("image",), "batch": True, "settings": {}},
    {"id": "text_remover", "name": "Text Remover", "category": "ai_image", "icon": "🔤",
     "description": "Erase text overlays automatically", "accepted": ("image",), "batch": True, "settings": {}},

    {"id": "bg_blur", "name": "Background Blur", "category": "image_edit", "icon": "🌫️",
     "description": "Portrait bokeh blur effect", "accepted": ("image",), "batch": True,
     "settings": {"radius": {"type": "slider", "min": 1, "max": 50, "default": 15, "step": 1}}},
    {"id": "bg_color_changer", "name": "Background Color Changer", "category": "image_edit", "icon": "🎨",
     "description": "Replace background colors", "accepted": ("image",), "batch": True,
     "settings": {"new_color": {"type": "color", "default": "#ffffff"},
                  "tolerance": {"type": "slider", "min": 5, "max": 100, "default": 30, "step": 1}}},
    {"id": "face_retouch", "name": "Face Retouch", "category": "image_edit", "icon": "👤",
     "description": "Smooth skin and enhance facial features", "accepted": ("image",), "batch": True, "settings": {}},
    {"id": "portrait_enhance", "name": "Portrait Enhancer", "category": "image_edit", "icon": "📸",
     "description": "Improve portrait lighting and details", "accepted": ("image",), "batch": True, "settings": {}},
    {"id": "skin_smooth", "name": "Skin Smoothing", "category": "image_edit", "icon": "🪞",
     "description": "Natural skin smoothing", "accepted": ("image",), "batch": True,
     "settings": {"strength": {"type": "slider", "min": 0.0, "max": 1.0, "default": 0.5, "step": 0.05}}},
    {"id": "teeth_whiten", "name": "Teeth Whitening", "category": "image_edit", "icon": "😁",
     "description": "Brighten teeth digitally", "accepted": ("image",), "batch": True, "settings": {}},
    {"id": "eye_enhance", "name": "Eye Enhancement", "category": "image_edit", "icon": "👁️",
     "description": "Sharpen and brighten eyes", "accepted": ("image",), "batch": True, "settings": {}},
    {"id": "ai_relight", "name": "AI Relight", "category": "image_edit", "icon": "💡",
     "description": "Adjust lighting direction", "accepted": ("image",), "batch": True,
     "settings": {"direction": {"type": "select", "options": ["center", "top", "bottom", "left", "right"], "default": "center"},
                  "intensity": {"type": "slider", "min": 0.1, "max": 3.0, "default": 1.0, "step": 0.1}}},
    {"id": "shadow_gen", "name": "Shadow Generator", "category": "image_edit", "icon": "🌑",
     "description": "Add realistic drop shadows", "accepted": ("image",), "batch": True,
     "settings": {"direction": {"type": "select", "options": ["bottom-right", "bottom-left", "top-right", "top-left"], "default": "bottom-right"},
                  "opacity": {"type": "slider", "min": 0.05, "max": 1.0, "default": 0.3, "step": 0.05}}},
    {"id": "reflection_gen", "name": "Reflection Generator", "category": "image_edit", "icon": "🪞",
     "description": "Create mirror reflections", "accepted": ("image",), "batch": True,
     "settings": {"opacity": {"type": "slider", "min": 0.05, "max": 1.0, "default": 0.4, "step": 0.05}}},

    {"id": "cropper", "name": "Image Cropper", "category": "image_util", "icon": "✂️",
     "description": "Crop with social media presets", "accepted": ("image",), "batch": True,
     "settings": {"preset": {"type": "select", "options": ["Custom", "Instagram (1:1)", "Story (9:16)", "YouTube (16:9)"], "default": "Custom"},
                  "left": {"type": "number", "min": 0, "default": 0}, "top": {"type": "number", "min": 0, "default": 0},
                  "right": {"type": "number", "min": 100, "default": 400}, "bottom": {"type": "number", "min": 100, "default": 400}}},
    {"id": "resizer", "name": "Image Resizer", "category": "image_util", "icon": "📐",
     "description": "Resize maintaining aspect ratio", "accepted": ("image",), "batch": True,
     "settings": {"width": {"type": "number", "min": 1, "default": 800}, "height": {"type": "number", "min": 1, "default": 600},
                  "maintain_aspect": {"type": "checkbox", "default": True}}},
    {"id": "rotator", "name": "Image Rotator", "category": "image_util", "icon": "🔄",
     "description": "Rotate by any angle", "accepted": ("image",), "batch": True,
     "settings": {"angle": {"type": "slider", "min": -180, "max": 180, "default": 0, "step": 1}}},
    {"id": "flipper", "name": "Image Flipper", "category": "image_util", "icon": "↔️",
     "description": "Flip horizontal or vertical", "accepted": ("image",), "batch": True,
     "settings": {"direction": {"type": "radio", "options": ["horizontal", "vertical"], "default": "horizontal"}}},
    {"id": "compressor", "name": "Image Compressor", "category": "image_util", "icon": "📦",
     "description": "Reduce file size efficiently", "accepted": ("image",), "batch": True,
     "settings": {"quality": {"type": "slider", "min": 1, "max": 100, "default": 85, "step": 1},
                  "format": {"type": "select", "options": ["JPEG", "PNG", "WEBP"], "default": "JPEG"}}},
    {"id": "batch_processor", "name": "Batch Processor", "category": "image_util", "icon": "📋",
     "description": "Process multiple images at once", "accepted": ("image",), "batch": True,
     "settings": {"operation": {"type": "select", "options": ["Enhance", "Upscale 2x", "Resize", "Compress"], "default": "Enhance"}}},

    {"id": "video_enhance", "name": "Video Enhancer", "category": "video", "icon": "🎥",
     "description": "Sharpen and denoise video", "accepted": ("video",), "batch": False,
     "settings": {"quality": {"type": "slider", "min": 1, "max": 5, "default": 2, "step": 1}}},
    {"id": "video_upscale", "name": "Video Upscaler", "category": "video", "icon": "📺",
     "description": "Upscale to HD/4K", "accepted": ("video",), "batch": False,
     "settings": {"scale": {"type": "select", "options": ["2", "3", "4"], "default": "2"}}},
    {"id": "video_bg_remove", "name": "Video BG Remover", "category": "video", "icon": "🎬",
     "description": "Remove video backgrounds", "accepted": ("video",), "batch": False, "settings": {}},
    {"id": "video_compress", "name": "Video Compressor", "category": "video", "icon": "📦",
     "description": "Reduce video file size", "accepted": ("video",), "batch": False,
     "settings": {"crf": {"type": "slider", "min": 1, "max": 51, "default": 23, "step": 1}}},
    {"id": "video_trim", "name": "Video Trimmer", "category": "video", "icon": "⏱️",
     "description": "Cut video segments", "accepted": ("video",), "batch": False,
     "settings": {"start_time": {"type": "number", "min": 0.0, "default": 0.0, "step": 0.1},
                  "end_time": {"type": "number", "min": 0.1, "default": 5.0, "step": 0.1}}},
    {"id": "video_merge", "name": "Video Merger", "category": "video", "icon": "🔗",
     "description": "Combine multiple videos", "accepted": ("video",), "batch": False, "settings": {}},
    {"id": "video_speed", "name": "Video Speed Controller", "category": "video", "icon": "⚡",
     "description": "Slow-motion / fast-motion", "accepted": ("video",), "batch": False,
     "settings": {"speed": {"type": "slider", "min": 0.25, "max": 4.0, "default": 1.0, "step": 0.25}}},
    {"id": "gif_create", "name": "GIF Creator", "category": "video", "icon": "🎞️",
     "description": "Create GIFs from video", "accepted": ("video",), "batch": False,
     "settings": {"fps": {"type": "slider", "min": 5, "max": 30, "default": 10, "step": 1}}},
    {"id": "video_thumbnail", "name": "Video Thumbnail", "category": "video", "icon": "🖼️",
     "description": "Extract thumbnail frame", "accepted": ("video",), "batch": False,
     "settings": {"time_sec": {"type": "number", "min": 0.0, "default": 1.0, "step": 0.1}}},
    {"id": "frame_extract", "name": "Frame Extractor", "category": "video", "icon": "🎞️",
     "description": "Export all frames", "accepted": ("video",), "batch": False,
     "settings": {"every_n": {"type": "number", "min": 1, "default": 1}}},

    {"id": "poster", "name": "Poster Maker", "category": "design", "icon": "🖼️",
     "description": "Create posters with text", "accepted": (), "batch": False,
     "settings": {"width": {"type": "number", "min": 100, "default": 800},
                  "height": {"type": "number", "min": 100, "default": 1100},
                  "bg_color": {"type": "color", "default": "#ffffff"},
                  "title": {"type": "text", "default": "Event Title"},
                  "subtitle": {"type": "text", "default": "Your amazing event goes here"}}},
    {"id": "flyer", "name": "Flyer Maker", "category": "design", "icon": "📰",
     "description": "Design marketing flyers", "accepted": (), "batch": False,
     "settings": {"width": {"type": "number", "min": 100, "default": 800},
                  "height": {"type": "number", "min": 100, "default": 1100},
                  "bg_color": {"type": "color", "default": "#ffffff"},
                  "title": {"type": "text", "default": "Special Offer"},
                  "subtitle": {"type": "text", "default": "Limited Time Only"},
                  "body": {"type": "textarea", "default": "Get 50% off on all products."}}},
    {"id": "banner", "name": "Banner Maker", "category": "design", "icon": "🏷️",
     "description": "Web/print banners", "accepted": (), "batch": False,
     "settings": {"width": {"type": "number", "min": 100, "default": 1200},
                  "height": {"type": "number", "min": 50, "default": 400},
                  "bg_color": {"type": "color", "default": "#7c3aed"},
                  "title": {"type": "text", "default": "SUMMER SALE"},
                  "subtitle": {"type": "text", "default": "Up to 70% OFF"}}},
    {"id": "social_post", "name": "Social Media Post", "category": "design", "icon": "📱",
     "description": "Platform-optimized posts", "accepted": (), "batch": False,
     "settings": {"platform": {"type": "select", "options": ["Instagram", "Facebook", "Twitter", "LinkedIn"], "default": "Instagram"},
                  "bg_color": {"type": "color", "default": "#0d1117"},
                  "title": {"type": "text", "default": "Your Post Title"},
                  "subtitle": {"type": "text", "default": "Add a catchy subtitle"}}},
    {"id": "yt_thumbnail", "name": "YouTube Thumbnail", "category": "design", "icon": "▶️",
     "description": "Click-worthy thumbnails", "accepted": (), "batch": False,
     "settings": {"bg_color": {"type": "color", "default": "#1a0a3e"},
                  "title": {"type": "text", "default": "AMAZING VIDEO TITLE"},
                  "subtitle": {"type": "text", "default": "Episode 1"}}},

    {"id": "qr_gen", "name": "QR Code Generator", "category": "utilities", "icon": "📱",
     "description": "Generate custom QR codes", "accepted": (), "batch": False,
     "settings": {"data": {"type": "text", "default": "https://example.com"},
                  "size": {"type": "slider", "min": 5, "max": 30, "default": 10, "step": 1},
                  "fill_color": {"type": "color", "default": "#000000"},
                  "bg_color": {"type": "color", "default": "#ffffff"}}},
    {"id": "barcode_gen", "name": "Barcode Generator", "category": "utilities", "icon": "📊",
     "description": "Standard barcodes", "accepted": (), "batch": False,
     "settings": {"data": {"type": "text", "default": "1234567890"},
                  "barcode_type": {"type": "select", "options": ["code128", "code39", "ean13"], "default": "code128"}}},
    {"id": "meme_gen", "name": "Meme Generator", "category": "utilities", "icon": "😂",
     "description": "Add meme text to images", "accepted": ("image",), "batch": True,
     "settings": {"top_text": {"type": "text", "default": "WHEN YOU DEPLOY ON FRIDAY"},
                  "bottom_text": {"type": "text", "default": "AND NOTHING BREAKS"},
                  "font_size": {"type": "slider", "min": 20, "max": 80, "default": 40, "step": 1}}},
    {"id": "collage", "name": "Collage Maker", "category": "utilities", "icon": "🖼️",
     "description": "Combine images in grids", "accepted": ("image",), "batch": False,
     "settings": {"layout": {"type": "select", "options": ["grid", "horizontal", "vertical"], "default": "grid"},
                  "spacing": {"type": "slider", "min": 0, "max": 30, "default": 10, "step": 1},
                  "bg_color": {"type": "color", "default": "#ffffff"}}},
    {"id": "bg_remover", "name": "Background Remover", "category": "utilities", "icon": "🖼️",
     "description": "Remove image backgrounds", "accepted": ("image",), "batch": True, "settings": {}},
    {"id": "bg_adder", "name": "Background Adder", "category": "utilities", "icon": "🎨",
     "description": "Add color/image backgrounds", "accepted": ("image",), "batch": True,
     "settings": {"bg_type": {"type": "radio", "options": ["Solid Color", "Image"], "default": "Solid Color"},
                  "color": {"type": "color", "default": "#ffffff"}}},
    {"id": "color_grader", "name": "Color Grader", "category": "utilities", "icon": "🌈",
     "description": "Brightness, contrast, saturation", "accepted": ("image",), "batch": True,
     "settings": {"brightness": {"type": "slider", "min": 0.0, "max": 2.0, "default": 1.0, "step": 0.05},
                  "contrast": {"type": "slider", "min": 0.0, "max": 2.0, "default": 1.0, "step": 0.05},
                  "saturation": {"type": "slider", "min": 0.0, "max": 2.0, "default": 1.0, "step": 0.05},
                  "filter": {"type": "select", "options": ["None", "B&W", "Sepia", "Warm", "Cool", "Cyberpunk"], "default": "None"},
                  "format": {"type": "select", "options": ["JPEG", "PNG"], "default": "JPEG"}}},
]

_TOOLS_BY_ID = {t["id"]: t for t in TOOLS}
_TOOLS_BY_CATEGORY = {}
for _t in TOOLS:
    _TOOLS_BY_CATEGORY.setdefault(_t["category"], []).append(_t)


def get_all_tools():
    return TOOLS


def get_tool(tool_id: str):
    return _TOOLS_BY_ID.get(tool_id)


def get_tools_by_category(category: str):
    if category == "all":
        return TOOLS
    return _TOOLS_BY_CATEGORY.get(category, [])


def search_tools(query: str):
    q = query.lower().strip()
    if not q:
        return TOOLS
    return [t for t in TOOLS if q in t["name"].lower() or q in t["description"].lower()]


def get_category_info(category: str):
    return TOOL_CATEGORIES.get(category, {"name": category, "icon": "📦", "description": ""})
