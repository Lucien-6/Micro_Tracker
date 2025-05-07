import base64
import time
from io import BytesIO

import cv2
import numpy as np
from PIL import Image

from models.gdino.utils import display_image_with_boxes
from models.gdino.models.gdino import GDINO
from models.gdino.utils import DEVICE
from models.sam2.sam import SAM


class Lang2Seg_img:
    def __init__(self, sam_type="sam2.1_hiera_tiny", ckpt_path: str | None = None, device=DEVICE, GroundingDINO_16=False):
        self.sam_type = sam_type

        self.sam = SAM()
        self.sam.build_model(sam_type, ckpt_path, device=device)
        self.gdino = GDINO()
        self.GroundingDINO_16 = GroundingDINO_16
        if not self.GroundingDINO_16:
            print("Building GroundingDINO model...")
            self.gdino.build_model(device=device)

    def predict(
        self,
        images_pil: list[Image.Image],
        texts_prompt: list[str],
        box_threshold: float = 0.3,
        text_threshold: float = 0.25,
    ):
        """Predicts masks for given images and text prompts using GDINO and SAM models.

        Parameters:
            images_pil (list[Image.Image]): List of input images.
            texts_prompt (list[str]): List of text prompts corresponding to the images.
            box_threshold (float): Threshold for box predictions.
            text_threshold (float): Threshold for text predictions.

        Returns:
            list[dict]: List of results containing masks and other outputs for each image.
            Output format:
            [{
                "boxes": np.ndarray,
                "scores": np.ndarray,
                "masks": np.ndarray,
                "mask_scores": np.ndarray,
            }, ...]
        """

        if self.GroundingDINO_16:
            if len(images_pil) > 1:
                raise ValueError("GroundingDINO_16 only support single image")
            byte_io = BytesIO()
            images_pil[0].save(byte_io, format='PNG')
            image_bytes = byte_io.getvalue()
            base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
            texts_prompt = texts_prompt[0]
            gdino_results = self.gdino.predict_dino_1_6_pro(base64_encoded, texts_prompt, box_threshold, text_threshold)
        else:
            gdino_results = self.gdino.predict(images_pil, texts_prompt, box_threshold, text_threshold)
        all_results = []
        sam_images = []
        sam_boxes = []
        sam_indices = []
        for idx, result in enumerate(gdino_results):
            result = {k: (v.cpu().numpy() if hasattr(v, "numpy") else v) for k, v in result.items()}
            processed_result = {
                **result,
                "masks": [],
                "mask_scores": [],
            }

            if result["labels"]:
                sam_images.append(np.asarray(images_pil[idx]))
                sam_boxes.append(processed_result["boxes"])
                sam_indices.append(idx)

            all_results.append(processed_result)
        if sam_images:
            # print(f"Predicting {len(sam_boxes)} masks")
            masks, mask_scores, _ = self.sam.predict_batch(sam_images, xyxy=sam_boxes)
            for idx, mask, score in zip(sam_indices, masks, mask_scores):
                all_results[idx].update(
                    {
                        "masks": mask,
                        "mask_scores": score,
                    }
                )
            # print(f"Predicted {len(all_results)} masks")
        return all_results


if __name__ == "__main__":
    model = Lang2Seg_img(GroundingDINO_16=False)
    out = model.predict(
        [Image.open("assets/img_01.jpg")],
        ["cup.ball"],
    )
    print(out)
    img = cv2.imread("assets/img_01.jpg")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    display_image_with_boxes(img, list(out[0]["boxes"]), out[0]["scores"], list(out[0]["labels"]))

