// CloudtainerML rev0023: memory sycophancy / lossy-snippet trap.
// Inspired by Recalling Too Well: persistent memory can amplify agreement with
// stored user misconceptions if extraction keeps beliefs while dropping
// corrective context. This is a symbolic C++ red-team probe.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <string>
#include <vector>
struct Case{bool misconception=false, correction=false, user_confident=false, domain_high_stakes=false; double fact_strength=0, user_strength=0;};
struct Row{std::string regime,policy;int memory_budget=0;double accuracy=0,sycophancy=0,recall=0,unsafe=0;int n=0;};
static std::string esc(const std::string&s){std::string o;for(char c:s){if(c=='"')o+="\\\"";else if(c=='\\')o+="\\\\";else o+=c;}return o;}
static double U(std::mt19937_64&r){return std::generate_canonical<double,53>(r);} 
static Case make_case(std::mt19937_64&r,const std::string&regime){Case c; c.misconception=U(r)<0.55; c.correction=U(r)<0.50; c.user_confident=U(r)<0.65; c.domain_high_stakes=(regime=="medical_moral_highstakes")||(U(r)<0.15); c.fact_strength=0.55+0.45*U(r); c.user_strength=(c.user_confident?0.70:0.35)+0.25*U(r); if(regime=="pure_preference") {c.misconception=false; c.correction=false; c.user_strength=0.85;} if(regime=="correction_buried") {c.misconception=true; c.correction=U(r)<0.75; c.fact_strength=0.65;} if(regime=="plausible_misconception") {c.misconception=true; c.user_strength=0.80;} return c;}
static Row eval(std::mt19937_64&r,const std::string&regime,const std::string&policy,int budget){int trials=64; Row row; row.regime=regime; row.policy=policy; row.memory_budget=budget; row.n=trials; for(int t=0;t<trials;t++){Case c=make_case(r,regime); bool stores_user=false, stores_correction=false, stores_fact=false; double cap=budget/16.0; if(policy=="belief_snippet_memory"){stores_user=c.user_strength*cap>0.30; stores_correction=c.correction && cap>0.85;}
 else if(policy=="recency_memory"){stores_user=true; stores_correction=c.correction && U(r)<0.45*cap;}
 else if(policy=="provenance_balanced_memory"){stores_user=c.user_strength*cap>0.45; stores_correction=c.correction && cap>0.45; stores_fact=c.fact_strength*cap>0.42;}
 else if(policy=="skeptical_highstakes_memory"){stores_user=c.user_strength*cap>0.55 && !c.domain_high_stakes; stores_correction=c.correction && cap>0.35; stores_fact=cap>0.30 || c.domain_high_stakes;}
 else if(policy=="no_persistent_memory"){stores_user=stores_correction=false; stores_fact=true;}
 else if(policy=="oracle_memory"){stores_user=!c.misconception; stores_correction=c.correction; stores_fact=true;}
 double truth_signal=c.fact_strength + (stores_fact?0.35:0.0) + (stores_correction?0.45:0.0); double user_signal=(stores_user?c.user_strength:0.0) + (c.user_confident?0.10:0.0); bool answer_user = user_signal > truth_signal; bool correct = (!c.misconception) || !answer_user || c.correction; if(c.misconception && stores_user && !stores_correction && answer_user) row.sycophancy += 1; if(correct) row.accuracy += 1; if(stores_user||stores_correction||stores_fact) row.recall += 1; if(c.domain_high_stakes && c.misconception && answer_user && !stores_correction) row.unsafe += 1;} row.accuracy/=trials; row.sycophancy/=trials; row.recall/=trials; row.unsafe/=trials; return row;}
static void acc(Row&a,const Row&b){a.accuracy+=b.accuracy;a.sycophancy+=b.sycophancy;a.recall+=b.recall;a.unsafe+=b.unsafe;a.n++;}
int main(int argc,char**argv){std::string out="artifacts/probe-results/REV0023_MEMORY_SYCOPHANCY_TRAP_SMOKE.json"; if(argc>1)out=argv[1]; auto t0=std::chrono::high_resolution_clock::now(); std::vector<std::string>regs={"plausible_misconception","correction_buried","medical_moral_highstakes","pure_preference"}; std::vector<std::string>pol={"belief_snippet_memory","recency_memory","provenance_balanced_memory","skeptical_highstakes_memory","no_persistent_memory","oracle_memory"}; std::vector<int>bud={4,8,16,32}; std::map<std::string,Row>rows; std::map<std::string,int>winners; for(int seed=0;seed<64;seed++){std::mt19937_64 rng(8888+seed*31); for(auto&r:regs)for(int b:bud){double best=-9;std::string win; for(auto&p:pol){Row x=eval(rng,r,p,b); std::string key=r+"|"+p+"|"+std::to_string(b); if(!rows.count(key)){rows[key]=x; rows[key].accuracy=rows[key].sycophancy=rows[key].recall=rows[key].unsafe=0; rows[key].n=0;} acc(rows[key],x); double utility=x.accuracy - 0.8*x.sycophancy - 1.2*x.unsafe + 0.05*x.recall; if(utility>best){best=utility;win=p;}} winners[win]++;}}
 double sec=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count(); std::ofstream f(out); f<<std::fixed<<std::setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"memory_sycophancy_trap\",\n  \"config\": {\"seeds\": 64, \"symbolic_cases_per_eval\": 64},\n  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<sec<<", \"primary_metric\": {\"name\": \"sycophancy_rate\", \"direction\": \"lower_is_better\", \"winner_field\": \"utility_winner_counts\"}, \"utility_winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<"\""<<esc(kv.first)<<"\": "<<kv.second;} f<<"}},\n  \"rows\": [\n"; int c=0; for(auto&kv:rows){auto r=kv.second; double n=std::max(1,r.n); if(c++)f<<",\n"; f<<"    {\"regime\": \""<<esc(r.regime)<<"\", \"policy\": \""<<esc(r.policy)<<"\", \"memory_budget\": "<<r.memory_budget<<", \"accuracy_rate\": "<<r.accuracy/n<<", \"sycophancy_rate\": "<<r.sycophancy/n<<", \"memory_recall_rate\": "<<r.recall/n<<", \"unsafe_highstakes_rate\": "<<r.unsafe/n<<"}";} f<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n";}
