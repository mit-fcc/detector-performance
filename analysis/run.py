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
parser.add_argument("--gun", help="Run gun generation", action='store_true')
parser.add_argument("--delphes", help="Run Delphes", action='store_true')
parser.add_argument("--analysis", help="Run analysis", action='store_true')
parser.add_argument("--plots", help="Run plots", action='store_true')
parser.add_argument("--summary_plots", help="Run summary plots", action='store_true')
parser.add_argument("--display_commands", help="Display commands only, don't run", action='store_true')
parser.add_argument("--delphes_card", type=str, help="Delphes detector card name (as in delphes_cards directory)", default="IDEA_baseline")
parser.add_argument("--output_dir", type=str, help="Output directory", default="output")
parser.add_argument("--nThreads", type=int, help="Number of threads", default=12)
args = parser.parse_args()

current_dir = os.path.abspath(os.getcwd())

pdg_dict = {
    # Quarks
    1: "d",       -1: "d_bar",
    2: "u",       -2: "u_bar",
    3: "s",       -3: "s_bar",
    4: "c",       -4: "c_bar",
    5: "b",       -5: "b_bar",
    6: "t",       -6: "t_bar",
    7: "b'",      -7: "b'_bar",
    8: "t'",      -8: "t'_bar",

    # Leptons
    11:  "e_minus",       -11: "e_plus",
    12:  "nu_minus",      -12: "nu_e_bar",
    13:  "mu_minus",      -13: "mu_plus",
    14:  "nu_mu",         -14: "nu_mu_bar",
    15:  "tau_minus",     -15: "tau_plus",
    16:  "nu_tau",        -16: "nu_tau_bar",
    17:  "tau'_minus",    -17: "tau'_plus",
    18:  "nu_tau'",       -18: "nu_tau'_bar",
}

def generate_gun_cards(input_dir, theta_range, mom_range, pid, nevents = 100000, npart = 1):

    def helper_ranges():
        for theta in theta_range:
            for mom in mom_range:
                yield theta, mom

    def helper_write(theta, mom):
        filename = os.path.join(input_dir, f"{pdg_dict[pid]}_theta_{theta}_p_{mom}.input")
        with open(filename, 'w') as f:
            f.write(f"npart {npart}\n")
            f.write(f"theta_range {theta}.0,{theta}.0\n")
            f.write(f"mom_range {mom}.0,{mom}.0\n")
            f.write(f"pid_list {pid}\n")
            f.write(f"nevents {nevents}\n")

        print(f"Generated {filename}")

    print("Starting gun generator")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.nThreads) as pool:
        for theta, mom in helper_ranges():
            pool.submit(helper_write, theta, mom)
    print(f"All gun input files generated and stored in {input_dir}")


