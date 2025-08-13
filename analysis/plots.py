import argparse
import sys,array,ROOT,math,os,copy
import numpy as np
import json

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


def compute_res(input_file, output_name, hist_name, hist_type, plotGauss=True):

    fIn = ROOT.TFile(input_file)
    hist = fIn.Get(hist_name)

    rebin = 1
    hist = hist.Rebin(rebin)

    probabilities = np.array([0.001, 0.999, 0.84, 0.16], dtype='d')

    # get mean
    mean = hist.GetMean()

    # compute RMS
    rms, rms_err = hist.GetRMS(), hist.GetRMSError()

    # range for plotting
    xMin, xMax = mean - 3*rms, mean + 3*rms

    # compute quantiles
    quantiles = np.array([0.0, 0.0, 0.0, 0.0], dtype='d')
    hist.GetQuantiles(4, quantiles, probabilities)
    #xMin, xMax = min([quantiles[0], -quantiles[1]]), max([-quantiles[0], quantiles[1]])
    res_quantile = 0.5*(quantiles[2] - quantiles[3])



    # fit with Gauss
    gauss = ROOT.TF1("gauss2", "gaus", xMin, xMax)
    gauss.SetParameter(0, hist.Integral())
    gauss.SetParameter(1, hist.GetMean())
    gauss.SetParameter(2, hist.GetRMS())
    gauss.SetLineColor(ROOT.kRed)
    gauss.SetLineWidth(3)
    hist.Fit("gauss2", "R")

    mu, sigma = gauss.GetParameter(1), gauss.GetParameter(2)
    sigma_err = gauss.GetParError(2)


    ## do plotting
    yMin, yMax = 0, 1.3*hist.GetMaximum()
    canvas = ROOT.TCanvas("canvas", "", 1000, 1000)
    canvas.SetTopMargin(0.055)
    canvas.SetRightMargin(0.05)
    canvas.SetLeftMargin(0.15)
    canvas.SetBottomMargin(0.11)

    hist_types = {"d0": "d_{0} (#mum)", "z0": "z_{0} (#mum)", "p": "Momentum resolution (%)", "k": "Curvature resolution (%)"}
    dummy = ROOT.TH1D("h", "h", 1, xMin, xMax)
    dummy.GetXaxis().SetTitle(hist_types[hist_type])
    dummy.GetXaxis().SetRangeUser(xMin, xMax)

    dummy.GetXaxis().SetTitleFont(43)
    dummy.GetXaxis().SetTitleSize(40)
    dummy.GetXaxis().SetLabelFont(43)
    dummy.GetXaxis().SetLabelSize(35)

    dummy.GetXaxis().SetTitleOffset(1.2*dummy.GetXaxis().GetTitleOffset())
    dummy.GetXaxis().SetLabelOffset(1.2*dummy.GetXaxis().GetLabelOffset())

    dummy.GetYaxis().SetTitle("Events / bin")
    dummy.GetYaxis().SetRangeUser(yMin, yMax)
    dummy.SetMaximum(yMax)
    dummy.SetMinimum(yMin)

    dummy.GetYaxis().SetTitleFont(43)
    dummy.GetYaxis().SetTitleSize(40)
    dummy.GetYaxis().SetLabelFont(43)
    dummy.GetYaxis().SetLabelSize(35)

    dummy.GetYaxis().SetTitleOffset(1.7*dummy.GetYaxis().GetTitleOffset())
    dummy.GetYaxis().SetLabelOffset(1.4*dummy.GetYaxis().GetLabelOffset())

    dummy.Draw("HIST")
    hist.Draw("SAME HIST")
    if plotGauss:
        gauss.Draw("SAME")

    canvas.SetGrid()
    ROOT.gPad.SetTickx()
    ROOT.gPad.SetTicky()
    ROOT.gPad.RedrawAxis()

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.035)
    latex.SetTextColor(1)
    latex.SetTextFont(42)
    latex.DrawLatex(0.2, 0.9, f"Mean/RMS = {hist.GetMean():.4f}/{rms:.4f}")
    latex.DrawLatex(0.2, 0.85, f"Resolution = {res_quantile:.4f} %")
    if plotGauss:
        latex.DrawLatex(0.2, 0.80, f"Gauss #mu/#sigma = {mu:.4f}/{sigma:.4f}")

    canvas.SaveAs(f"{output_name}.png")
    canvas.SaveAs(f"{output_name}.pdf")
    canvas.Close()

    del gauss

    data = {}
    data["rms"] = rms
    data["rms_err"] = rms_err
    data["sigma"] = sigma
    data["sigma_err"] = sigma_err
    data["res_quantile"] = res_quantile
    with open(f"{output_name}.json", "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Input file", required=True)
    parser.add_argument("-o", "--output", type=str, help="Output file base name", required=True)
    parser.add_argument("-n", "--histName", type=str, help="Histogram to plot", required=True)
    parser.add_argument("-t", "--type", type=str, help="Type (d0, z0, p or k)", required=True)
    args = parser.parse_args()

    compute_res(args.input, args.output, args.histName, args.type)
