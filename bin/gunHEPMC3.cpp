#include <HepMC3/GenEvent.h>
#include <HepMC3/WriterAscii.h>
#include <HepMC3/GenParticle.h>
#include <HepMC3/FourVector.h>
#include <HepMC3/GenVertex.h>

#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <string>
#include <random>
#include <cmath>

using namespace HepMC3;

#include <random>
#include <cmath>

double get_mass(int pid) {
    // PDG mass values
    std::map<int, double> masses = {
        {211, 0.139570},    // charged pion
        {-211, 0.139570},   // charged pion
        {2212, 0.93827},    // proton
        {-2212, 0.93827},     // proton
        {2112, 0.93957},    // neutron
        {111, 0.13498},     // pi0
        {130, 0.49767},     // Klong
        {310, 0.49767},     // K_S^0
        {11, 0.00051},
        {-11, 0.00051},
        {22, 0.00000},
        {13, 0.10566},
        {-13, 0.10566},
        {213, 0.76690},     //rho(770)^+
        {-213,0.76690 },    //rho(770)^-

    };
    // Return the mass if found, 0 otherwise
    return masses.count(pid) ? masses[pid] : 0;
}

void generate_event(int iEv, WriterAscii& writer, const std::vector<int>& pid_list, 
                    int npart, const std::vector<float>& theta_range, 
                    const std::vector<float>& mom_range) {
    // Create a random number generator
    std::random_device rd;
    std::mt19937 gen(rd());

    // Create a new event
    GenEvent evt(Units::GEV, Units::MM);

    // Create a vertex at the origin
    GenVertexPtr v = std::make_shared<GenVertex>();

    GenParticlePtr p1 = make_shared<GenParticle>(FourVector (0.0,    0.0,   125.0,  125.0  ),11,  3);
    GenParticlePtr p2 = make_shared<GenParticle>(FourVector (0.0,    0.0,   -125.0,  125.0  ),11,  3);

    v->add_particle_in(p1);
    v->add_particle_in(p2);

    // Loop over each particle
    for (int i = 0; i < npart; i++) {
        // Generate random PID
        std::uniform_int_distribution<> pid_dist(0, pid_list.size() - 1);
        int pid = pid_list[pid_dist(gen)];


        // Generate random theta
        std::uniform_real_distribution<> theta_dist(theta_range[0], theta_range[1]);
        float theta = theta_dist(gen) * 2.0*M_PI/360.;

        // Generate random phi
        std::uniform_real_distribution<> phi_dist(-M_PI, M_PI);
        float phi = phi_dist(gen);

        // Create the particle

        // Get the particle mass
        double mass = get_mass(pid);

        // Generate random momentum
        std::uniform_real_distribution<> log_mom_dist(log(mom_range[0]), log(mom_range[1]));
        float momp = exp(log_mom_dist(gen));

         //std::cout<<"  "<<i<<","<<pid<<","<<momp<<","<<etap<<","<<phip<<"\n";
        // Compute px, py, pz, E
        float px = momp * sin(theta) * cos(phi);
        float py = momp * sin(theta) * sin(phi);
        float pz = momp * cos(theta);
        float e = sqrt(px*px + py*py + pz*pz + mass*mass);

        // Create the particle
        GenParticlePtr particle = make_shared<GenParticle>(FourVector(px, py, pz, e), pid, 1);

        // add the particle to the vertex
        //v->add_particle_in(particle);
        v->add_particle_out(particle);

    }

    evt.add_vertex(v);
    evt.set_event_number(iEv);

    // Write the event to the file
    writer.write_event(evt);
}


int main(int argc, char** argv) {
    // Check that the correct number of parameters were passed
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <config file>\n";
        return 1;
    }

    // Open the configuration file
    std::ifstream configFile(argv[1]);
    if (!configFile) {
        std::cerr << "Could not open configuration file " << argv[1] << "\n";
        return 1;
    }

    // extract filename of input file
    std::string filename_str = argv[1];
    size_t slash_pos = filename_str.find_last_of("/\\"); // Find position of last '/' or '\\'
    std::string filename = (slash_pos == std::string::npos) ? filename_str : filename_str.substr(slash_pos + 1);
    size_t dot_pos = filename.find_last_of('.'); // Find last dot
    std::string filename_name_only = (dot_pos == std::string::npos) ? filename : filename.substr(0, dot_pos);


    // Parse the configuration file
    std::map<std::string, std::string> config;
    std::string line;
    while (std::getline(configFile, line)) {
        if (line[0] == '#') continue;
        std::istringstream iss(line);
        std::string key, value;
        if (!(iss >> key >> value)) {
            break;  // error
        }
        config[key] = value;
    }
    
    // Convert nevents from string to int
    float nevents = std::stof(config["nevents"]);

    // Convert npart from string to int
    int npart = std::stof(config["npart"]);

    // Convert theta_range from string to vector<float>
    std::vector<float> theta_range;
    std::istringstream eta_range_stream(config["theta_range"]);
    std::string eta;
    while (std::getline(eta_range_stream, eta, ',')) {
        theta_range.push_back(std::stof(eta));
    }

    // Convert mom_range from string to vector<float>
    std::vector<float> mom_range;
    std::istringstream mom_range_stream(config["mom_range"]);
    std::string mom;
    while (std::getline(mom_range_stream, mom, ',')) {
        mom_range.push_back(std::stof(mom));
    }


    // Convert pid_list from string to vector<int>
    std::vector<int> pid_list;
    std::istringstream pid_list_stream(config["pid_list"]);
    std::string pid;
    while (std::getline(pid_list_stream, pid, ',')) {
        pid_list.push_back(std::stoi(pid));
    }

    // Print the parsed values for debugging
    std::cout << "nevents: " << nevents << "\n";

    // Print the parsed values for debugging
    std::cout << "npart: " << npart << "\n";


    std::cout << "theta_range: ";
    for (float theta : theta_range) {
        std::cout << theta << " ";
    }
    std::cout << "\n";

    std::cout << "mom_range: ";
    for (float mom : mom_range) {
        std::cout << mom << " ";
    }
    std::cout << "\n";

    std::cout << "pid_list: ";
    for (int pid : pid_list) {
        std::cout << pid << " ";
    }
    std::cout << "\n";

    // Open the output file
    WriterAscii writer(filename_name_only + ".hepmc");

    // Generate and write n events
    for (int i = 0; i < nevents; i++) {
        generate_event(i, writer, pid_list, npart, theta_range, mom_range);
    }

    writer.close();  // This will add the "HepMC::Asciiv3-END_EVENT_LISTING" line
    return 0;
}