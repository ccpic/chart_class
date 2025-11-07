"""
Plots module - Collection of plot classes for various chart types.
"""

from chart.plots.base import Plot
from chart.plots.bar import PlotBar, PlotBarh
from chart.plots.line import PlotLine, PlotArea
from chart.plots.scatter import PlotBubble, PlotStripdot
from chart.plots.statistical import PlotHist, PlotBoxdot
from chart.plots.specialty import PlotHeatmap, PlotTreemap, PlotWaffle, PlotFunnel
from chart.plots.pie import PlotPie
from chart.plots.wordcloud import PlotWordcloud
from chart.plots.table import PlotTable
from chart.plots.venn import PlotVenn2, PlotVenn3

__all__ = [
    "Plot",
    "PlotBar",
    "PlotBarh",
    "PlotLine",
    "PlotArea",
    "PlotBubble",
    "PlotStripdot",
    "PlotHist",
    "PlotBoxdot",
    "PlotHeatmap",
    "PlotTreemap",
    "PlotPie",
    "PlotWaffle",
    "PlotFunnel",
    "PlotWordcloud",
    "PlotTable",
    "PlotVenn2",
    "PlotVenn3",
]
