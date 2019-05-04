class TrackableObject:
    def __init__(self, objectID, centroid):
        # store the object ID, then initialize a list of centroids
        # using the current centroid
        self.objectID = objectID
        self.centroids = [centroid]

        # initialize a boolean used to indicate if the object has
        # already been counted or not
        self.counted = False

        # Direction
        self.number_of_speed_data = 0
        self.x_speed = 0
        self.y_speed = 0
