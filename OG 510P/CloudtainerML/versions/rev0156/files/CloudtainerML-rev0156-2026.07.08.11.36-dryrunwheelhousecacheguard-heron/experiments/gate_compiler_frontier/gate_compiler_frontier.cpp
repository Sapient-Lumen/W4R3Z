// CloudtainerML rev0042 — gate compiler frontier repair.
//
// The rev0038/0039 source accidentally made `validation_topk_budget` identical
// to `topk_budget3`. This repair removes the duplicate branch. The validation
// compiler now chooses among distinct hard-mask compilers on a held-out
// calibration split, then applies the chosen compiler to an unseen synthetic row.
#include <bits/stdc++.h>
using namespace std;

#ifndef SOURCE_SHA256
#define SOURCE_SHA256 "unknown"
#endif
#ifndef BUILD_COMMAND
#define BUILD_COMMAND "unknown"
#endif

static string q(const string& s){ string o="\""; for(char c:s){ if(c=='\"'||c=='\\'){o+='\\';o+=c;} else if(c=='\n') o+="\\n"; else o+=c; } return o+'\"'; }
static double C(double x){ return max(0.0, min(1.0, x)); }

struct EdgeScore{ int edge; bool truth; double score; };
struct Regime{ string name; double true_mu,false_mu,true_sd,false_sd,false_spike,shrink,val_noise,cost_pressure; };
struct Metrics{ int selected=0,tp=0,fp=0,fn=0; double precision=0,recall=0,f1=0,reachable=0,miss=0,cost=0,calibration_error=0,rank_quality=0,score=0; };
struct Row{ string regime,method,chosen_policy; int seed,selected,tp,fp,fn; double precision,recall,f1,reachable,miss,cost,calibration_error,rank_quality,validation_score,regret,score; };

static vector<string> base_policies(){
    return {"threshold_0p5","threshold_0p2","topk_budget3","gap_knee","uncertainty_band_keep","cost_capped_topk5"};
}

static vector<EdgeScore> make_edges(const Regime& r, int seed){
    mt19937 gen(seed);
    normal_distribution<double> nt(r.true_mu,r.true_sd), nf(r.false_mu,r.false_sd);
    uniform_real_distribution<double> unif(0,1);
    vector<EdgeScore> v; int n_true=3, n_false=9;
    for(int i=0;i<n_true;i++){ double s=r.shrink*nt(gen); v.push_back({i,true,C(s)}); }
    for(int i=0;i<n_false;i++){
        double s=nf(gen);
        if(unif(gen)<r.false_spike) s=max(s, r.true_mu + 0.12 + 0.2*unif(gen));
        s=r.shrink*s; v.push_back({n_true+i,false,C(s)});
    }
    return v;
}

static vector<int> select_edges(vector<EdgeScore> v, const string& policy){
    vector<int> out; int N=v.size();
    if(policy=="threshold_0p5"){
        for(auto& e:v) if(e.score>=0.5) out.push_back(e.edge);
    } else if(policy=="threshold_0p2"){
        for(auto& e:v) if(e.score>=0.2) out.push_back(e.edge);
    } else if(policy=="topk_budget3"){
        sort(v.begin(),v.end(),[](auto&a,auto&b){return a.score>b.score;});
        for(int i=0;i<min(3,N);++i) out.push_back(v[i].edge);
    } else if(policy=="gap_knee"){
        sort(v.begin(),v.end(),[](auto&a,auto&b){return a.score>b.score;});
        int bestk=1; double bestgap=-1;
        for(int i=1;i<N;i++){ double gap=v[i-1].score-v[i].score; if(gap>bestgap){bestgap=gap; bestk=i;} }
        for(int i=0;i<bestk;i++) out.push_back(v[i].edge);
    } else if(policy=="uncertainty_band_keep"){
        for(auto& e:v) if(e.score>=0.45 || (e.score>=0.16 && e.score<=0.32)) out.push_back(e.edge);
    } else if(policy=="cost_capped_topk5"){
        sort(v.begin(),v.end(),[](auto&a,auto&b){return a.score>b.score;});
        for(int i=0;i<min(5,N);++i) out.push_back(v[i].edge);
    } else if(policy=="oracle_true_edges"){
        for(auto& e:v) if(e.truth) out.push_back(e.edge);
    }
    return out;
}

