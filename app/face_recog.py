import cv2
import numpy as np

from insightface.app import FaceAnalysis


class FaceEngine:

    def __init__(self):

        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=[
                "CPUExecutionProvider"
            ]
        )

        self.app.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

    def extract_embedding(
        self,
        image_bytes: bytes
    ):

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None:
            raise ValueError(
                "Invalid image"
            )

        faces = self.app.get(image)

        if len(faces) == 0:

            raise ValueError(
                "No face detected"
            )

        if len(faces) > 1:

            raise ValueError(
                "Multiple faces detected"
            )

        face = faces[0]

        embedding = face.embedding

        embedding = (
            embedding /
            np.linalg.norm(embedding)
        )

        return embedding.astype(
            np.float32
        )