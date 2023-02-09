"""Image Generation API Utils"""

import io


def image_to_bytes(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="png")
    # img_byte_arr.seek(0)
    # return img_byte_arr
    return img_byte_arr.getvalue()
