import math
class EuclideanDistTracker:
    def __init__(self):
        # Store the center positions of the objects
        self.center_points = {}
        # Keep the count of the IDs
        # each time a new object id detected, the count will increase by one
        self.id_count = 0

    def update(self, objects_rect):
        # Objects boxes and ids
        objects_bbs_ids = []

        # Get center point of new object
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # Find out if that object was detected already
            object_id = None
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 25:
                    object_id = id
                    break

            # New object is detected we assign the ID to that object
            if object_id is None:
                object_id = self.id_count
                self.id_count += 1

            # Update dictionary with new object center
            self.center_points[object_id] = (cx, cy)
            objects_bbs_ids.append([x, y, w, h, object_id])

        # Clean the dictionary by center points to remove IDS not used anymore
        active_object_ids = list(self.center_points.keys())
        for object_id in active_object_ids:
            if object_id not in [obj_bb_id[4] for obj_bb_id in objects_bbs_ids]:
                del self.center_points[object_id]

        return objects_bbs_ids
