from scipy.spatial import distance as dist


class TrackerBox(object):
    """
    Attributes:
        coordinates left, bottom, right, top values
        confidence  the confidence value the box was detected with
    """

    def __init__(self, coordinates, confidence = 1.0):
        self.coordinates = coordinates
        self.confidence = confidence


def __rect_overlapping(rect1, rect2):
    # 0-3: left, bottom, right, top
    rect1_area = (rect1[2] - rect1[0]) * (rect1[3] - rect1[1])

    x_overlap = max(0, min(rect1[2], rect2[2]) - max(rect1[0], rect2[0]))
    y_overlap = max(0, min(rect1[3], rect2[3]) - max(rect1[1], rect2[1]))
    overlap_area = x_overlap * y_overlap

    return overlap_area / rect1_area


def drop_overlapping_boxes(candidates, overlapping = 0.3):
    coord_candidates = [candidate.coordinates for candidate in candidates]
    c = dist.cdist(coord_candidates, coord_candidates, __rect_overlapping)

    # Every box overlap themself
    for i in range(c.shape[0]):
        c[i, i] = 0

    # Keep boxes on these indexes
    keep = {i for i in range(c.shape[0])}

    while c.max() > overlapping:
        rows = c.max(axis=1).argsort()[::-1]
        row = rows[0]
        keep.remove(row)
        c[:, row] = 0
        c[row, :] = 0

    return [candidates[i] for i in keep]
