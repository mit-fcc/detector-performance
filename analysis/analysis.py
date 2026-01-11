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

bins_d0 = (20000, -10, 10) # range mm, bins um
bins_z0 = (20000, -10, 10) # range mm, bins um

bins_d0_um = (200000, -1000, 1000) # range mm, bins um
bins_z0_um = (200000, -1000, 1000) # range mm, bins um

bins_p = (250, 0, 250)
bins_res_p = (20000, -0.10, 0.10)
bins_res_k = (10000, -0.005, 0.005)


## functions defined here: https://github.com/HEP-FCC/FCCAnalyses/blob/master/analyzers/dataframe/src/myUtils.cc
## vertex fitter: https://indico.cern.ch/event/1003610/contributions/4214579/attachments/2187815/3696958/Bedeschi_Vertexing_Feb2021.pdf
## perf. plots: https://indico.cern.ch/event/965346/contributions/4062989/attachments/2125687/3578824/vertexing.pdf

def analysis(input_file, output_file):

    df = ROOT.RDataFrame("events", input_file)


    df = df.Alias("MCRecoAssociations0", "_Particle_parents.index")
    df = df.Alias("MCRecoAssociations1", "_Particle_daughters.index")
    df = df.Alias("Muons", "Muon_objIdx.index")

    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muons, ReconstructedParticles)")
    df = df.Define("muons_p", "FCCAnalyses::ReconstructedParticle::get_p(muons_all)")
    muon_p = df.Histo1D(("muons_", "", *bins_p), "muons_p")


    # get track resolution (p and k)
    df = df.Define("muon_res_p", "FCCAnalyses::leptonResolution(muons_all, MCRecoAssociations0, MCRecoAssociations1, ReconstructedParticles, Particle, 0)")
    df = df.Define("muon_res_k", "FCCAnalyses::leptonResolution(muons_all, MCRecoAssociations0, MCRecoAssociations1, ReconstructedParticles, Particle, 3)")
    muon_res_p = df.Histo1D(("muon_res_p", "", *bins_res_p), "muon_res_p")
    muon_res_k = df.Histo1D(("muon_res_k", "", *bins_res_k), "muon_res_k")



    # get the track fit parameters
    df = df.Define("RP_TRK_D0", "ReconstructedParticle2Track::getRP2TRK_D0(ReconstructedParticles, _EFlowTrack_trackStates)") # d0 in mm
    df = df.Define("RP_TRK_Z0", "ReconstructedParticle2Track::getRP2TRK_Z0(ReconstructedParticles, _EFlowTrack_trackStates)") # z0 in mm
    df = df.Define("RP_TRK_omega", "ReconstructedParticle2Track::getRP2TRK_omega(ReconstructedParticles, _EFlowTrack_trackStates)")  # rho, in mm-1
    df = df.Define("RP_TRK_phi", "ReconstructedParticle2Track::getRP2TRK_phi(ReconstructedParticles, _EFlowTrack_trackStates)")
    df = df.Define("RP_TRK_tanlambda", "ReconstructedParticle2Track::getRP2TRK_tanLambda(ReconstructedParticles, _EFlowTrack_trackStates)")
    df = df.Define("RP_TRK_D0_um", "RP_TRK_D0 * 1000.0")
    df = df.Define("RP_TRK_Z0_um", "RP_TRK_Z0 * 1000.0")

    # get the errors on the track parameters
    df = df.Define("RP_TRK_D0_cov", "ReconstructedParticle2Track::getRP2TRK_D0_cov(ReconstructedParticles, _EFlowTrack_trackStates)")
    df = df.Define("RP_TRK_Z0_cov", "ReconstructedParticle2Track::getRP2TRK_Z0_cov(ReconstructedParticles, _EFlowTrack_trackStates)")
    df = df.Define("RP_TRK_omega_cov", "ReconstructedParticle2Track::getRP2TRK_omega_cov(ReconstructedParticles, _EFlowTrack_trackStates)")
    df = df.Define("RP_TRK_phi_cov", "ReconstructedParticle2Track::getRP2TRK_phi_cov(ReconstructedParticles, _EFlowTrack_trackStates)")
    df = df.Define("RP_TRK_tanlambda_cov", "ReconstructedParticle2Track::getRP2TRK_tanLambda_cov(ReconstructedParticles, _EFlowTrack_trackStates)")

    h_RP_TRK_D0 = df.Histo1D(("RP_TRK_D0", "", *bins_d0), "RP_TRK_D0")
    h_RP_TRK_Z0 = df.Histo1D(("RP_TRK_Z0", "", *bins_z0), "RP_TRK_Z0")

    h_RP_TRK_D0_um = df.Histo1D(("RP_TRK_D0_um", "", *bins_d0_um), "RP_TRK_D0_um")
    h_RP_TRK_Z0_um = df.Histo1D(("RP_TRK_Z0_um", "", *bins_z0_um), "RP_TRK_Z0_um")

    h_RP_TRK_D0_cov = df.Histo1D(("RP_TRK_D0_cov", "", *bins_d0), "RP_TRK_D0_cov")
    h_RP_TRK_Z0_cov = df.Histo1D(("RP_TRK_Z0_cov", "", *bins_z0), "RP_TRK_Z0_cov")


    # write output
    fout = ROOT.TFile(output_file, "RECREATE")
    h_RP_TRK_D0.Write()
    h_RP_TRK_Z0.Write()
    h_RP_TRK_D0_um.Write()
    h_RP_TRK_Z0_um.Write()
    h_RP_TRK_D0_cov.Write()
    h_RP_TRK_Z0_cov.Write()
    muon_p.Write()
    muon_res_p.Write()
    muon_res_k.Write()
    fout.Close()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="Input file", required=True)
    parser.add_argument("-o", "--output", type=str, help="Output file", required=True)
    args = parser.parse_args()

    logger.info(f"Start analysis on {args.input}")
    analysis(args.input, args.output)
    logger.info(f"Done! Output saved to {args.output}")
