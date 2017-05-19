import os
import pyx
from pyx import *
from Perception.Data import *
from Perception.Data.Operators import *


def plan2pdf(area: Area) -> Area:
    return Area(
        Point(area.up_left.x, 1080 - area.up_left.y),
        Point(area.bottom_right.x - area.up_left.x, area.up_left.y - area.bottom_right.y)
    )


class Drawer(object):
    IVThreshold = 200
    ScreenSize = ((0, 0), (1920, 1080))

    Operators = {
        'gaze': GazeOperator(Area(
            Point(*ScreenSize[0]),
            Point(*ScreenSize[1])
        )),
        'ivt': IVTOperator(IVThreshold)
    }

    ChunkOp = ChunkOperator()

    def __init__(self, transaction, destination_path, aoi=None):
        if not os.path.isdir(destination_path):
            raise IOError("Path {0} does not exist.".format(destination_path))
        self.destination = destination_path

        self.time = TimeOperator()
        self.transaction = transaction.accept(self.time)
        self.sample_rate = self.time.sample_rate

        self.aoi_operator = AOIOperator(aoi)

        self.ChunkOp.when(self.transaction, ChunkOperator.purge, self.transaction)
        for operator in self.Operators:
            self.transaction = self.transaction.accept(self.Operators[operator])
        self.transaction.accept(self.aoi_operator)

        median_fixation_weight = 0.0
        for row in self.transaction:
            median_fixation_weight += row["weight"]
        self.median_fixation_time = median_fixation_weight / self.transaction.count() * self.time.time

        self.info = canvas.canvas()
        self.picture = canvas.canvas()

    def information_canvas(self, target: canvas.canvas = None, offset: int = 0) -> canvas.canvas:
        info = canvas.canvas() if target is None else target
        align = text.halign.boxleft

        info.text(0, offset + 5, "EyeTracking Transaction Information",                                 [align])
        info.text(0, offset + 3, "Transaction length (s): " + str(self.time.time),                      [align])
        info.text(0, offset + 2, "Estimated sample rate (hz): " + str(self.time.sample_rate),           [align])
        info.text(0, offset + 1, "Gaze to fixation method: Velocity-Threshold Identification (IVT)",    [align])
        info.text(0, offset + 0, "Threshold (px): " + str(self.IVThreshold),                            [align])
        info.text(0, offset - 1, "Median fixation time (s): " + str(self.median_fixation_time),         [align])

        return info

    def aoi_canvas(self, target: canvas.canvas = None, offset: int = 0) -> canvas.canvas:
        aois = canvas.canvas() if target is None else target

        for i in range(len(self.aoi_operator.match_rates)):
            time_spent_in_aoi = self.aoi_operator.match_rates[i] * self.time.time
            aois.text(
                0,
                offset - i,
                "AOI {index}:{area}, fixation rate: {percent:.4} \% ({seconds:.4}s)".format(
                    index=i,
                    area=str(self.aoi_operator.areas[i]),
                    percent=(self.aoi_operator.match_rates[i] * 100),
                    seconds=str(time_spent_in_aoi)
                )
            )

        return aois

    def legend_canvas(self, target: canvas.canvas = None, offset: int = 0)  -> canvas.canvas:
        legend = canvas.canvas() if target is None else target

        legend.text(0, -1, "Velocity threshold", [text.halign.boxleft])
        legend.stroke(path.line(3, -1, 3 + self.IVThreshold / 100, -1))
        legend.text(0, -2, "Transaction start", [text.halign.boxleft])
        legend.fill(path.circle(3, -1.90, 0.20), [color.rgb(0, 0, 1.0)])
        legend.text(0, -3, "Transaction end", [text.halign.boxleft])
        legend.fill(path.circle(3, -2.90, 0.20), [color.rgb(1.0, 0, 0)])

        return legend

    def graph_canvas(self, target: canvas.canvas = None, offset: int = 0) -> canvas.canvas:
        grph = canvas.canvas() if target is None else target

        grph.stroke(path.rect(-0.05, -0.05, 1920 / 100 + 0.1, 1080 / 100 + 0.1))

        for index in range(self.transaction.count() - 1):
            row = self.transaction[index]
            red_hue = 1.0 * (index + 1) / (self.transaction.count())
            clr = color.rgb(red_hue, 0, 1.0 - red_hue)
            grph.fill(path.circle(row['x'] / 100, (1080 - row['y']) / 100, row['weight'] * 10), [clr])

        for plan_aoi in self.aoi_operator.areas:
            aoi = plan2pdf(plan_aoi)
            area_square = path.rect(aoi.up_left.x / 100, aoi.up_left.y / 100, aoi.bottom_right.x / 100,
                                    aoi.bottom_right.y / 100)
            grph.stroke(area_square)

        return grph

    def draw(self, filename):
        self.information_canvas(self.info)
        self.aoi_canvas(self.info, -2)
        self.legend_canvas(self.picture)
        self.graph_canvas(self.picture)

        info_page   = document.page(self.info,    filename,                       document.paperformat.A4)
        graph_page  = document.page(self.picture, filename + " - fixation graph", document.paperformat.A4, rotated=True)

        doc = document.document([info_page, graph_page])
        doc.writePDFfile(os.path.join(self.destination, filename + ".pdf"))

        self.transaction.save(os.path.join(self.destination, filename + ".csv"))
