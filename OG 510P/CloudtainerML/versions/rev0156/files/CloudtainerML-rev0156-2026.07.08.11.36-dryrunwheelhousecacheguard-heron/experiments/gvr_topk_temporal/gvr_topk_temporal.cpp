// CloudtainerML rev0042 — de-oracled temporal Top-K / GVR repair.
//
// The rev0039 toy used true current Top-K membership to decide whether the GVR
// candidate set was safe. This version deliberately separates selection from
// evaluation: candidate certification can only use score values observed by the
// method itself. True Top-K is computed only after selection for scoring rows.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

#ifndef SOURCE_SHA256
#define SOURCE_SHA256 "unknown"
#endif
#ifndef BUILD_COMMAND
#define BUILD_COMMAND "unknown"
#endif

static string q(const string& s){
    string o="\"";
    for(char c:s){
        if(c=='\"'||c=='\\') { o+='\\'; o+=c; }
        else if(c=='\n') o += "\\n";
        else o += c;
    }
    o += "\"";
    return o;
}

static vector<int> topk_indices(const vector<double>& x, int k){
    vector<int> idx(x.size()); iota(idx.begin(),idx.end(),0);
    if(k<=0) return {};
    if(k >= (int)idx.size()){
        sort(idx.begin(),idx.end(),[&](int a,int b){return x[a]>x[b];});
        return idx;
    }
    nth_element(idx.begin(), idx.begin()+k, idx.end(), [&](int a,int b){return x[a]>x[b];});
    idx.resize(k);
    sort(idx.begin(),idx.end(),[&](int a,int b){return x[a]>x[b];});
    return idx;
}
static set<int> as_set(const vector<int>& v){ return set<int>(v.begin(),v.end()); }
static long long ceil_log2_int(int n){ long long r=0; int x=max(1,n-1); while(x>0){r++; x>>=1;} return max(1LL,r); }

struct Pick{
    vector<int> picked;
    int passes=0;
    int candidate_count=0;
    int fallback=0;
    int certified=0;
    string fallback_reason="none";
    string certifier="none";
    long long score_reads=0;
    long long prev_reads=0;
    long long candidate_reads=0;
    long long comparisons_est=0;
    double threshold=0.0;
    double kth_score=0.0;
    double omitted_max=-1e300;
    double selector_cost=0.0;
    double verify_cost=0.0;
    double wall_proxy=0.0;
};

struct Row{
    string regime,method,fallback_reason,certifier;
    int seed,step,N,K,passes,candidate_count,exact,misses,pred_hits,fallback,certified;
    long long score_reads,prev_reads,candidate_reads,comparisons_est;
    double rho,prev_hit_ratio,threshold,kth_score,omitted_max,selector_cost,verify_cost,wall_proxy,regret,score;
};

vector<vector<double>> make_stream(const string& regime,int seed,int steps,int N){
    mt19937 rng(seed);
    normal_distribution<double> noise(0,1.0);
    vector<double> base(N); for(auto& v:base) v=noise(rng);
    vector<vector<double>> xs; xs.reserve(steps);
    set<int> hot; for(int i=0;i<32;i++) hot.insert((seed*17+i*97)%N);
    for(int t=0;t<steps;t++){
        vector<double> x(N);
        double rho = (regime=="stable_rope"?0.965:regime=="slow_drift"?0.895:regime=="bursty_spikes"?0.70:regime=="phase_shift"?0.62:0.80);
        for(int i=0;i<N;i++){
            double structural = 0.72*cos((i-(seed+t*3))*0.003) + 0.42*cos((i%257)*0.017 + t*0.03);
            double n=noise(rng)*0.40;
            if(t==0) x[i]=base[i]+structural+n;
            else x[i]=rho*xs.back()[i]+(1-rho)*(base[i]+structural+n);
        }
        if(regime=="stable_rope") for(int h:hot) x[h]+=3.25;
        if(regime=="slow_drift") for(int h:hot) x[(h+t*7)%N]+=3.05;
        if(regime=="bursty_spikes" && t%4==1) for(int j=0;j<24;j++) x[(seed*13+t*151+j*59)%N]+=4.35;
        if(regime=="phase_shift" && t>steps/2) for(int j=0;j<32;j++) x[(seed*19+j*83+N/2)%N]+=4.0;
        if(regime=="flat_ambiguous") for(int i=0;i<N;i++) x[i]=0.32*x[i]+noise(rng)*0.58;
        xs.push_back(move(x));
    }
    return xs;
}

