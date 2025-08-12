import argparse
import sys, os, glob, math
import ROOT
import logging

logging.basicConfig(format='%(levelname)s: %(message)s')
logger = logging.getLogger("fcclogger")
logger.setLevel(logging.INFO)


ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

ROOT.EnableImplicitMT() # use all cores
ROOT.DisableImplicitMT() # single core

# load libraries
ROOT.gSystem.Load("libFCCAnalyses")
fcc_loaded = ROOT.dummyLoader()
ROOT.gInterpreter.Declare("using namespace FCCAnalyses;")
ROOT.gInterpreter.Declare(f'#include "{os.path.dirname(os.path.realpath(__file__))}/functions.h"')

bins_p = (250, 0, 250)
bins_res_p = (10000, -0.05, 0.05)
bins_res_k = (10000, -0.005, 0.005)

def analysis(input_file, output_file):

    df = ROOT.RDataFrame("events", input_file)

    df = df.Alias("MCRecoAssociations0", "_MCRecoAssociations_rec.index")
    df = df.Alias("MCRecoAssociations1", "_MCRecoAssociations_sim.index")
    df = df.Alias("Muons", "Muon_objIdx.index")

    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muons, ReconstructedParticles)")
    df = df.Define("muons_p", "FCCAnalyses::ReconstructedParticle::get_p(muons_all)")

    muons_p = df.Histo1D(("muons_p", "", *bins_p), "muons_p")


    # get resolutions
    df = df.Define("muons_res_p", "FCCAnalyses::leptonResolution(muons_all, MCRecoAssociations0, MCRecoAssociations1, ReconstructedParticles, Particle, 0)")
    df = df.Define("muons_res_k", "FCCAnalyses::leptonResolution(muons_all, MCRecoAssociations0, MCRecoAssociations1, ReconstructedParticles, Particle, 3)")
    muons_res_p = df.Histo1D(("muons_res_p", "", *bins_res_p), "muons_res_p")
    muons_res_k = df.Histo1D(("muons_res_k", "", *bins_res_k), "muons_res_k")


    fout = ROOT.TFile(output_file, "RECREATE")
    muons_p.Write()
    muons_res_p.Write()
    muons_res_k.Write()
    fout.Close()





if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Input file", required=True)
    parser.add_argument("-o", "--output", type=str, help="Output file", required=True)
    args = parser.parse_args()

    logger.info(f"Start analysis on {args.input}")
    analysis(args.input, args.output)
    logger.info(f"Done! Output saved to {args.output}")
