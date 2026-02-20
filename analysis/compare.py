import concurrent.futures
import os
import subprocess
import shutil
import argparse
import math
import json
import numpy as np

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

parser = argparse.ArgumentParser()
parser.add_argument("--card1", type=str, help="First card", default="IDEA_baseline")
parser.add_argument("--card2", type=str, help="Second card", default="IDEA_baseline_3T")
parser.add_argument("--output", type=str, help="Output", default="output")
args = parser.parse_args()

current_dir = os.path.abspath(os.getcwd())

def ratio_tgraphs(g1, g2, name="ratio_graph"):
    """Return a new TGraph that is the ratio g1/g2"""
    n1 = g1.GetN()
    n2 = g2.GetN()
    if n1 != n2:
        raise ValueError("Graphs have different number of points")

    x1 = g1.GetX()
    y1 = g1.GetY()
    x2 = g2.GetX()
    y2 = g2.GetY()

    miny, maxy = 1e99, -1e99

    #ratio_graph = ROOT.TGraph()
    #ratio_graph.SetName(name)
    ratio_graph = g1.Clone(name)

    for i in range(n1):
        x = x1[i]
        if x != x2[i]:
            raise ValueError(f"x values differ at index {i}: {x} vs {x2[i]}")
        if y2[i] != 0:
            ratio = y2[i] / y1[i]
            ratio_graph.SetPoint(i, x, ratio)
            if ratio > maxy:
                maxy = ratio
            if ratio < miny:
                miny = ratio
        else:
            ratio_graph.SetPoint(i, x, 0)  # or float('nan')

    return ratio_graph, miny, maxy

