// CloudtainerML rev0023: topic-document vs temporal-graph memory probe.
// C++17 symbolic agent-memory simulator. Tests topic-doc consolidation, temporal
// confidence graphs, and flat memory under changing facts, corrections, and
// incomplete evidence. Synthetic only.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

struct Fact{int entity,topic,time; double confidence; bool correction; int value;};
struct Query{int entity,topic,time; int answer; bool needs_revision;};
struct Row{std::string scenario,method; int n=0; double accuracy=0, stale_error=0, evidence_count=0, harmful_overwrite=0, utility=0;};
static std::string esc(const std::string&s){std::string o; for(char c:s){ if(c=='"')o+="\\\""; else if(c=='\\')o+="\\\\"; else o+=c;} return o;}
struct World{std::vector<Fact> facts; std::vector<Query> queries;};
static World make_world(int seed,const std::string&scenario){ std::mt19937_64 rng(seed); std::uniform_real_distribution<double>U(0,1); World w; int E=24,T=6,steps=120; std::map<std::pair<int,int>,int> cur; for(int e=0;e<E;e++)for(int t=0;t<T;t++)cur[{e,t}]=0;
    double change= scenario=="stable_topics"?0.03: scenario=="rapid_revisions"?0.17: scenario=="conflicting_evidence"?0.11:0.08; double confnoise=scenario=="conflicting_evidence"?0.42:0.18;
    for(int time=0; time<steps; ++time){ int e=rng()%E, topic=rng()%T; bool corr=U(rng)<change; int old=cur[{e,topic}]; int val=corr?old+1:old; if(corr) cur[{e,topic}]=val; double conf=std::max(0.05,std::min(0.99,0.70 + (corr?0.18:0.0) + (U(rng)-0.5)*confnoise)); if(scenario=="low_confidence_corrections"&&corr) conf=0.35+0.25*U(rng); w.facts.push_back({e,topic,time,conf,corr,val}); if(time>20 && time%3==0){ int qe=rng()%E, qt=rng()%T; w.queries.push_back({qe,qt,time,cur[{qe,qt}],change>0.08}); }}
    return w; }
static int predict(const std::vector<Fact>&hist,const Query&q,const std::string&m,int&ev,bool&harmful){ std::vector<Fact> cand; for(auto&f:hist) if(f.time<=q.time && f.entity==q.entity && (m.find("topic")==std::string::npos || f.topic==q.topic)) cand.push_back(f); ev=(int)cand.size(); harmful=false; if(cand.empty()) return 0;
    if(m=="flat_recency") return std::max_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.time<b.time;})->value;
    if(m=="flat_confidence") return std::max_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.confidence<b.confidence;})->value;
    if(m=="topic_document"){ std::map<int,double> score; for(auto&f:cand) if(f.topic==q.topic) score[f.value]+=1.0+0.01*f.time+0.3*f.confidence; if(score.empty()) return cand.back().value; return std::max_element(score.begin(),score.end(),[](auto&a,auto&b){return a.second<b.second;})->first; }
    if(m=="temporal_graph"){ double best=-1e9; int ans=0; for(auto&f:cand) if(f.topic==q.topic){ double s=0.04*f.time + 1.7*f.confidence + (f.correction?0.45:0); if(s>best){best=s;ans=f.value;} } return ans; }
    if(m=="non_destructive_graph"){ std::map<int,double> score; for(auto&f:cand) if(f.topic==q.topic){ double decay=std::exp(-(q.time-f.time)/45.0); score[f.value]+=decay*(0.8+f.confidence)+(f.correction?0.30:0); } return std::max_element(score.begin(),score.end(),[](auto&a,auto&b){return a.second<b.second;})->first; }
    if(m=="oracle_latest_valid") return q.answer; return cand.back().value; }