def generate_gun_events(samples_directory, hepmcs_directory):

    gun_singularity_helper = f"{current_dir}/bin/run_gunHEPMC3_singularity.sh" # gun helper
    gun_exe = f"{current_dir}/bin/gunHEPMC3" # gun executable

    def helper_run(input_path):
        """
        $1: directory to cd into (where you want to run the command, so output files go there)
        $2: command to run (./gunHEPMC3)
        $3: argument to that command (input file)
        """
        try:
            cmd = [
                gun_singularity_helper, 
                hepmcs_directory,
                gun_exe,
                input_path
            ]
            if args.display_commands:
                print(' '.join(cmd))
            else:
                subprocess.run(cmd, check=True)

        except Exception as e:
            print(f"Unknown error for {input_path}: {e}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.nThreads) as pool:
        for sample_name in os.listdir(samples_directory):
            pool.submit(helper_run, os.path.join(samples_directory, sample_name))

    print(f"All gun HepMC3 files generated and stored in {hepmcs_directory}")

def detector_response(input_dir, output_dir, delphes_card):

    def helper_response(hepmc):
        filename, _ = os.path.splitext(hepmc)
        cmd = [
            "DelphesHepMC_EDM4HEP",
            delphes_card,
            f"{current_dir}/bin/delphes_output.tcl",
            f"{output_dir}/{filename}.root",
            f"{input_dir}/{hepmc}"
        ]

        if args.display_commands:
            print(' '.join(cmd))
        else:
            subprocess.run(cmd, check=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.nThreads) as pool:
        for gun_hepmc in os.listdir(input_dir):
            pool.submit(helper_response, gun_hepmc)


def analyze(input_dir, output_dir, analysis_script):

    def helper_analyze(sample_name):
        cmd = [
            "python",
            analysis_script,
            "--input",
            f"{input_dir}/{sample_name}",
            "--output",
            f"{output_dir}/{sample_name}"
        ]

        if args.display_commands:
            print(' '.join(cmd))
        else:
            subprocess.run(cmd, check=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.nThreads) as pool:
        for sample_name in os.listdir(input_dir):
            pool.submit(helper_analyze, sample_name)


def plot(input_dir, output_dir, plots_script):

    def helper_plot(sample_name):
        sample_name = sample_name.replace(".root", "")
        for hist_name, hist_type in zip(["RP_TRK_D0_um", "RP_TRK_Z0_um", "muon_res_p", "muon_res_k"], ["d0", "z0", "p", "k"]):
            cmd = [
                "python",
                plots_script,
                "--input",
                f"{input_dir}/{sample_name}.root",
                "--output",
                f"{output_dir}/{hist_type}_{sample_name}",
                "--histName",
                hist_name,
                "--type",
                hist_type
            ]

            if args.display_commands:
                print(' '.join(cmd))
            else:
                subprocess.run(cmd, check=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.nThreads) as pool:
        for sample_name in os.listdir(input_dir):
            pool.submit(helper_plot, sample_name)

def plot_summary(plots_path, theta_ranges, mom_ranges, hist_type):

    xmin, xmax = 0, 1
    ymin, ymax = 9e99, -9e99

    c = ROOT.TCanvas("c", "", 800, 800)
    c.SetTopMargin(0.055)
    c.SetRightMargin(0.05)
    c.SetLeftMargin(0.18)
    c.SetBottomMargin(0.15)
    c.SetLogy()
    c.SetGrid()

    dummy = ROOT.TH1D("dummy", "", 1, 0, 1)
    dummy.SetBinContent(1, -10000)
    dummy.GetXaxis().SetTitle("cos(#theta)")
    dummy.GetXaxis().SetRangeUser(xmin, xmax)
    dummy.GetXaxis().SetTitleFont(43)
    dummy.GetXaxis().SetTitleSize(40)
    dummy.GetXaxis().SetLabelFont(43)
    dummy.GetXaxis().SetLabelSize(35)
    dummy.GetXaxis().SetTitleOffset(1.2*dummy.GetXaxis().GetTitleOffset())
    dummy.GetXaxis().SetLabelOffset(1.2*dummy.GetXaxis().GetLabelOffset())

    hist_types = {"d0": "d_{0} resolution (#mum)", "z0": "z_{0} resolution (#mum)", "p": "Momentum resolution (%)", "k": "Curvature resolution (%)"}
    dummy.GetYaxis().SetTitle(hist_types[hist_type])
    dummy.GetYaxis().SetTitleFont(43)
    dummy.GetYaxis().SetTitleSize(40)
    dummy.GetYaxis().SetLabelFont(43)
    dummy.GetYaxis().SetLabelSize(35)
    dummy.GetYaxis().SetTitleOffset(1.7*dummy.GetYaxis().GetTitleOffset())
    dummy.GetYaxis().SetLabelOffset(1.4*dummy.GetYaxis().GetLabelOffset())

    dummy.Draw("HIST")

    legend = ROOT.TLegend(0.25, 0.65, 0.55, 0.9)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.03)
    legend.SetMargin(0.2)
    legend.SetHeader(f"Delphes {delphes_card_name}")

    colors = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kMagenta+1]
    graphs = []
    for i,mom in enumerate(mom_ranges):
        g = ROOT.TGraph()
        g.SetName(f"mom{mom}")
        g.SetLineColor(colors[i])
        g.SetLineWidth(2)
        g.SetMarkerColor(colors[i])
        g.SetMarkerStyle(20)
        g.SetMarkerSize(1.2)
        g.SetTitle(f"p = {mom} GeV")
        legend.AddEntry(g, f"p = {mom} GeV", "LP")

        for j,theta in enumerate(theta_ranges):
            cost = math.cos(theta*math.pi/180.)
            res = -9e99
            with open(f"{plots_path}/{hist_type}_{pdg_dict[particle_id]}_theta_{theta}_p_{mom}.json") as json_file:
                data = json.load(json_file)
                res = data['res_quantile']
                if res < ymin:
                    ymin = res
                if res > ymax:
                    ymax = res
            g.SetPoint(j, cost, res)
        graphs.append(g)
        g.Draw("LP SAME")

    ymin_decade = 10**np.floor(np.log10(ymin))
    ymax_decade = 10**np.ceil(np.log10(ymax))

    dummy.GetYaxis().SetRangeUser(ymin_decade, ymax_decade)
    dummy.SetMaximum(ymax_decade)
    dummy.SetMinimum(ymin_decade)

    legend.Draw()

    c.Update()
    c.SaveAs(f"{plots_path}/{hist_type}_vs_theta.png")
    c.SaveAs(f"{plots_path}/{hist_type}_vs_theta.pdf")

    fOut = ROOT.TFile(f"{plots_path}/{hist_type}_vs_theta.root", "RECREATE")
    for g in graphs:
        g.Write()
    fOut.Close()