def make_plot(card1, card2, output, hist_type):

    output_base_dir = f"{current_dir}/{output}"
    plots_path_card1 = f"{output_base_dir}/plots_{card1}/"
    plots_path_card2 = f"{output_base_dir}/plots_{card2}/"

    xmin, xmax = 0, 1
    ymin, ymax = 1e99, -1e99
    yminr, ymaxr = 1e99, -1e99

    ratiofraction = 0.35
    epsilon = 0.025
    c = ROOT.TCanvas("c", "c", 800, 800)
    c.SetTopMargin(0.0)
    c.SetRightMargin(0.0)
    c.SetBottomMargin(0.0)
    c.SetLeftMargin(0.0)

    pad1 = ROOT.TPad("p1","p1", 0, ratiofraction, 1, 1)
    pad2 = ROOT.TPad("p2","p2", 0, 0.0, 1, ratiofraction-0.7*epsilon)

    pad1.SetBottomMargin(epsilon)
    pad1.SetTopMargin(0.055/(1.-ratiofraction))
    pad1.SetRightMargin(0.05)
    pad1.SetLeftMargin(0.18)
    #pad1.SetFrameLineWidth(2)

    pad2.SetBottomMargin(0.37)
    pad2.SetTopMargin(0.0)
    pad2.SetRightMargin(0.05)
    pad2.SetLeftMargin(0.18)
    #pad2.SetFrameLineWidth(2)


    pad1.SetLogy()
    pad1.SetGrid()
    pad2.SetGrid()

    c.Modify()
    c.Update()


    # dummy
    dummyT = ROOT.TH1D("h1", "h", 1, xmin, xmax)
    dummyB = ROOT.TH1D("h2", "h", 1, xmin, xmax)


    # x-axis
    dummyB.GetXaxis().SetTitle("cos(#theta)")
    dummyT.GetXaxis().SetRangeUser(xmin, xmax)
    dummyB.GetXaxis().SetRangeUser(xmin, xmax)

    dummyT.GetXaxis().SetTitleFont(43)
    dummyT.GetXaxis().SetTitleSize(0)
    dummyT.GetXaxis().SetLabelFont(43)
    dummyT.GetXaxis().SetLabelSize(0)

    dummyT.GetXaxis().SetTitleOffset(1.2*dummyT.GetXaxis().GetTitleOffset())
    dummyT.GetXaxis().SetLabelOffset(1.2*dummyT.GetXaxis().GetLabelOffset())

    dummyB.GetXaxis().SetTitleFont(43)
    dummyB.GetXaxis().SetTitleSize(32)
    dummyB.GetXaxis().SetLabelFont(43)
    dummyB.GetXaxis().SetLabelSize(28)

    dummyB.GetXaxis().SetTitleOffset(1.0*dummyB.GetXaxis().GetTitleOffset())
    dummyB.GetXaxis().SetLabelOffset(3.0*dummyB.GetXaxis().GetLabelOffset())

    # y-axis
    hist_types = {"d0": "d_{0} resolution (#mum)", "z0": "z_{0} resolution (#mum)", "p": "Momentum resolution (%)", "k": "Curvature resolution (%)"}
    dummyT.GetYaxis().SetTitle(hist_types[hist_type])
    dummyB.GetYaxis().SetTitle("Ratio")

    dummyT.GetYaxis().SetRangeUser(ymin, ymax)
    dummyT.SetMaximum(ymax)
    dummyT.SetMinimum(ymin)



    dummyT.GetYaxis().SetTitleFont(43)
    dummyT.GetYaxis().SetTitleSize(32)
    dummyT.GetYaxis().SetLabelFont(43)
    dummyT.GetYaxis().SetLabelSize(28)

    dummyT.GetYaxis().SetTitleOffset(1.3) # 1.7*dummyT.GetYaxis().GetTitleOffset()
    dummyT.GetYaxis().SetLabelOffset(1.4*dummyT.GetYaxis().GetLabelOffset())

    dummyB.GetYaxis().SetTitleFont(43)
    dummyB.GetYaxis().SetTitleSize(32)
    dummyB.GetYaxis().SetLabelFont(43)
    dummyB.GetYaxis().SetLabelSize(28)

    dummyB.GetYaxis().SetTitleOffset(1.7*dummyB.GetYaxis().GetTitleOffset()) 
    dummyB.GetYaxis().SetLabelOffset(1.4*dummyB.GetYaxis().GetLabelOffset())
    dummyB.GetYaxis().SetNdivisions(505)
    
    line = ROOT.TLine(xmin, 1, xmax, 1)
    line.SetLineColor(ROOT.kRed)
    line.SetLineWidth(2)

    c.cd()
    pad1.Draw()
    pad1.cd()
    pad1.SetGrid()
    dummyT.Draw("HIST")

    legend = ROOT.TLegend(0.25, 0.45, 0.55, 0.9)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.03)
    legend.SetMargin(0.2)
    #legend.SetNColumns(2)
    #legend.SetHeader(f"Delphes {delphes_card_name}")
    graphs_ratios = []

    # open graphs of the first card
    fIn = ROOT.TFile(f"{plots_path_card1}/{hist_type}_vs_theta.root")
    graphs_card1 = []
    for ig, key in enumerate(fIn.GetListOfKeys()):
        obj = key.ReadObj()
        if obj.InheritsFrom("TGraph"):
            obj.SetMarkerStyle(20)
            obj.SetMarkerSize(1.2)
            obj.SetName(obj.GetName() + "card1")
            graphs_card1.append(obj)
            legend.AddEntry(obj, f"{obj.GetTitle()} {card1}", "LP")
            n = obj.GetN()
            y = np.array(obj.GetY(), dtype=float)
            ymin_g, ymax_g = np.min(y), np.max(y)
            if ymin_g < ymin:
                ymin = ymin_g
            if ymax_g > ymax:
                ymax = ymax_g

    # open graphs of the second card
    fIn = ROOT.TFile(f"{plots_path_card2}/{hist_type}_vs_theta.root")
    graphs_card2 = []
    for ig, key in enumerate(fIn.GetListOfKeys()):
        obj = key.ReadObj()
        if obj.InheritsFrom("TGraph"):
            print(obj.GetName())
            obj.SetMarkerStyle(22)
            obj.SetMarkerSize(1.2)
            obj.SetName(obj.GetName() + "card2")
            graphs_card2.append(obj)
            legend.AddEntry(obj, f"{obj.GetTitle()} {card2}", "LP")
            n = obj.GetN()
            y = np.array(obj.GetY(), dtype=float)
            ymin_g, ymax_g = np.min(y), np.max(y)
            if ymin_g < ymin:
                ymin = ymin_g
            if ymax_g > ymax:
                ymax = ymax_g

            # compute the ratio w.r.t. first card
            g_ratio, miny, maxy = ratio_tgraphs(graphs_card1[ig], graphs_card2[ig], obj.GetName() + "ratio")
            graphs_ratios.append(g_ratio)
            if miny < yminr:
                yminr = miny
            if maxy > ymaxr:
                ymaxr = maxy

    for g in graphs_card1:
        g.Draw("LP")
    for g in graphs_card2:
        g.Draw("LP")


    ymin_decade = 10**np.floor(np.log10(ymin))
    ymax_decade = 10**np.ceil(np.log10(ymax))

    dummyT.GetYaxis().SetRangeUser(ymin_decade, ymax_decade)
    dummyT.SetMaximum(ymax_decade)
    dummyT.SetMinimum(ymin_decade)

    legend.Draw()

    ## bottom panel
    c.cd()
    pad2.Draw()
    pad2.SetFillStyle(0)
    pad2.cd()
    dummyB.GetYaxis().SetRangeUser(yminr*0.95, ymaxr*1.05)
    dummyB.SetMaximum(ymaxr*1.05)
    dummyB.SetMinimum(yminr*0.95)
    dummyB.Draw("HIST")

    line.Draw("SAME")
    for g in graphs_ratios:
        g.Draw("LP")

    ROOT.gPad.SetTickx()
    ROOT.gPad.SetTicky()
    ROOT.gPad.RedrawAxis()

    c.Update()
    c.SaveAs(f"{output}/{card1}_{card2}_{hist_type}_vs_theta.png")
    c.SaveAs(f"{output}/{card1}_{card2}_{hist_type}_vs_theta.pdf")


if __name__ == "__main__":

    card1 = args.card1
    card2 = args.card2
    output = args.output

    make_plot(card1, card2, output, "d0")
    make_plot(card1, card2, output, "z0")
    make_plot(card1, card2, output, "p")
    make_plot(card1, card2, output, "k")


