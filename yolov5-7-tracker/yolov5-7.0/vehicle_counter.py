# -*- coding: utf-8 -*-
"""Track vehicle detections and count each vehicle once when it crosses a line."""

import math

import cv2


VEHICLE_CLASSES = [2, 3, 5, 7]  # COCO: car, motorcycle, bus, truck


def _anchor(box):
    x1, _, x2, y2 = box
    return ((x1 + x2) / 2, y2)


def _iou(a, b):
    left, top = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[2], b[2]), min(a[3], b[3])
    overlap = max(0, right - left) * max(0, bottom - top)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - overlap
    return overlap / union if union else 0


class VehicleCounter:
    """Match adjacent-frame boxes and count confirmed line crossings."""

    def __init__(self, line_fraction=0.65, max_missing=10):
        self.line_fraction = line_fraction
        self.max_missing = max_missing
        self.reset()

    def reset(self):
        self.tracks = {}
        self.next_id = 1
        self.up = 0
        self.down = 0

    @property
    def total(self):
        return self.up + self.down

    @staticmethod
    def _side(y, line_y, band):
        if y < line_y - band:
            return -1
        if y > line_y + band:
            return 1
        return 0

    def update(self, detections, frame_shape):
        """detections: (x1, y1, x2, y2, confidence, class_name)."""
        height, width = frame_shape[:2]
        line_y = int(height * self.line_fraction)
        band = max(4, int(height * 0.006))
        matches = []

        for index, detection in enumerate(detections):
            box = detection[:4]
            name = detection[5]
            point = _anchor(box)
            for track_id, track in self.tracks.items():
                if track['name'] != name:
                    continue
                old_point = _anchor(track['box'])
                distance = math.hypot(point[0] - old_point[0], point[1] - old_point[1])
                max_distance = max(45, width * 0.06, (box[2] - box[0]) * 0.8)
                overlap = _iou(box, track['box'])
                if overlap < 0.05 and distance > max_distance:
                    continue
                matches.append((overlap * 2 - distance / max_distance,
                                index, track_id))

        assigned_detections = set()
        assigned_tracks = set()
        visible = []
        for _, index, track_id in sorted(matches, reverse=True):
            if index in assigned_detections or track_id in assigned_tracks:
                continue
            assigned_detections.add(index)
            assigned_tracks.add(track_id)
            detection = detections[index]
            track = self.tracks[track_id]
            side = self._side(_anchor(detection[:4])[1], line_y, band)
            if side and track['side'] and side != track['side'] and not track['counted'] \
                    and track['hits'] >= 2:
                if side > 0:
                    self.down += 1
                else:
                    self.up += 1
                track['counted'] = True
            if side:
                track['side'] = side
            track['box'] = detection[:4]
            track['hits'] += 1
            track['missing'] = 0
            visible.append((track_id, detection))

        for track_id in list(self.tracks):
            if track_id not in assigned_tracks:
                self.tracks[track_id]['missing'] += 1
                if self.tracks[track_id]['missing'] > self.max_missing:
                    del self.tracks[track_id]

        for index, detection in enumerate(detections):
            if index in assigned_detections:
                continue
            self.tracks[self.next_id] = {
                'box': detection[:4],
                'name': detection[5],
                'side': self._side(_anchor(detection[:4])[1], line_y, band),
                'hits': 1,
                'missing': 0,
                'counted': False,
            }
            visible.append((self.next_id, detection))
            self.next_id += 1
        return visible

    def draw(self, frame, visible):
        height, width = frame.shape[:2]
        line_y = int(height * self.line_fraction)
        cv2.line(frame, (0, line_y), (width - 1, line_y), (0, 255, 255), 2)
        for track_id, detection in visible:
            x1, y1, x2, y2, _, name = detection
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
            cv2.putText(frame, '{} #{}'.format(name, track_id),
                        (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (0, 200, 0), 2, cv2.LINE_AA)
        cv2.rectangle(frame, (5, 5), (min(width - 1, 440), 48), (0, 0, 0), -1)
        cv2.putText(frame, 'Vehicles: {}  Up: {}  Down: {}'.format(
            self.total, self.up, self.down), (15, 35),
            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2, cv2.LINE_AA)