static void finish_cost(Pick& p){
    p.wall_proxy = 0.085*p.passes + 0.000018*p.score_reads + 0.000042*p.candidate_reads
                 + 0.00000035*p.comparisons_est + 0.000010*p.candidate_count
                 + 0.08*p.fallback + p.selector_cost + p.verify_cost;
}

static Pick exact_heap(const vector<double>& x, int K){
    Pick p; p.certified=1; p.certifier="full_scan_heap_exact"; p.passes=1;
    p.score_reads=x.size(); p.candidate_count=K; p.candidate_reads=K;
    p.comparisons_est=(long long)x.size()*ceil_log2_int(K);
    p.picked=topk_indices(x,K); p.kth_score=x[p.picked.back()];
    p.selector_cost=0.24; finish_cost(p); return p;
}

static Pick exact_radix4(const vector<double>& x, int K){
    Pick p; p.certified=1; p.certifier="full_materialized_sort_exact"; p.passes=4;
    p.score_reads=(long long)x.size()*4; p.candidate_count=K; p.candidate_reads=x.size();
    p.comparisons_est=(long long)x.size()*ceil_log2_int((int)x.size());
    p.picked=topk_indices(x,K); p.kth_score=x[p.picked.back()];
    p.selector_cost=0.62; finish_cost(p); return p;
}

static Pick approx_prev_only(const vector<double>& x, const vector<int>& prev, int K){
    Pick p; p.certified=0; p.certifier="none_prev_indices_only"; p.passes=0;
    for(int id:prev){ if(id>=0 && id<(int)x.size() && (int)p.picked.size()<K) p.picked.push_back(id); }
    p.prev_reads=p.picked.size(); p.candidate_count=p.picked.size(); p.candidate_reads=p.picked.size();
    p.threshold=0.0; p.kth_score=p.picked.empty()?0.0:x[p.picked.back()]; p.selector_cost=0.025; finish_cost(p); return p;
}

static Pick certified_threshold_refine(const vector<double>& x, const vector<int>& prev, int K, double slack, int cap_mult, const string& label){
    Pick p; p.certifier="threshold_scan_kth_certifier"; const int N=x.size();
    if((int)prev.size()<K){
        p=exact_heap(x,K); p.fallback=1; p.fallback_reason="no_previous_exact_topk"; p.certifier=label+"_fallback_heap"; finish_cost(p); return p;
    }
    double prev_min=1e300, prev_mean=0.0;
    for(int id:prev){
        double v=x[id]; prev_min=min(prev_min,v); prev_mean+=v; p.prev_reads++;
    }
    prev_mean/=max(1,(int)prev.size());
    double spread=max(0.05, prev_mean-prev_min);
    p.threshold = prev_min - slack*(spread + 0.16);
    vector<int> candidates; candidates.reserve(min(N,cap_mult*K+64));
    p.omitted_max=-1e300; p.passes=1; p.score_reads=N;
    for(int i=0;i<N;i++){
        if(x[i] >= p.threshold) candidates.push_back(i);
        else if(x[i] > p.omitted_max) p.omitted_max=x[i];
    }
    p.candidate_count=candidates.size();
    if((int)candidates.size()<K){
        Pick fb=exact_heap(x,K); fb.fallback=1; fb.fallback_reason="threshold_too_high_candidate_underflow";
        fb.prev_reads=p.prev_reads; fb.score_reads += p.score_reads; fb.passes += p.passes;
        fb.candidate_count=p.candidate_count; fb.threshold=p.threshold; fb.omitted_max=p.omitted_max;
        fb.certifier=label+"_fallback_heap"; finish_cost(fb); return fb;
    }
    if((int)candidates.size()>cap_mult*K){
        Pick fb=exact_heap(x,K); fb.fallback=1; fb.fallback_reason="candidate_buffer_over_cap";
        fb.prev_reads=p.prev_reads; fb.score_reads += p.score_reads; fb.passes += p.passes;
        fb.candidate_count=p.candidate_count; fb.threshold=p.threshold; fb.omitted_max=p.omitted_max;
        fb.certifier=label+"_fallback_heap"; finish_cost(fb); return fb;
    }
    vector<double> sub; sub.reserve(candidates.size());
    for(int id:candidates){ sub.push_back(x[id]); p.candidate_reads++; }
    auto subidx=topk_indices(sub,K);
    for(int sid:subidx) p.picked.push_back(candidates[sid]);
    p.kth_score=x[p.picked.back()];
    p.comparisons_est=(long long)candidates.size()*ceil_log2_int(max(2,K));
    p.certified = (p.picked.size()==(size_t)K && p.kth_score >= p.omitted_max) ? 1 : 0;
    if(!p.certified){
        Pick fb=exact_heap(x,K); fb.fallback=1; fb.fallback_reason="certifier_failed_kth_below_omitted_max";
        fb.prev_reads=p.prev_reads; fb.score_reads += p.score_reads; fb.candidate_reads += p.candidate_reads;
        fb.passes += p.passes; fb.candidate_count=p.candidate_count; fb.threshold=p.threshold; fb.omitted_max=p.omitted_max;
        fb.certifier=label+"_fallback_heap"; finish_cost(fb); return fb;
    }
    p.fallback_reason="none"; p.selector_cost=0.10; p.verify_cost=0.00022*p.candidate_count; finish_cost(p); return p;
}