static Metrics score_selection(const Regime& r, const vector<EdgeScore>& v, const vector<int>& sel){
    Metrics m; set<int> S(sel.begin(),sel.end()); m.selected=sel.size();
    double true_mean=0,false_mean=0; int tc=0,fc=0;
    for(auto& e:v){
        if(e.truth){ tc++; true_mean+=e.score; if(S.count(e.edge)) m.tp++; else m.fn++; }
        else { fc++; false_mean+=e.score; if(S.count(e.edge)) m.fp++; }
    }
    true_mean/=max(1,tc); false_mean/=max(1,fc);
    m.precision=m.tp/(double)max(1,m.tp+m.fp);
    m.recall=m.tp/(double)max(1,m.tp+m.fn);
    m.f1=(2*m.precision*m.recall)/max(1e-9,m.precision+m.recall);
    m.reachable=(m.tp==3?1.0:(m.tp==2?0.60:(m.tp==1?0.25:0.0)));
    m.cost=sel.size()/12.0;
    m.calibration_error=fabs(true_mean-0.85)+0.55*fabs(false_mean-0.08);
    m.rank_quality=C((true_mean-false_mean+0.30)/0.95);
    m.miss=1.0-m.reachable + 0.15*m.fp/9.0 + r.val_noise*(1.0-m.rank_quality)*0.25;
    m.score=1.25*m.reachable + 0.18*m.f1 + 0.10*m.rank_quality - r.cost_pressure*0.22*m.cost - 0.18*m.miss - 0.04*m.calibration_error;
    return m;
}

static Metrics eval_policy(const Regime& r, int seed, const string& policy){
    auto v=make_edges(r,seed); auto sel=select_edges(v,policy); return score_selection(r,v,sel);
}

static string choose_on_validation(const Regime& r, int test_seed, double* out_score){
    string best="topk_budget3"; double best_score=-1e300;
    auto policies=base_policies();
    for(const string& pol:policies){
        double s=0.0;
        // A deterministic calibration split not sharing the test seed. Labels are allowed here
        // because this is an explicitly supervised compiler-choice step.
        for(int i=0;i<18;i++){
            int val_seed=910000 + 1009*(int)r.name.size() + 37*i + (test_seed%17);
            s += eval_policy(r,val_seed,pol).score;
        }
        s/=18.0;
        // Account for the policy-search tax so validation cannot look free.
        s -= 0.012*policies.size();
        if(s>best_score){ best_score=s; best=pol; }
    }
    if(out_score) *out_score=best_score;
    return best;
}

static Row eval_method(const Regime& r, int seed, const string& method){
    string policy=method; double val_score=0.0;
    if(method=="validation_selected") policy=choose_on_validation(r,seed,&val_score);
    else if(method=="oracle_true_edges") val_score=0.0;
    else val_score=numeric_limits<double>::quiet_NaN();
    Metrics m=eval_policy(r,seed,policy);
    return {r.name,method,policy,seed,m.selected,m.tp,m.fp,m.fn,m.precision,m.recall,m.f1,m.reachable,m.miss,m.cost,m.calibration_error,m.rank_quality,val_score,0.0,m.score};
}

