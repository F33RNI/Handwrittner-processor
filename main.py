"""
This is free and unencumbered software released into the public domain.
Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.
In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
For more information, please refer to <https://unlicense.org>
"""

import glob
import os

import numpy as np
import cv2

# Path to directory with .png files from handwrittner.com
PATH_TO_HANDWRITTENER = "C:\\Users\\F3rni\\Documents\\Polytech\\магистратура\\защита интеллектуальной собственности\\handwrittner.com-POPxzexL"

# Path where to save processed images
OUTPUT_DIRECTORY = "To print"

# Extension (format) of input and output files
HANDWRITTENER_EXTENSION = "png"
OUTPUT_FILES_EXTENSION = "jpg"

# Letter: 2550 X 3300
OUTPUT_FILE_WIDTH = 2550
OUTPUT_FILE_HEIGHT = 3300

OUTPUT_FILE_PADDING_LEFT = 288
OUTPUT_FILE_PADDING_TOP = 151
OUTPUT_FILE_PADDING_RIGHT = 130
OUTPUT_FILE_PADDING_BOTTOM = 256

HANDWRITTENER_FILE_PADDING_LEFT_ODD = 21
HANDWRITTENER_FILE_PADDING_TOP_ODD = 29
HANDWRITTENER_FILE_PADDING_RIGHT_ODD = 106
HANDWRITTENER_FILE_PADDING_BOTTOM_ODD = 184

HANDWRITTENER_FILE_PADDING_LEFT_EVEN = 106
HANDWRITTENER_FILE_PADDING_TOP_EVEN = 29
HANDWRITTENER_FILE_PADDING_RIGHT_EVEN = 22
HANDWRITTENER_FILE_PADDING_BOTTOM_EVEN = 184

