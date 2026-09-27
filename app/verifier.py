import numpy as np


class FaceVerifier:

    def __init__(
        self,
        threshold: float = 0.45
    ):

        self.threshold = threshold


    def similarity(
        self,
        first,
        second
    ):

        first = np.asarray(
            first,
            dtype=np.float32
        )

        second = np.asarray(
            second,
            dtype=np.float32
        )

        first /= np.linalg.norm(first)

        second /= np.linalg.norm(second)

        return float(
            np.dot(first, second)
        )


    def verify(
        self,
        captured,
        stored
    ):

        score = self.similarity(
            captured,
            stored
        )

        return {
            "verified":
                score >= self.threshold,

            "similarity":
                score
        }