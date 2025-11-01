# file that runs on PC and converts images to bytes, store them in data.json and send them to pico

import PIL.Image
import os
import PIL.ImageMode
import json
import base64

print("======== SCRIPT STARTED =======")
print("\n")
print("Converting images to byte...")

# https://github.com/TimHanewich/MicroPython-SSD1306
def image_to_buffer(
    img_path: str, threshold: float = 0.5, resize: tuple[int, int] = None
) -> tuple[bytes, int, int]:
    """
    Converts a bitmap image (JPG, PNG, etc.) to a byte buffer, translating each RGB pixel into a single white/black dot that can be displayed on an OLED display.

    Parameters
    ----------
    img_path:str
        The path to the image file.
    threshold:float, optional
        Defines how "dark" each RGB pixel has to be for it to be considered "filled in". Higher threshold values are more discriminating.

    Returns
    -------
    tuple
        A tuple containing:
        - bytes: The image data in bytes that can be loaded into a FrameBuffer in MicroPython.
        - int: The width of the image.
        - int: The height of the image.
    """

    # open image
    i = PIL.Image.open(img_path).convert(
        "RGB"
    )  # always open in RGB mode (don't handle RGBA like in PNG)

    # resize if desired
    if resize != None:
        i = i.resize(resize)

    # record size
    width, height = i.size

    # calculate the threshold. In other words, the average RGB value that the pixel has to be below (filled in with darkness) to be considered "on" and above to be considered "off"
    thresholdRGB: int = min(max(int(round(threshold * 255, 0)), 0), 255)

    # get a list of individual bits for each pixel (True is filled in, False is not filled in)
    bits: list[bool] = []
    for y in range(0, height):
        for x in range(0, width):
            pix: tuple[int, int, int, int] = i.getpixel((x, y))  # [R,G,B,A]

            # determine, is this pixel solid (filled in BLACK) or not (filled in WHITE)?
            filled: bool = False
            avg: int = int(round((pix[0] + pix[1] + pix[2]) / 3, 0))
            if avg >= thresholdRGB:  # it is bright (so fill it with an on pixel)
                filled = True

            # add it to the list of bits
            bits.append(filled)

    # now that we have all the bits, chunk them by 8 and convert
    BytesToReturn: bytearray = bytearray()
    bit_collection_buffer: list[bool] = []
    for bit in bits:
        # add it
        bit_collection_buffer.append(bit)

        # if we are now at 8, convert and append
        if len(bit_collection_buffer) == 8:
            # convert to 1's and 0's
            AsStr: str = ""
            for bit in bit_collection_buffer:
                if bit:
                    AsStr = AsStr + "1"
                else:
                    AsStr = AsStr + "0"

            # convert to byte
            b = int(AsStr, 2)

            # Add it
            BytesToReturn.append(b)

            # clear out bit collection buffer
            bit_collection_buffer.clear()

    # return!
    return (bytes(BytesToReturn), width, height)


# all the path
paths = [
    "temp/clock/0.png",
    "temp/clock/1.png",
    "temp/clock/2.png",
    "temp/clock/3.png",
    "temp/clock/4.png",
    "temp/clock/5.png",
    "temp/clock/6.png",
    "temp/clock/7.png",
    "temp/clock/8.png",
    "temp/clock/9.png",
    "temp/clock/dots.png",
]

data = {}


# convert to byte
for i in range(10):
    converted = image_to_buffer(paths[i])
    data.update({i: converted[0]})

# special traitement for ":" because it's not a number
converted = image_to_buffer(paths[10])
data.update({10: converted[0]})

print("Converted !")
print("Encoding...")

# encode data in base64 because json doesn't accept raw bytes
encoded_data = {
    str(k): base64.b64encode(v).decode("utf-8")  
    for k, v in data.items()
}

print("Encoded !")
print("Writing...")

# write in the file
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(encoded_data, f, indent=2)

print("Writed !")

# send to pico, disconnect all app connected to pico to let mpremote works
os.system("mpremote cp data.json :data.json")

print("Synced with Pico")


print("\n")
print("===============================")
print("\n")

os.system("mpremote run main.py")