# Keep it as high as possible without getting background visible
COLOR_KEEP_THRESHOLD_BGR = (220, 0, 0)

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    # Create output directory if not exists
    if not os.path.exists(OUTPUT_DIRECTORY):
        print("Creating " + OUTPUT_DIRECTORY + " directory")
        os.makedirs(OUTPUT_DIRECTORY)

    # List all png files in directory
    pages = glob.glob(glob.escape(PATH_TO_HANDWRITTENER) + "/*." + HANDWRITTENER_EXTENSION)
    print("Found " + str(len(pages)) + " pages")
    for page in pages:
        # Extract page number from filename 1-страница-handwrittner.com-POPxzexL.png
        page_number = int(os.path.basename(page).split("-")[0])
        is_page_even = page_number % 2 == 0
        print("Processing page: " + str(page_number))

        # Generate output image with white background
        final_image = np.ones((OUTPUT_FILE_HEIGHT, OUTPUT_FILE_WIDTH, 3), dtype=np.uint8) * 255

        # Read image from file
        image = cv2.imdecode(np.fromfile(page, dtype=np.uint8), cv2.IMREAD_COLOR)
        image_width = image.shape[1]
        image_height = image.shape[0]

        # Calculate width and height in pixels of cutouts (zones) of final images
        if is_page_even:
            image_cut_width = image_width - HANDWRITTENER_FILE_PADDING_LEFT_EVEN \
                              - HANDWRITTENER_FILE_PADDING_RIGHT_EVEN
            image_cut_height = image_height - HANDWRITTENER_FILE_PADDING_TOP_EVEN \
                               - HANDWRITTENER_FILE_PADDING_BOTTOM_EVEN
        else:
            image_cut_width = image_width - HANDWRITTENER_FILE_PADDING_LEFT_ODD \
                              - HANDWRITTENER_FILE_PADDING_RIGHT_ODD
            image_cut_height = image_height - HANDWRITTENER_FILE_PADDING_TOP_ODD \
                               - HANDWRITTENER_FILE_PADDING_BOTTOM_ODD
        output_cut_width = OUTPUT_FILE_WIDTH - OUTPUT_FILE_PADDING_LEFT - OUTPUT_FILE_PADDING_RIGHT
        output_cut_height = OUTPUT_FILE_HEIGHT - OUTPUT_FILE_PADDING_TOP - OUTPUT_FILE_PADDING_BOTTOM

        # Calculate resize coefficients based on cutouts
        resize_k_x = output_cut_width / image_cut_width
        resize_k_y = output_cut_height / image_cut_height
        resize_k = (resize_k_x + resize_k_y) / 2
        image_resized_width = int(image_width * resize_k)
        image_resized_height = int(image_height * resize_k)

        # Resize handwrittener image
        image_resized = cv2.resize(image, (image_resized_width, image_resized_height))

        # Calculate new paddings of resized handwrittener image
        if is_page_even:
            padding_left_resized = int(HANDWRITTENER_FILE_PADDING_LEFT_EVEN * resize_k)
            padding_top_resized = int(HANDWRITTENER_FILE_PADDING_TOP_EVEN * resize_k)
            padding_right_resized = int(HANDWRITTENER_FILE_PADDING_RIGHT_EVEN * resize_k)
            padding_bottom_resized = int(HANDWRITTENER_FILE_PADDING_BOTTOM_EVEN * resize_k)
        else:
            padding_left_resized = int(HANDWRITTENER_FILE_PADDING_LEFT_ODD * resize_k)
            padding_top_resized = int(HANDWRITTENER_FILE_PADDING_TOP_ODD * resize_k)
            padding_right_resized = int(HANDWRITTENER_FILE_PADDING_RIGHT_ODD * resize_k)
            padding_bottom_resized = int(HANDWRITTENER_FILE_PADDING_BOTTOM_ODD * resize_k)

        # Calculate where we need to place resized handwrittener image on top of final_image
        if is_page_even:
            place_to_top_left_x = OUTPUT_FILE_PADDING_RIGHT - padding_left_resized
        else:
            place_to_top_left_x = OUTPUT_FILE_PADDING_LEFT - padding_left_resized
        place_to_top_left_y = OUTPUT_FILE_PADDING_TOP - padding_top_resized

        # Crop resized handwrittener image if we get negative values
        if place_to_top_left_x < 0:
            image_resized = image_resized[:, -place_to_top_left_x: image_resized_width]
        if place_to_top_left_y < 0:
            image_resized = image_resized[-place_to_top_left_y: image_resized_height, :]

        # Re-calculate size of cropped handwrittener image
        image_resized_width = image_resized.shape[1]
        image_resized_height = image_resized.shape[0]

        # Crop handwrittener image if it is larger that output image
        if image_resized_width + max(place_to_top_left_x, 0) > OUTPUT_FILE_WIDTH:
            image_resized \
                = image_resized[:, : -(image_resized_width - OUTPUT_FILE_WIDTH) - max(place_to_top_left_x, 0)]
        if image_resized_height + max(place_to_top_left_y, 0) > OUTPUT_FILE_HEIGHT:
            image_resized \
                = image_resized[: -(image_resized_height - OUTPUT_FILE_HEIGHT) - max(place_to_top_left_y, 0), :]

        # Re-calculate size of cropped handwrittener image again
        image_resized_width = image_resized.shape[1]
        image_resized_height = image_resized.shape[0]

        # Calculate top-left corner and right-bottom corner of final image where we need to paste handwrittener image
        place_image_from_x = max(place_to_top_left_x, 0)
        place_image_from_y = max(place_to_top_left_y, 0)
        place_image_to_x = image_resized_width + max(place_to_top_left_x, 0)
        place_image_to_y = image_resized_height + max(place_to_top_left_y, 0)


        # Paste handwrittener image on top of final image
        final_image[place_image_from_y: place_image_to_y, place_image_from_x: place_image_to_x] = image_resized

        # Create mask where white region is where we need to remove checkered background
        mask = np.ones((OUTPUT_FILE_HEIGHT, OUTPUT_FILE_WIDTH), dtype=np.uint8) * 255

        if is_page_even:
            mask[OUTPUT_FILE_PADDING_TOP: OUTPUT_FILE_HEIGHT - OUTPUT_FILE_PADDING_BOTTOM,
            OUTPUT_FILE_PADDING_RIGHT: OUTPUT_FILE_WIDTH - OUTPUT_FILE_PADDING_LEFT] = 0
        else:
            mask[OUTPUT_FILE_PADDING_TOP: OUTPUT_FILE_HEIGHT - OUTPUT_FILE_PADDING_BOTTOM,
            OUTPUT_FILE_PADDING_LEFT: OUTPUT_FILE_WIDTH - OUTPUT_FILE_PADDING_RIGHT] = 0

        # Find all text by color
        text = cv2.inRange(final_image, COLOR_KEEP_THRESHOLD_BGR, (255, 255, 255))

        # Apply mask to get only text that is outsize of target zone
        text_outside_zone = cv2.bitwise_and(text, mask)

        # Invert mask
        text_outside_zone = cv2.bitwise_not(text_outside_zone)

        # Remove all checkered background from final image outside mask and keep written text
        final_image = cv2.bitwise_and(final_image, final_image, mask=text_outside_zone)

        # Convert mask from 1d to 2d
        text_outside_zone = cv2.cvtColor(text_outside_zone, cv2.COLOR_GRAY2BGR)

        # Replace background to white where there is no mask
        final_image[(text_outside_zone == 0).all(-1)] = (255, 255, 255)

        # Save result to file and specify in name is page even or odd
        cv2.imwrite(os.path.join(OUTPUT_DIRECTORY,
                                 str(page_number) + ("_FLIP" if is_page_even else "") + "." + OUTPUT_FILES_EXTENSION),
                    final_image)

    # All pages processed
    print("Done!")
