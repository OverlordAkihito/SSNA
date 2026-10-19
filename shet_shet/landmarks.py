"""MediaPipe face-mesh indices used by the luminous dot filter.

The groups follow MediaPipe's published Face Landmarker contour connections:
https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/tasks/python/vision/face_landmarker.py
We render their unique endpoints as individual dots rather than drawing the
connections as solid lines.
"""

from __future__ import annotations


FACE_OVAL = (
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365,
    379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93,
    234, 127, 162, 21, 54, 103, 67, 109,
)

LEFT_EYE = (
    263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387,
    388, 466,
)
RIGHT_EYE = (
    33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160,
    161, 246,
)
LEFT_EYEBROW = (276, 283, 282, 295, 285, 300, 293, 334, 296, 336)
RIGHT_EYEBROW = (46, 53, 52, 65, 55, 70, 63, 105, 66, 107)
NOSE = (
    168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 98, 97, 326, 327, 294, 278,
    344, 440, 275, 45, 220, 115, 48, 64,
)
LIPS = (
    61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 185, 40, 39, 37,
    0, 267, 269, 270, 409, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324,
    308, 191, 80, 81, 82, 13, 312, 311, 310, 415,
)
LEFT_IRIS = (474, 475, 476, 477)
RIGHT_IRIS = (469, 470, 471, 472)

EYE_DOTS = tuple(sorted(set(LEFT_EYE + RIGHT_EYE + LEFT_IRIS + RIGHT_IRIS)))
EYEBROW_DOTS = tuple(sorted(set(LEFT_EYEBROW + RIGHT_EYEBROW)))
NOSE_DOTS = tuple(sorted(set(NOSE)))
LIP_DOTS = tuple(sorted(set(LIPS)))
FACE_DOTS = tuple(sorted(set(FACE_OVAL + EYEBROW_DOTS + EYE_DOTS + NOSE_DOTS + LIP_DOTS)))

# Eye and iris points get the magenta halo. Larger pearl dots mark stable,
# visually useful anchors without adding any inferred positions.
EYE_ANCHORS = frozenset((33, 133, 263, 362, 469, 474, 1, 61, 291, 152))
