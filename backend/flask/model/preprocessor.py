import random
from typing import Tuple, List

import cv2
import numpy as np



class TextImagePreprocessor:
    def __init__(self,
                 target_image_size: Tuple[int, int],
                 padding: int = 0,
                 dynamic_width: bool = False,
                 apply_data_augmentation: bool = False,
                 line_mode: bool = False) -> None:
        # Dynamic width only supported when no data augmentation happens
        assert not (dynamic_width and apply_data_augmentation)
        # When padding is on, we need dynamic width enabled
        assert not (padding > 0 and not dynamic_width)

        self.target_image_size = target_image_size
        self.padding = padding
        self.dynamic_width = dynamic_width
        self.apply_data_augmentation = apply_data_augmentation
        self.line_mode = line_mode

   
   
    def process_image(self, image: np.ndarray) -> np.ndarray:
        """Resize to the target size and apply data augmentation."""

        # There are damaged files in the IAM dataset - just use a black image instead
        if image is None:
            image = np.zeros(self.target_image_size[::-1])

        # Data augmentation
        image = image.astype(float)
        if self.apply_data_augmentation:
            # Photometric data augmentation
            if random.random() < 0.25:
                def random_odd():
                    return random.randint(1, 3) * 2 + 1
                image = cv2.GaussianBlur(image, (random_odd(), random_odd()), 0)
            if random.random() < 0.25:
                image = cv2.dilate(image, np.ones((3, 3)))
            if random.random() < 0.25:
                image = cv2.erode(image, np.ones((3, 3)))

            # Geometric data augmentation
            width_target, height_target = self.target_image_size
            height, width = image.shape
            factor = min(width_target / width, height_target / height)
            fx = factor * np.random.uniform(0.75, 1.05)
            fy = factor * np.random.uniform(0.75, 1.05)

            # Random position around the center
            txc = (width_target - width * fx) / 2
            tyc = (height_target - height * fy) / 2
            freedom_x = max((width_target - fx * width) / 2, 0)
            freedom_y = max((height_target - fy * height) / 2, 0)
            tx = txc + np.random.uniform(-freedom_x, freedom_x)
            ty = tyc + np.random.uniform(-freedom_y, freedom_y)

            # Map the image into the target image
            M = np.float32([[fx, 0, tx], [0, fy, ty]])
            target = np.ones(self.target_image_size[::-1]) * 255
            image = cv2.warpAffine(image, M, dsize=self.target_image_size, dst=target, borderMode=cv2.BORDER_TRANSPARENT)

            # Photometric data augmentation
            if random.random() < 0.5:
                image = image * (0.25 + random.random() * 0.75)
            if random.random() < 0.25:
                image = np.clip(image + (np.random.random(image.shape) - 0.5) * random.randint(1, 25), 0, 255)
            if random.random() < 0.1:
                image = 255 - image

        # No data augmentation
        else:
            if self.dynamic_width:
                height_target = self.target_image_size[1]
                height, width = image.shape
                factor = height_target / height
                width_target = int(factor * width + self.padding)
                width_target = width_target + (4 - width_target) % 4
                tx = (width_target - width * factor) / 2
                ty = 0
            else:
                width_target, height_target = self.target_image_size
                height, width = image.shape
                factor = min(width_target / width, height_target / height)
                tx = (width_target - width * factor) / 2
                ty = (height_target - height * factor) / 2

            # Map the image into the target image
            M = np.float32([[factor, 0, tx], [0, factor, ty]])
            target = np.ones([height_target, width_target]) * 255
            image = cv2.warpAffine(image, M, dsize=(width_target, height_target), dst=target, borderMode=cv2.BORDER_TRANSPARENT)

        # Transpose for TensorFlow
        image = cv2.transpose(image)

        # Convert to range [-1, 1]
        image = image / 255 - 0.5
        return image

    

def main():
    import matplotlib.pyplot as plt

    image = cv2.imread('/Users/fofejo/Desktop/test4.png', cv2.IMREAD_GRAYSCALE)
    preprocessor = TextImagePreprocessor(target_image_size=(256, 32), apply_data_augmentation=True)
    augmented_image = preprocessor.process_image(image)

    # plt.subplot(121)
    # plt.imshow(image, cmap='gray')
    # plt.subplot(122)
    # plt.imshow(cv2.transpose(augmented_image) + 0.5, cmap='gray', vmin=0, vmax=1)
    # plt.show()


if __name__ == '__main__':
    main()