int main(int argc,char**argv){
    string out = argc>1?argv[1]:"artifacts/probe-results/REV0042_GATE_COMPILER_FRONTIER_REPAIR_SMOKE.json";
    vector<Regime> regimes={
        {"well_calibrated_separated",0.86,0.07,0.06,0.05,0.02,1.00,0.05,0.7},
        {"l1_shrunken_rank_good",0.28,0.03,0.04,0.025,0.00,1.00,0.05,0.9},
        {"soft_solved_all_low",0.18,0.02,0.035,0.018,0.00,1.00,0.08,1.1},
        {"false_spike_noisy",0.75,0.10,0.12,0.07,0.28,1.00,0.12,0.8},
        {"underconfident_but_ranked",0.42,0.14,0.05,0.04,0.04,0.80,0.07,1.0},
        {"ambiguous_close_scores",0.55,0.42,0.08,0.08,0.10,1.00,0.18,0.6},
        {"overactive_false_edges",0.82,0.32,0.08,0.16,0.20,1.00,0.10,1.2}
    };
    vector<string> methods=base_policies(); methods.push_back("validation_selected"); methods.push_back("oracle_true_edges");
    vector<Row> rows; map<string,int> wins, nonoracle_wins, exact_misses, validation_policy_counts;
    map<string,double> score_sum, regret_sum; map<string,int> n_by_method;
    for(const auto& r:regimes){
        for(int seed=0; seed<48; ++seed){
            int test_seed=1000*seed+(int)r.name.size();
            vector<Row> cand; for(const auto& m:methods) cand.push_back(eval_method(r,test_seed,m));
            double best=-1e99; for(auto& x:cand) best=max(best,x.score);
            auto bw=max_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); wins[bw->method]++;
            auto bn=max_element(cand.begin(),cand.end(),[](auto&a,auto&b){
                bool ao=(a.method=="oracle_true_edges"), bo=(b.method=="oracle_true_edges");
                if(ao!=bo) return ao; return a.score<b.score;
            }); nonoracle_wins[bn->method]++;
            for(auto& x:cand){
                x.regret=max(0.0,best-x.score); if(x.reachable<1.0) exact_misses[x.method]++;
                if(x.method=="validation_selected") validation_policy_counts[x.chosen_policy]++;
                score_sum[x.method]+=x.score; regret_sum[x.method]+=x.regret; n_by_method[x.method]++;
                rows.push_back(x);
            }
        }
    }
    ofstream f(out); f<<fixed<<setprecision(6);
    f << "{\n  \"project\":\"CloudtainerML\",\n  \"revision\":\"rev0042\",\n  \"probe\":\"gate_compiler_frontier_repair\",\n  \"kind\":\"native_cxx_probe\",\n";
    f << "  \"source_ids\":[\"SRC-0348\",\"SRC-0356\",\"SRC-0357\"],\n  \"cell_ids\":[\"CELL-350\"],\n";
    f << "  \"repair_of\":\"rev0038_validation_topk_budget_duplicate_branch\",\n";
    f << "  \"run_provenance\":{\"source_path\":\"experiments/gate_compiler_frontier/gate_compiler_frontier.cpp\",\"source_sha256\":"<<q(SOURCE_SHA256)<<",\"build_command\":"<<q(BUILD_COMMAND)<<",\"validation_policy\":\"held-out calibration labels choose among distinct compiler policies before test evaluation\"},\n";
    f << "  \"summary\":{\n    \"primary_metric\":{\"name\":\"score\",\"direction\":\"higher_is_better\"},\n";
    auto dump_map_int=[&](const map<string,int>& m){ bool first=true; f<<"{"; for(auto&kv:m){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<kv.second;} f<<"}"; };
    f << "    \"winner_counts\":"; dump_map_int(wins); f << ",\n";
    f << "    \"nonoracle_winner_counts\":"; dump_map_int(nonoracle_wins); f << ",\n";
    f << "    \"exact_miss_counts\":"; dump_map_int(exact_misses); f << ",\n";
    f << "    \"validation_selected_policy_counts\":"; dump_map_int(validation_policy_counts); f << ",\n";
    f << "    \"mean_score\":{"; bool first=true; for(auto&kv:score_sum){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<(kv.second/max(1,n_by_method[kv.first])); } f << "},\n";
    f << "    \"mean_regret\":{"; first=true; for(auto&kv:regret_sum){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<(kv.second/max(1,n_by_method[kv.first])); } f << "},\n";
    f << "    \"guard_fields\":[\"chosen_policy\",\"validation_score\",\"reachable\",\"miss\",\"selected\",\"tp\",\"fp\",\"fn\",\"calibration_error\",\"rank_quality\",\"regret\",\"cost\"],\n";
    f << "    \"interpretation\":\"validation_selected is now behaviorally distinct: it chooses among threshold, Top-K, knee, uncertainty-band, and cost-capped compilers using a held-out calibration split, then applies that compiler to test rows. It is not a promotion claim; it is a repaired comparison surface.\"\n  },\n";
    f << "  \"rows\":[\n";
    for(size_t i=0;i<rows.size();++i){ const auto&r=rows[i];
        f << "    {\"regime\":"<<q(r.regime)<<",\"method\":"<<q(r.method)<<",\"chosen_policy\":"<<q(r.chosen_policy)
          <<",\"seed\":"<<r.seed<<",\"selected\":"<<r.selected<<",\"tp\":"<<r.tp<<",\"fp\":"<<r.fp<<",\"fn\":"<<r.fn
          <<",\"precision\":"<<r.precision<<",\"recall\":"<<r.recall<<",\"f1\":"<<r.f1<<",\"reachable\":"<<r.reachable
          <<",\"miss\":"<<r.miss<<",\"cost\":"<<r.cost<<",\"calibration_error\":"<<r.calibration_error<<",\"rank_quality\":"<<r.rank_quality
          <<",\"validation_score\":"<<(isnan(r.validation_score)?0.0:r.validation_score)<<",\"regret\":"<<r.regret<<",\"score\":"<<r.score<<"}" << (i+1==rows.size()?"\n":",\n");
    }
    f << "  ]\n}\n";
    cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n";
    return 0;
}