int main(int argc,char**argv){ std::string out="artifacts/probe-results/REV0023_TOPIC_GRAPH_MEMORY_SMOKE.json"; if(argc>1) out=argv[1]; auto t0=std::chrono::high_resolution_clock::now(); std::vector<std::string>scs={"stable_topics","rapid_revisions","conflicting_evidence","low_confidence_corrections","cross_topic_noise"}; std::vector<std::string>methods={"flat_recency","flat_confidence","topic_document","temporal_graph","non_destructive_graph","oracle_latest_valid"}; std::map<std::string,Row>rows; std::map<std::string,int>wins,nonoracle;
    for(auto&sc:scs) for(int seed=0; seed<90; ++seed){ World w=make_world(42000+seed*31,sc); std::map<std::string,double> util; for(auto&m:methods){ int ok=0,stale=0,evsum=0,harm=0; for(auto&q:w.queries){ int ev=0; bool h=false; int p=predict(w.facts,q,m,ev,h); if(p==q.answer) ok++; else if(p<q.answer) stale++; if(h)harm++; evsum+=ev;} double n=std::max(1,(int)w.queries.size()); double acc=ok/n, st=stale/n, evc=evsum/n, hr=harm/n; double u=acc-0.8*st-0.015*std::sqrt(evc)-1.1*hr-(m=="oracle_latest_valid"?0.18:0.0); std::string key=sc+"|"+m; if(!rows.count(key)){rows[key].scenario=sc;rows[key].method=m;} rows[key].accuracy+=acc;rows[key].stale_error+=st;rows[key].evidence_count+=evc;rows[key].harmful_overwrite+=hr;rows[key].utility+=u;rows[key].n++; util[m]=u; } double b=-9,bn=-9; std::string wm,wn; for(auto&m:methods){ if(util[m]>b){b=util[m];wm=m;} if(m.find("oracle")==std::string::npos && util[m]>bn){bn=util[m];wn=m;} } wins[wm]++; nonoracle[wn]++; }
    double sec=std::chrono::duration<double>(std::chrono::high_resolution_clock::now()-t0).count(); std::ofstream o(out); o<<std::fixed<<std::setprecision(6); o<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0023\",\n  \"probe\": \"topic_graph_memory\",\n  \"language\": \"c++17\",\n  \"is_paper_reproduction\": false,\n  \"taxonomy\": [\"persistent-memory\", \"agent-memory\", \"provenance\", \"graph-memory\"],\n";
    o<<"  \"summary\": {\"row_count\": "<<rows.size()<<", \"seconds\": "<<sec<<", \"primary_metric\": {\"name\": \"mean_utility\", \"direction\": \"higher_is_better\", \"winner_field\": \"winner_counts_excluding_oracle\"}, \"winner_counts\": {"; bool first=true; for(auto&kv:wins){if(!first)o<<", "; first=false; o<<"\""<<esc(kv.first)<<"\": "<<kv.second;} o<<"}, \"winner_counts_excluding_oracle\": {"; first=true; for(auto&kv:nonoracle){if(!first)o<<", "; first=false; o<<"\""<<esc(kv.first)<<"\": "<<kv.second;} o<<"}, \"interpretation\": \"Topic documents and non-destructive graph memory are tested against flat recency under fact revision and conflicting evidence.\"},\n  \"rows\": [\n";
    int c=0; for(auto&kv:rows){ const Row&r=kv.second; double n=std::max(1,r.n); if(c++)o<<",\n"; o<<"    {\"scenario\": \""<<esc(r.scenario)<<"\", \"method\": \""<<esc(r.method)<<"\", \"mean_accuracy\": "<<r.accuracy/n<<", \"mean_stale_error\": "<<r.stale_error/n<<", \"mean_evidence_count\": "<<r.evidence_count/n<<", \"mean_harmful_overwrite\": "<<r.harmful_overwrite/n<<", \"mean_utility\": "<<r.utility/n<<"}"; }
    o<<"\n  ]\n}\n"; std::cerr<<"wrote "<<out<<" rows="<<rows.size()<<"\n"; return 0; }
