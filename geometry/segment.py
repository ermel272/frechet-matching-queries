class Segment2D(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b


class PolygonalCurve2D(object):
    def __init__(self, points=None):
        self.segments = list()

        if points:
            self.segments = self.__init_segments(points)

    def add_segment(self, segment):
        if self.segments[-1].b != segment.a:
            return False

        self.segments.append(segment)
        return True

    @staticmethod
    def __init_segments(points):
        assert len(points) >= 2, 'Need at least 2 points to define a polygonal curve.'
        segments = list()

        last = points[0]
        for point in points[1:]:
            segments.append(Segment2D(last, point))
            last = point

        return segments
