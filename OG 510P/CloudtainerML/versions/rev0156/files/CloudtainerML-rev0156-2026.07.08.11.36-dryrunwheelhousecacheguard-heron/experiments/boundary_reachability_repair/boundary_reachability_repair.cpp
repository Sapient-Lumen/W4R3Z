// CloudtainerML rev0034 — Boundary reachability repair wind tunnel.
// Inspired by "Locality Does Not Imply Reachability: Boundary Repair in Block-Sparse Causal Attention".
// Synthetic graph/coverage screen; not a reproduction.
#include <bits/stdc++.h>
using namespace std;
static string q(const string&s){string o="\""; for(char c:s){if(c=='\"'||c=='\\')o+='\\'; if(c=='\n')o+="\\n"; else o+=c;} return o+'\"';}
struct Case{string regime; int L,B,depth,source,target,offset,distance; double cost_pressure;};
struct Row{string regime,method; int L,B,depth,source,target,offset,distance; double reachable,coverage,cost,phase_risk,boundary_cliff,regret,score;};
static bool in(int x,int lo,int hi){return x>=lo && x<=hi;}
static double C(double x){return max(0.0,min(1.0,x));}
static bool block_reach(int s,int t,int B){return s<=t && s/B==t/B;}
static bool slide_reach(int s,int t,int W,int depth){return s<=t && t-s<=W*depth;}
static bool bridge_center(int s,int t,int B,int half){
    if(s>t) return false; if(block_reach(s,t,B)) return true;
    int b=(t/B)*B; if(b==0) return false;
    return in(s,b-half,b+half-1) && in(t,b-half,b+half-1);
}
static bool pbb(int s,int t,int B,int half){
    if(s>t) return false; if(block_reach(s,t,B)) return true;
    int b=(t/B)*B; if(b==0) return false;
    return in(s,b-half,b+half-1) && in(t,b,b+half-1);
}
static bool sebridge(int s,int t,int B,int tail){
    if(s>t) return false; if(block_reach(s,t,B)) return true;
    int b=(t/B)*B; if(b==0) return false;
    return in(s,b-B,b+tail-1) && in(t,b,b+tail-1);
}
static Row eval(const Case&c,const string&m){
    double reach=0,cost=0,coverage=0,phase=0,cliff=0; int W=c.B/2; int half=c.B/4; int tail=c.B/2;
    if(m=="fixed_block") {reach=block_reach(c.source,c.target,c.B); cost=0.25; coverage= c.B/(double)c.L; phase=(c.offset>=0 && c.offset<4)?0.80:0.20;}
    else if(m=="sliding_window") {reach=slide_reach(c.source,c.target,W,c.depth); cost=0.50; coverage=min(1.0,(W*c.depth)/(double)c.L); phase=0.10;}
    else if(m=="centered_bridge") {reach=bridge_center(c.source,c.target,c.B,half); cost=0.34; coverage=(c.B+2*half)/(double)c.L; phase=(c.offset>=0 && c.offset<half)?0.18:0.38;}
    else if(m=="post_boundary_bridge") {reach=pbb(c.source,c.target,c.B,half); cost=0.31; coverage=(c.B+half)/(double)c.L; phase=(c.offset>=0 && c.offset<half)?0.10:0.42;}
    else if(m=="source_extended_bridge") {reach=sebridge(c.source,c.target,c.B,tail); cost=0.42; coverage=(c.B+tail)/(double)c.L; phase=(c.offset>=0 && c.offset<tail)?0.08:0.32;}
    else if(m=="block_plus_periodic_full") {reach=(block_reach(c.source,c.target,c.B)||c.depth>=4); cost=0.68; coverage=(c.depth>=4?1.0:c.B/(double)c.L); phase=0.12;}
    else if(m=="dense_full_oracle") {reach=1.0; cost=1.0; coverage=1.0; phase=0.0;}
    cliff=(reach<0.5 && c.distance<=4 && c.offset>=0 && c.offset<=4)?1.0:0.0;
    double miss=1.0-reach;
    double score=miss + 0.24*cost*c.cost_pressure + 0.18*phase + 0.30*cliff;
    return {c.regime,m,c.L,c.B,c.depth,c.source,c.target,c.offset,c.distance,reach,coverage,cost,phase,cliff,0,score};
}
int main(int argc,char**argv){string out=argc>1?argv[1]:"REV0034_BOUNDARY_REACHABILITY_REPAIR_SMOKE.json"; vector<Case> cases; vector<int> Bs={16,32}; vector<int> depths={1,2,4}; int L=128;
    for(int B:Bs){ for(int d:depths){ for(int off=-4; off<=12; off+=2){ int boundary=2*B; int t=boundary+off; if(t<1||t>=L) continue; for(int dist: {1,2,4,8,12,16,24,32}){ int s=t-dist; if(s<0) continue; string regime="uniform_local"; double cp=0.8; if(off>=0 && off<=4 && dist<=8) {regime="boundary_adjacent_copy"; cp=0.9;} else if(dist>=B/2) {regime="long_local_history"; cp=0.7;} else if(off<0 && dist<=4) {regime="preboundary_easy"; cp=1.1;} cases.push_back({regime,L,B,d,s,t,off,dist,cp}); } } } }
    vector<string> methods={"fixed_block","sliding_window","centered_bridge","post_boundary_bridge","source_extended_bridge","block_plus_periodic_full","dense_full_oracle"}; vector<Row> rows; map<string,int>winners,nonoracle; map<string,int> exact_misses;
    for(auto&c:cases){ vector<Row> cand; for(auto&m:methods)cand.push_back(eval(c,m)); double best=1e9; for(auto&x:cand) best=min(best,x.score); for(auto&x:cand) x.regret=max(0.0,x.score-best); auto b=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); winners[b->method]++; auto no=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){ if(a.method=="dense_full_oracle") return false; if(b.method=="dense_full_oracle") return true; return a.score<b.score;}); nonoracle[no->method]++; for(auto&x:cand){ if(x.reachable<0.5) exact_misses[x.method]++; } rows.insert(rows.end(),cand.begin(),cand.end()); }
    ofstream f(out); f<<fixed<<setprecision(6); f<<"{\n  \"project\": \"CloudtainerML\",\n  \"revision\": \"rev0034\",\n  \"probe\": \"boundary_reachability_repair\",\n  \"summary\": {\n    \"row_count\": "<<rows.size()<<",\n    \"case_count\": "<<cases.size()<<",\n    \"primary_metric\": {\"name\": \"score\", \"direction\": \"lower_is_better\", \"winner_field\": \"method\"},\n    \"winner_counts\": {"; bool first=true; for(auto&kv:winners){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"nonoracle_winner_counts\": {"; first=true; for(auto&kv:nonoracle){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"exact_miss_counts\": {"; first=true; for(auto&kv:exact_misses){if(!first)f<<", "; first=false; f<<q(kv.first)<<": "<<kv.second;} f<<"},\n    \"interpretation\": \"Local distance is not enough: fixed block masks create phase-specific reachability cliffs. Boundary repair is useful only where source/write-back coverage aligns with the missing causal edge; sliding windows remain strong broad local baselines.\",\n    \"screen_regret_fields\": [\"reachable\", \"boundary_cliff\", \"phase_risk\", \"cost\", \"regret\", \"score\"]\n  },\n  \"rows\": [\n"; for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\": "<<q(r.regime)<<", \"method\": "<<q(r.method)<<", \"L\": "<<r.L<<", \"B\": "<<r.B<<", \"depth\": "<<r.depth<<", \"source\": "<<r.source<<", \"target\": "<<r.target<<", \"offset\": "<<r.offset<<", \"distance\": "<<r.distance<<", \"reachable\": "<<r.reachable<<", \"coverage\": "<<r.coverage<<", \"cost\": "<<r.cost<<", \"phase_risk\": "<<r.phase_risk<<", \"boundary_cliff\": "<<r.boundary_cliff<<", \"regret\": "<<r.regret<<", \"score\": "<<r.score<<"}"<<(i+1==rows.size()?"\n":",\n");} f<<"  ]\n}\n";
}
