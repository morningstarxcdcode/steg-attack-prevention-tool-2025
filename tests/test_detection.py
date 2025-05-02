import unittest
from PIL import Image
import numpy as np
import sys
import os

# Add parent directory to path to import main module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import extract_lsb_ratios, model

class TestSteganographyDetection(unittest.TestCase):

    def create_test_image(self, lsb_ratio):
        # Create an image with specified LSB ratio in red channel
        size = (10, 10)
        data = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        # Set LSB bits in red channel according to ratio
        total_pixels = size[0] * size[1]
        num_set_bits = int(total_pixels * lsb_ratio)
        for i in range(num_set_bits):
            x = i % size[0]
            y = i // size[0]
            data[y, x, 0] = 1  # LSB set
        img = Image.fromarray(data, 'RGB')
        return img

    def test_clean_image(self):
        img = self.create_test_image(0.1)
        features = extract_lsb_ratios(img)
        prediction = model.predict([features])[0]
        self.assertEqual(prediction, 0)

    def test_stego_image(self):
        img = self.create_test_image(0.6)
        features = extract_lsb_ratios(img)
        prediction = model.predict([features])[0]
        self.assertEqual(prediction, 1)

if __name__ == '__main__':
    unittest.main()