if __name__ == "__main__":

    # configuration of the gun
    theta_ranges = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    mom_ranges = [2, 5, 10, 50, 100]
    particle_id = 13
    nevents = 100000 # number of events
    npart = 1 # particles per event

    output_base_dir = f"{current_dir}/{args.output_dir}"
    delphes_card_name = args.delphes_card
    delphes_card = f"{current_dir}/delphes_cards/{delphes_card_name}.tcl"
    if not delphes_card:
        print(f"ERROR: Delphes card {delphes_card_name} does not exist")
        quit()

    gun_path = f"{output_base_dir}/cards/"
    hepmc_path = f"{output_base_dir}/hepmc3/"
    delphes_path = f"{output_base_dir}/delphes_{delphes_card_name}/"
    analysis_path = f"{output_base_dir}/analysis_{delphes_card_name}/"
    plots_path = f"{output_base_dir}/plots_{delphes_card_name}/"

    if args.gun:
        os.makedirs(gun_path, exist_ok=True)
        os.makedirs(hepmc_path, exist_ok=True)
        generate_gun_cards(gun_path, theta_range=theta_ranges, mom_range=mom_ranges, pid=particle_id, nevents=nevents, npart=npart)
        generate_gun_events(gun_path, hepmc_path)

    if args.delphes:
        os.makedirs(delphes_path, exist_ok=True)
        detector_response(hepmc_path, delphes_path, delphes_card)


    if args.analysis:
        os.makedirs(analysis_path, exist_ok=True)
        analysis_script = f"{current_dir}/analysis/analysis.py"
        analyze(delphes_path, analysis_path, analysis_script)

    if args.plots:
        os.makedirs(plots_path, exist_ok=True)
        plots_script = f"{current_dir}/analysis/plots.py"
        plot(analysis_path, plots_path, plots_script)

    if args.summary_plots:
        os.makedirs(plots_path, exist_ok=True)
        plot_summary(plots_path, theta_ranges, mom_ranges, 'd0')
        plot_summary(plots_path, theta_ranges, mom_ranges, 'z0')
        plot_summary(plots_path, theta_ranges, mom_ranges, 'p')
        plot_summary(plots_path, theta_ranges, mom_ranges, 'k')

