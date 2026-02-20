
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

Vec_f get_D0_gen(Vec_rp leptons, Vec_i recind, Vec_i mcind, Vec_rp reco, Vec_mc mc, int mode=0) {
    Vec_f result;
    result.reserve(leptons.size());
    for(int i = 0; i < leptons.size(); ++i) {
        int track_index = leptons[i].tracks_begin;
        int mc_index = FCCAnalyses::ReconstructedParticle2MC::getTrack2MC_index(track_index, recind, mcind, reco);
        if(mc_index >= 0 && mc_index < (int)mc.size()) {
            float d0 = std::sqrt(mc.at(mc_index).vertex.x*mc.at(mc_index).vertex.x + mc.at(mc_index).vertex.y*mc.at(mc_index).vertex.y);
            result.push_back(d0);
            
        }
    }
    return result;
}

Vec_f get_Z0_gen(Vec_rp leptons, Vec_i recind, Vec_i mcind, Vec_rp reco, Vec_mc mc, int mode=0) {
    Vec_f result;
    result.reserve(leptons.size());
    for(int i = 0; i < leptons.size(); ++i) {
        int track_index = leptons[i].tracks_begin;
        int mc_index = FCCAnalyses::ReconstructedParticle2MC::getTrack2MC_index(track_index, recind, mcind, reco);
        if(mc_index >= 0 && mc_index < (int)mc.size()) {
            float z0 = mc.at(mc_index).vertex.z;
            result.push_back(z0);
        }
    }
    return result;
}


Vec_tlv makeLorentzVectors(Vec_rp in) {
    Vec_tlv result;
    for(auto & p: in) {
        TLorentzVector tlv;
        tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
        result.push_back(tlv);
    }
    return result;
}


Vec_f get_gen_vtx(Vec_mc mc) {
    Vec_f result;
    for(auto & p: mc) {
        if(p.PDG == 443) {
            result.push_back(p.vertex.x);
            result.push_back(p.vertex.y);
            result.push_back(p.vertex.z);
        }
    }
    return result;
}

static inline int sgn(double x) {
  return (x > 0.0) - (x < 0.0);   // returns +1, 0, or -1
}

Vec_f calculate_d0_z0_gen(Vec_mc mc, Vec_f Bz) {

    //cout << "calculate_d0_z0_gen **************************************************" << endl;
    Vec_f result;
    float Bz_T = Bz[0];

    auto mcp = mc[2];

    double x_mm = mcp.vertex.x;
    double y_mm = mcp.vertex.y;
    double z_mm = mcp.vertex.z;
    double px_GeV = mcp.momentum.x;
    double py_GeV = mcp.momentum.y;
    double pz_GeV = mcp.momentum.z;
    int q = mcp.charge;

    // Position vector
    TVector3 vtx(x_mm, y_mm, z_mm);

    // Momentum vector
    TVector3 p(px_GeV, py_GeV, pz_GeV);

    //cout << " PHI " << vtx.Phi() <<  "  " << p.Phi() << endl;
    //cout << " VTX " << x_mm <<  "  " << y_mm <<  "  " << z_mm << " " << std::sqrt(x_mm*x_mm + y_mm*y_mm) << endl;
    if(vtx.Phi() > -M_PI && vtx.Phi() < -0.5*M_PI) cout << "THIRD QUAD" << endl;

    double xref_mm=0.0;
    double yref_mm=0.0;
    double zref_mm=0.0;
           
    //cout << std::sqrt(x_mm*x_mm + y_mm*y_mm) << endl;
    const double pT = std::hypot(px_GeV, py_GeV);
    // straight-line fallback if pT~0 or B~0
    if (pT < 1e-9 || std::abs(Bz_T) < 1e-12) {
        // PCA to ref in transverse plane for a line is more work; for your muons pT>0 and B!=0.
        result.push_back(0.0);
        result.push_back(z_mm - zref_mm);
        return result;
    }

    const double tx = px_GeV / pT;
    const double ty = py_GeV / pT;

    // curvature sign s = sign(q*Bz)
    const double s = sgn(double(q) * Bz_T);

    // radius in mm: R = (pT / (0.3|q|B)) * 1000
    const double R_mm = (pT / (0.3 * std::abs(double(q) * Bz_T))) * 1000.0;

    // center of circle in xy
    const double xc = x_mm + s * R_mm * (-ty);
    const double yc = y_mm + s * R_mm * ( tx);

    // vector center -> ref
    const double dxC = xc - xref_mm;
    const double dyC = yc - yref_mm;
    const double Dc  = std::hypot(dxC, dyC);

    // PCA point on circle closest to ref
    const double xP = xc - R_mm * (dxC / Dc);
    const double yP = yc - R_mm * (dyC / Dc);

    // unsigned d0 is distance ref -> PCA
    const double d0_abs = std::hypot(xP - xref_mm, yP - yref_mm);

    // tangent at PCA to get signed d0
    const double ux = (xP - xc) / R_mm;
    const double uy = (yP - yc) / R_mm;
    const double tpx = s * (-uy);
    const double tpy = s * ( ux);

    const double rx = (xP - xref_mm);
    const double ry = (yP - yref_mm);
    const double cross_z = tpx*ry - tpy*rx; // (t x r)_z
    double d0 = - sgn(cross_z) * d0_abs; // should be opposite sign to be correct -- what is the convention in Delphes?

    // compute z at PCA via phase advance along circle
    double phi0 = std::atan2(y_mm - yc, x_mm - xc);
    double phi1 = std::atan2(yP  - yc, xP  - xc);
    double dphi = phi1 - phi0;

    // enforce motion direction: rot = -s
    const double rot = -s;
    // shift by 2pi so that rot*dphi >= 0, picking the nearest equivalent
    const double twopi = 2.0*M_PI;
    while (rot*dphi < 0.0) {
        dphi += (rot > 0 ? +twopi : -twopi);
    }
    // keep within [-2pi,2pi] (optional safety)
    if (dphi >  twopi) dphi -= twopi;
    if (dphi < -twopi) dphi += twopi;

    const double dz = R_mm * dphi * (pz_GeV / pT);
    const double zP = z_mm + dz;

    const double z0 = zP - zref_mm;

    //cout << d0 <<  " " << z0 << endl;
    //if(vtx.Phi() > -M_PI && vtx.Phi() < -0.5*M_PI) d0 = 0;

    result.push_back(d0);
    result.push_back(z0);
    
    
    return result;
}


}