static Pick zscore_certified(const vector<double>& x, int K, double z, int cap_mult){
    Pick p; p.certifier="zscore_threshold_scan_kth_certifier"; const int N=x.size();
    double mean=0.0; for(double v:x){ mean+=v; p.score_reads++; } mean/=N;
    double var=0.0; for(double v:x){ double d=v-mean; var+=d*d; p.score_reads++; } var=sqrt(var/N);
    p.threshold=mean+z*var; p.passes=2;
    vector<int> candidates; p.omitted_max=-1e300; p.score_reads += N; p.passes++;
    for(int i=0;i<N;i++){
        if(x[i]>=p.threshold) candidates.push_back(i);
        else if(x[i]>p.omitted_max) p.omitted_max=x[i];
    }
    p.candidate_count=candidates.size();
    if((int)candidates.size()<K){
        Pick fb=exact_heap(x,K); fb.fallback=1; fb.fallback_reason="zscore_candidate_underflow";
        fb.score_reads+=p.score_reads; fb.passes+=p.passes; fb.candidate_count=p.candidate_count; fb.threshold=p.threshold; fb.omitted_max=p.omitted_max; fb.certifier="zscore_fallback_heap"; finish_cost(fb); return fb;
    }
    if((int)candidates.size()>cap_mult*K){
        Pick fb=exact_heap(x,K); fb.fallback=1; fb.fallback_reason="zscore_candidate_over_cap";
        fb.score_reads+=p.score_reads; fb.passes+=p.passes; fb.candidate_count=p.candidate_count; fb.threshold=p.threshold; fb.omitted_max=p.omitted_max; fb.certifier="zscore_fallback_heap"; finish_cost(fb); return fb;
    }
    vector<double> sub; for(int id:candidates){ sub.push_back(x[id]); p.candidate_reads++; }
    auto subidx=topk_indices(sub,K); for(int sid:subidx) p.picked.push_back(candidates[sid]);
    p.kth_score=x[p.picked.back()]; p.comparisons_est=(long long)candidates.size()*ceil_log2_int(max(2,K));
    p.certified=(p.kth_score>=p.omitted_max); p.selector_cost=0.18; p.verify_cost=0.0002*p.candidate_count; finish_cost(p); return p;
}

static Pick threshold_uncertified(const vector<double>& x, int K){
    Pick p; p.certifier="none_zscore_partial"; const int N=x.size();
    double mean=0.0; for(double v:x){mean+=v; p.score_reads++;} mean/=N;
    double var=0.0; for(double v:x){double d=v-mean; var+=d*d; p.score_reads++;} var=sqrt(var/N);
    p.threshold=mean+1.65*var; p.passes=2;
    vector<int> c; for(int i=0;i<N;i++){p.score_reads++; if(x[i]>=p.threshold)c.push_back(i);} p.passes++;
    p.candidate_count=c.size(); vector<double> sub; for(int id:c){sub.push_back(x[id]); p.candidate_reads++;}
    if((int)c.size()>=K){auto ids=topk_indices(sub,K); for(int sid:ids)p.picked.push_back(c[sid]);}
    else p.picked=c;
    p.kth_score=p.picked.empty()?0.0:x[p.picked.back()]; p.comparisons_est=(long long)c.size()*ceil_log2_int(max(2,K));
    p.selector_cost=0.12; finish_cost(p); return p;
}

static Pick select_method(const vector<double>& x, const vector<int>& prev, const string& method, int K){
    if(method=="exact_heap_baseline") return exact_heap(x,K);
    if(method=="radix_exact_baseline") return exact_radix4(x,K);
    if(method=="approx_prev_topk_only") return approx_prev_only(x,prev,K);
    if(method=="gvr_certified_cap6") return certified_threshold_refine(x,prev,K,0.34,6,"gvr_certified_cap6");
    if(method=="gvr_certified_cap12") return certified_threshold_refine(x,prev,K,0.58,12,"gvr_certified_cap12");
    if(method=="zscore_certified_cap8") return zscore_certified(x,K,1.72,8);
    if(method=="threshold_uncertified_no_fallback") return threshold_uncertified(x,K);
    return exact_heap(x,K);
}

