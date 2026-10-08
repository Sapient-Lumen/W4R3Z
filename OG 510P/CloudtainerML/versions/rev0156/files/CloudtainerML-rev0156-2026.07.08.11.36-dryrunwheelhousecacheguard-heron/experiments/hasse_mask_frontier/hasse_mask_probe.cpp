// CloudtainerML rev0023: Hasse/partial-order attention mask frontier probe.
// Dependency-free C++17 graph toy. Tests whether a minimal common-supergraph
// view of task masks exposes leakage, redundancy, and insufficient reachability.
// Synthetic only; not a proof or reproduction.

#include <algorithm>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <string>
#include <vector>

struct Row{std::string family,method; int n=0, edges=0; double coverage=0, leakage=0, redundancy=0, train_infer_gap=0, utility=0;};
static std::string esc(const std::string&s){std::string o; for(char c:s){ if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
struct Task{int n; std::set<std::pair<int,int>> req, forbid;};
static void add_edge(std::set<std::pair<int,int>>&E,int a,int b){ if(a!=b) E.insert({a,b}); }
static Task make_task(const std::string&fam,int n){ Task t; t.n=n; if(fam=="causal_lm"){ for(int i=0;i<n;i++) for(int j=0;j<i;j++) add_edge(t.req,j,i); for(int i=0;i<n;i++) for(int j=i+1;j<n;j++) add_edge(t.forbid,j,i); }
    else if(fam=="block_generation"){ int B=8; for(int i=0;i<n;i++) for(int j=std::max(0,(i/B)*B-8);j<=i;j++) add_edge(t.req,j,i); for(int i=0;i<n;i++) for(int j=i+1;j<std::min(n,(i/B)*B+B);j++) add_edge(t.forbid,j,i); }
    else if(fam=="butterfly_bidirectional"){ for(int i=0;i<n;i++) for(int step=1; step<n; step*=2){ if(i-step>=0) add_edge(t.req,i-step,i); if(i+step<n) add_edge(t.req,i+step,i);} }
    else if(fam=="prefix_verify"){ int p=n/3; for(int i=p;i<n;i++) for(int j=0;j<p;j++) add_edge(t.req,j,i); for(int i=0;i<p;i++) for(int j=p;j<n;j++) add_edge(t.forbid,j,i); }
    else { for(int i=0;i<n;i++) for(int j=0;j<n;j++) if(j!=i) add_edge(t.req,j,i); }
    return t; }
static std::set<std::pair<int,int>> mask(const std::string&m,const Task&t){ std::set<std::pair<int,int>>E; int n=t.n; if(m=="full_bidirectional"){ for(int i=0;i<n;i++) for(int j=0;j<n;j++) if(i!=j) add_edge(E,j,i); }
    else if(m=="causal"){ for(int i=0;i<n;i++) for(int j=0;j<i;j++) add_edge(E,j,i); }
    else if(m=="local_window"){ for(int i=0;i<n;i++) for(int j=std::max(0,i-12);j<i;j++) add_edge(E,j,i); }
    else if(m=="task_exact_hasse"){ E=t.req; }
    else if(m=="minimal_common_supergraph"){ E=t.req; int n=t.n; for(int i=0;i<n;i+=8) for(int j=0;j<i;j+=8) add_edge(E,j,i); }
    else if(m=="block_two_stream_toy"){ for(int i=0;i<n;i++) for(int j=std::max(0,(i/8)*8-8);j<=i;j++) add_edge(E,j,i); }
    else if(m=="butterfly_toy"){ for(int i=0;i<n;i++) for(int step=1; step<n; step*=2){ if(i-step>=0)add_edge(E,i-step,i); if(i+step<n)add_edge(E,i+step,i);} }
    return E; }
static std::set<std::pair<int,int>> transitive_closure(std::set<std::pair<int,int>>E,int n){ bool changed=true; while(changed){ changed=false; std::vector<std::pair<int,int>> v(E.begin(),E.end()); for(auto ab:v) for(auto cd:v) if(ab.second==cd.first && ab.first!=cd.second && !E.count({ab.first,cd.second})){ E.insert({ab.first,cd.second}); changed=true; } } return E; }
static void eval(const std::string&fam,const std::string&m,Row&r){ Task t=make_task(fam,48); auto E=mask(m,t); auto C=transitive_closure(E,t.n); int have=0; for(auto&e:t.req) if(C.count(e)) have++; int leak=0; for(auto&e:t.forbid) if(C.count(e)) leak++; double cov=t.req.empty()?1.0:(double)have/t.req.size(); double leakage=t.forbid.empty()?0.0:(double)leak/std::max(1,(int)t.forbid.size()); double red=(double)std::max(0,(int)E.size()-(int)t.req.size())/std::max(1,(int)t.req.size()); double gap=(m=="causal"&&fam=="block_generation")?0.25: (m=="full_bidirectional"&&fam!="butterfly_bidirectional"?0.18:0.02*red); double util=cov - 2.2*leakage - 0.10*red - 0.55*gap; r.coverage+=cov; r.leakage+=leakage; r.redundancy+=red; r.train_infer_gap+=gap; r.utility+=util; r.edges+=E.size(); r.n++; }
int main(int argc,char**argv){ std::string out="artifacts/probe-results/REV0023_HASSE_MASK_FRONTIER_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now();
    std::vector<std::string> fam={"causal_lm","block_generation","butterfly_bidirectional","prefix_verify"}; std::vector<std::string> methods={"full_bidirectional","causal","local_window","task_exact_hasse","minimal_common_supergraph","block_two_stream_toy","butterfly_toy"}; std::map<std::string,Row>rows; std::map<std::string,int>wins,nonoracle;
    for(auto&f:fam){ double b=-9,bn=-9; std::string wm,wn; for(auto&m:methods){ std::string key=f+"|"+m; rows[key].family=f; rows[key].method=m; eval(f,m,rows[key]); double u=rows[key].utility; if(u>b){b=u;wm=m;} if(m!="task_exact_hasse" && u>bn){bn=u;wn=m;} } wins[wm]++; nonoracle[wn]++; }
    double sec=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count(); std::ofstream o(out); o<<std::fixed<<std::setprecision(6);
    o<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"hasse_mask_frontier\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n  \"taxonomy\": [\"attention-mask\", \"partial-order\", \"training-inference-consistency\"],\n";
    o<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<sec<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts_excluding_oracle\"}, \"winner_counts\": {"; bool first=true; for(auto&kv:wins){ if(!first)o<<", "; first=false; o<<"\""<<esc(kv.first)<<"\": "<<kv.second;} o<<"}, \"winner_counts_excluding_oracle\": {"; first=true; for(auto&kv:nonoracle){ if(!first)o<<", "; first=false; o<<"\""<<esc(kv.first)<<"\": "<<kv.second;} o<<"}, \"interpretation\": \"Treats mask choice as reachability plus leakage/redundancy instead of just compute cost.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){ const Row&r=kv.second; double n=std::max(1,r.n); if(c++)o<<",\n"; o<<"    {\"family\": \""<<esc(r.family)<<"\", \"method\": \""<<esc(r.method)<<"\", \"mean_edges\": "<<r.edges/n<<", \"mean_coverage\": "<<r.coverage/n<<", \"mean_leakage\": "<<r.leakage/n<<", \"mean_redundancy\": "<<r.redundancy/n<<", \"mean_train_infer_gap\": "<<r.train_infer_gap/n<<", \"mean_utility\": "<<r.utility/n<<"}"; }
    o<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
