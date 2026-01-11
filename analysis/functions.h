
namespace FCCAnalyses {

Vec_f leptonResolution(Vec_rp leptons, Vec_i recind, Vec_i mcind, Vec_rp reco, Vec_mc mc, int mode=0) {
    Vec_f result;
    result.reserve(leptons.size());
    for(int i = 0; i < leptons.size(); ++i) {
        TLorentzVector reco_;
        reco_.SetXYZM(leptons[i].momentum.x, leptons[i].momentum.y, leptons[i].momentum.z, leptons[i].mass);
        int track_index = leptons[i].tracks_begin;
        int mc_index = FCCAnalyses::ReconstructedParticle2MC::getTrack2MC_index(track_index, recind, mcind, reco);
        if(mc_index >= 0 && mc_index < (int)mc.size()) {
            TLorentzVector mc_;
            mc_.SetXYZM(mc.at(mc_index).momentum.x, mc.at(mc_index).momentum.y, mc.at(mc_index).momentum.z, mc.at(mc_index).mass);
            if(mode == 0) result.push_back((reco_.Pt()-mc_.Pt())/mc_.Pt()); // momentum resolution
            else if(mode == 1) result.push_back((reco_.Theta()-mc_.Theta())/mc_.Theta()); // theta resolution
            else if(mode == 2) result.push_back((reco_.Phi()-mc_.Phi())/mc_.Phi()); // phi resolution
            else if(mode == 3) result.push_back(1./reco_.Pt() - 1./mc_.Pt()); // resolution on curvature k=1/p
        }
    }
    return result;
}


}