



# **Detector Performance – Quick Start Guide**

## **1. Get the Code and Install**
> **Note:** This installation is required **only once**.

```bash
git clone https://github.com/mit-fcc/detector-performance.git
cd detector-performance
chmod 755 bin/install.sh
./bin/install.sh
```



## **2. Setup Environment**
When you open a **fresh terminal**, first source the environment:
```bash
source bin/env.sh
```



## **3. Run Steps Individually**
The workflow consists of several steps that can be run one by one:

```bash
python analysis/run.py --gun # produces HepMC3 events (muons) in bins of theta and momentum
python analysis/run.py --delphes # detector response for the gun events
python analysis/run.py --analysis # loop over events, get track and impact parameters per muon
python analysis/run.py --plots # analyse track/impact resolution plots
python analysis/run.py --summary_plots # plot resolutions vs. cos(theta)
```

All these steps execute the respective tasks for each gun sample, and processes it in a multithreaded way (by default 12 threads are used). The analysis script (in RDataFrame) used is stored in `analysis/analysis.py`. The plotting script and analysis of the resolutions, is stored in `analysis/plots.py`.




## **4. Run All Steps in One Go**
You can run the full chain in a single command:
```bash
python analysis/run.py --gun --delphes --analysis --plots --summary_plots
```

The **full chain** typically takes about **10 minutes** to complete.

## **5. Options**

### **Change Detector Card**
By default, the **IDEA baseline** detector (`IDEA_baseline`) is used, corresponding to the steering file:
```
delphes_cards/IDEA_baseline.tcl
```
You can change it with:
```bash
python analysis/run.py --delphes_card IDEA_SiTracking
```

### **Control Number of Threads**
All steps run with **12 threads** by default. To change:
```bash
python analysis/run.py --nThreads 8
```

### **Change Output Directory**
By default, results are saved in the `output` directory. To specify a custom directory:
```bash
python analysis/run.py --output_dir my_results
```

### **Display commands**
If you want to see what commands are actually invoked, you can just display the commands on the screen without running them:
```bash
python analysis/run.py --delphes --display_commands
```

## **6. Example: Custom Card, Fewer Threads, and Custom Output**
```bash
python analysis/run.py --gun --delphes --analysis --plots --summary_plots \
  --delphes_card IDEA_SiTracking --nThreads 8 --output_dir my_results
```