static Row eval_row(const vector<double>& x, const vector<int>& prev, const set<int>& truth, const string& regime, const string& method, int seed, int step, int K, double rho){
    Pick p=select_method(x,prev,method,K);
    set<int> picked=as_set(p.picked);
    int hit=0; for(int id:truth) if(picked.count(id)) hit++;
    int misses=K-hit; int exact=(misses==0?1:0);
    int pred_hits=0; for(int id:prev) if(truth.count(id)) pred_hits++;
    double prev_hit_ratio=prev.empty()?0.0:(double)pred_hits/prev.size();
    double exactness=(double)hit/K;
    double score = 1.85*exactness - 0.58*p.wall_proxy - 0.95*(1.0-exactness) + 0.05*p.certified - 0.08*p.fallback;
    return {regime,method,p.fallback_reason,p.certifier,seed,step,(int)x.size(),K,p.passes,p.candidate_count,exact,misses,pred_hits,p.fallback,p.certified,p.score_reads,p.prev_reads,p.candidate_reads,p.comparisons_est,rho,prev_hit_ratio,p.threshold,p.kth_score,p.omitted_max,p.selector_cost,p.verify_cost,p.wall_proxy,0.0,score};
}

int main(int argc, char** argv){
    string out = argc>1 ? argv[1] : "artifacts/probe-results/REV0042_GVR_TOPK_TEMPORAL_DEORACLE_SMOKE.json";
    int N=2048,K=32,steps=20;
    vector<string> regimes={"stable_rope","slow_drift","bursty_spikes","phase_shift","flat_ambiguous"};
    vector<string> methods={"radix_exact_baseline","exact_heap_baseline","gvr_certified_cap6","gvr_certified_cap12","zscore_certified_cap8","threshold_uncertified_no_fallback","approx_prev_topk_only"};
    vector<Row> rows;
    for(const auto& reg:regimes){
        for(int seed: {13,29,47,61,83,101}){
            auto xs=make_stream(reg,seed,steps,N);
            vector<int> prev_exact;
            for(int t=0;t<steps;t++){
                vector<int> truth_vec=topk_indices(xs[t],K); set<int> truth=as_set(truth_vec);
                double rho=(reg=="stable_rope"?0.965:reg=="slow_drift"?0.895:reg=="bursty_spikes"?0.70:reg=="phase_shift"?0.62:0.80);
                vector<Row> tmp; for(const auto& m:methods) tmp.push_back(eval_row(xs[t],prev_exact,truth,reg,m,seed,t,K,rho));
                double best=-1e300; for(const auto& r:tmp) best=max(best,r.score);
                for(auto& r:tmp){ r.regret=best-r.score; rows.push_back(r); }
                prev_exact=truth_vec;
            }
        }
    }
    map<string,int> winner_counts, nonbaseline_winner_counts, exact_counts, fallback_counts, certified_counts;
    map<string,double> wall_sums, cand_sums; map<string,int> method_counts;
    for(size_t i=0;i<rows.size();){
        size_t j=i; while(j<rows.size() && rows[j].regime==rows[i].regime && rows[j].seed==rows[i].seed && rows[j].step==rows[i].step) j++;
        auto best=max_element(rows.begin()+i, rows.begin()+j, [](const Row&a,const Row&b){return a.score<b.score;});
        winner_counts[best->method]++;
        auto best2=max_element(rows.begin()+i, rows.begin()+j, [](const Row&a,const Row&b){
            bool abase=a.method.find("baseline")!=string::npos;
            bool bbase=b.method.find("baseline")!=string::npos;
            if(abase!=bbase) return abase;
            return a.score<b.score;
        });
        nonbaseline_winner_counts[best2->method]++;
        for(size_t k=i;k<j;k++){
            exact_counts[rows[k].method]+=rows[k].exact;
            fallback_counts[rows[k].method]+=rows[k].fallback;
            certified_counts[rows[k].method]+=rows[k].certified;
            wall_sums[rows[k].method]+=rows[k].wall_proxy;
            cand_sums[rows[k].method]+=rows[k].candidate_count;
            method_counts[rows[k].method]++;
        }
        i=j;
    }
    ofstream f(out); f<<fixed<<setprecision(6);
    f << "{\n  \"project\":\"CloudtainerML\",\n  \"revision\":\"rev0042\",\n  \"probe\":\"gvr_topk_temporal_deoracle\",\n  \"kind\":\"native_cxx_probe\",\n";
    f << "  \"source_ids\":[\"SRC-0362\"],\n  \"cell_ids\":[\"CELL-354\"],\n";
    f << "  \"repair_of\":\"rev0039_gvr_topk_temporal_oracle_truth_leak\",\n";
    f << "  \"run_provenance\":{\"source_path\":\"experiments/gvr_topk_temporal/gvr_topk_temporal.cpp\",\"source_sha256\":" << q(SOURCE_SHA256) << ",\"build_command\":" << q(BUILD_COMMAND) << ",\"selector_oracle_policy\":\"selection may use previous exact Top-K output and scanned current scores only; current truth Top-K is computed only for scoring rows\"},\n";
    f << "  \"summary\":{\n    \"primary_metric\":{\"name\":\"score\",\"direction\":\"higher_is_better\"},\n";
    f << "    \"winner_counts\":{"; bool first=true; for(auto& kv:winner_counts){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<kv.second;} f << "},\n";
    f << "    \"nonbaseline_winner_counts\":{"; first=true; for(auto& kv:nonbaseline_winner_counts){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<kv.second;} f << "},\n";
    f << "    \"exact_method_counts\":{"; first=true; for(auto& kv:exact_counts){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<kv.second;} f << "},\n";
    f << "    \"fallback_counts\":{"; first=true; for(auto& kv:fallback_counts){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<kv.second;} f << "},\n";
    f << "    \"certified_counts\":{"; first=true; for(auto& kv:certified_counts){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<kv.second;} f << "},\n";
    f << "    \"mean_wall_proxy\":{"; first=true; for(auto& kv:wall_sums){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<(kv.second/max(1,method_counts[kv.first]));} f << "},\n";
    f << "    \"mean_candidate_count\":{"; first=true; for(auto& kv:cand_sums){ if(!first)f<<","; first=false; f<<q(kv.first)<<":"<<(kv.second/max(1,method_counts[kv.first]));} f << "},\n";
    f << "    \"guard_fields\":[\"exact\",\"misses\",\"certified\",\"fallback\",\"fallback_reason\",\"score_reads\",\"prev_reads\",\"candidate_reads\",\"comparisons_est\",\"candidate_count\",\"passes\",\"prev_hit_ratio\",\"wall_proxy\",\"regret\"],\n";
    f << "    \"interpretation\":\"rev0042 replaces oracle membership fallback with a score-only kth-vs-omitted-max certifier. GVR can now be exact only when the scanned threshold candidate set certifies containment or pays an explicit heap fallback; savings are regime-dependent and no longer free.\"\n  },\n";
    f << "  \"rows\":[\n";
    for(size_t i=0;i<rows.size();++i){ const auto& r=rows[i];
        f << "    {\"regime\":"<<q(r.regime)<<",\"method\":"<<q(r.method)<<",\"seed\":"<<r.seed<<",\"step\":"<<r.step
          <<",\"N\":"<<r.N<<",\"K\":"<<r.K<<",\"rho\":"<<r.rho<<",\"passes\":"<<r.passes
          <<",\"candidate_count\":"<<r.candidate_count<<",\"exact\":"<<r.exact<<",\"misses\":"<<r.misses
          <<",\"pred_hits\":"<<r.pred_hits<<",\"prev_hit_ratio\":"<<r.prev_hit_ratio<<",\"fallback\":"<<r.fallback
          <<",\"fallback_reason\":"<<q(r.fallback_reason)<<",\"certified\":"<<r.certified<<",\"certifier\":"<<q(r.certifier)
          <<",\"score_reads\":"<<r.score_reads<<",\"prev_reads\":"<<r.prev_reads<<",\"candidate_reads\":"<<r.candidate_reads
          <<",\"comparisons_est\":"<<r.comparisons_est<<",\"threshold\":"<<r.threshold<<",\"kth_score\":"<<r.kth_score
          <<",\"omitted_max\":"<<r.omitted_max<<",\"selector_cost\":"<<r.selector_cost<<",\"verify_cost\":"<<r.verify_cost
          <<",\"wall_proxy\":"<<r.wall_proxy<<",\"regret\":"<<r.regret<<",\"score\":"<<r.score<<"}" << (i+1==rows.size()?"\n":" ,\n");
    }
    f << "  ]\n}\n";
    cerr << "wrote " << out << " rows=" << rows.size() << "\n";
    return 0;
}
