#include <bits/stdc++.h>
using namespace std;
struct Row{string regime, mech; int L,B,w,p,target,source,depth; double cost, score; bool direct, depth_reach;};
static string q(const string&s){string r="\""; for(char c:s){ if(c=='\"'||c=='\\') r+='\\'; r+=c;} return r+'\"';}

vector<vector<int>> edges(const string& mech,int L,int B,int w,int p){
    vector<vector<int>> e(L);
    for(int i=0;i<L;i++){
        auto add=[&](int j){ if(j>=0 && j<=i && j<L) e[i].push_back(j); };
        if(mech=="fixed_block"){
            for(int j=(i/B)*B;j<=i;j++) add(j);
        }else if(mech=="sliding_window"){
            for(int j=max(0,i-w);j<=i;j++) add(j);
        }else if(mech=="pi_periodic_skip"){
            for(int j=max(0,i-w);j<=i;j++) add(j);
            for(int j=i-p;j>=0;j-=p) add(j);
        }else if(mech=="boundary_bridge"){
            for(int j=(i/B)*B;j<=i;j++) add(j);
            if(i%B==0) add(i-1);
        }else if(mech=="source_extended_bridge"){
            for(int j=(i/B)*B;j<=i;j++) add(j);
            if(i%B<=1){ for(int j=max(0,(i/B)*B-2); j<(i/B)*B; ++j) add(j); }
        }else if(mech=="ring_plus_anchor"){
            for(int j=max(0,i-w);j<=i;j++) add(j);
            add(0); add(i/2);
        }else if(mech=="dense_causal"){
            for(int j=0;j<=i;j++) add(j);
        }
        sort(e[i].begin(), e[i].end()); e[i].erase(unique(e[i].begin(), e[i].end()), e[i].end());
    }
    return e;
}

int shortest_hops(const vector<vector<int>>&e,int t,int s,int maxd){
    if(t==s) return 0;
    set<int> frontier{t}, seen{t};
    for(int d=1; d<=maxd; ++d){
        set<int> nxt;
        for(int u: frontier) for(int v:e[u]){ if(v==s) return d; if(!seen.count(v)){seen.insert(v); nxt.insert(v);} }
        frontier.swap(nxt); if(frontier.empty()) break;
    }
    return 999;
}

double avg_cost(const vector<vector<int>>&e){ double c=0; for(auto&v:e)c+=v.size(); return c/e.size(); }

int main(){
    const string REV="rev0035";
    vector<string> mechs={"fixed_block","sliding_window","pi_periodic_skip","boundary_bridge","source_extended_bridge","ring_plus_anchor","dense_causal"};
    vector<Row> rows;
    for(int L: {32,64,128}) for(int B: {4,8,16}) for(int w: {2,4,8}) for(int p: {4,8,16}){
        if(B>=L||w>=L||p>=L) continue;
        vector<pair<string,pair<int,int>>> qs;
        for(int t=B;t<L;t+=B) qs.push_back({"boundary_prev",{t,t-1}});
        for(int t=L/2;t<L;t+=max(1,L/4)) qs.push_back({"old_anchor",{t,0}});
        for(int t=max(p+1,L/2);t<L;t+=max(1,L/4)) qs.push_back({"periodic_offphase",{t,max(0,t-p/2)}});
        for(auto&mech:mechs){ auto e=edges(mech,L,B,w,p); double c=avg_cost(e); double dense=(L+1)/2.0; for(auto &qr:qs){ int t=qr.second.first,s=qr.second.second; if(t>=L||s<0||s>t) continue; bool dir=binary_search(e[t].begin(),e[t].end(),s); int h=shortest_hops(e,t,s,3); bool depth=h<=3; double cost_frac=c/dense; double score=(depth?1.0:0.0)+0.35*(dir?1.0:0.0)-0.18*cost_frac-0.08*max(0,h-1); rows.push_back({qr.first,mech,L,B,w,p,t,s,h,cost_frac,score,dir,depth}); }}
    }
    map<string,int>wins; map<string,int>guardmiss;
    map<string, vector<Row>> groups;
    for(auto&r:rows){ string k=r.regime+"|"+to_string(r.L)+"|"+to_string(r.B)+"|"+to_string(r.w)+"|"+to_string(r.p)+"|"+to_string(r.target)+"|"+to_string(r.source); groups[k].push_back(r); }
    for(auto&kv:groups){ auto best=max_element(kv.second.begin(),kv.second.end(),[](const Row&a,const Row&b){return a.score<b.score;}); wins[best->mech]++; for(auto&r:kv.second) if(!r.depth_reach) guardmiss[r.mech]++; }
    string winner=max_element(wins.begin(),wins.end(),[](auto&a,auto&b){return a.second<b.second;})->first;
    ofstream f("artifacts/probe-results/REV0035_SPARSE_ATTENTION_PROGRAM_SCHEMA_SMOKE.json");
    f << "{\n  \"project\":\"CloudtainerML\",\n  \"revision\":\""<<REV<<"\",\n  \"probe\":\"sparse_attention_program_schema\",\n  \"kind\":\"native_cpp_probe\",\n  \"source_ids\":[\"SRC-0348\",\"SRC-0350\"],\n  \"cell_ids\":[\"CELL-337\"],\n  \"summary\":{\n";
    f << "    \"primary_metric\":{\"name\":\"score\",\"direction\":\"higher_is_better\"},\n";
    f << "    \"winner\":"<<q(winner)<<",\n    \"row_count\":"<<rows.size()<<",\n    \"screen_regret_fields\":[\"direct\",\"depth_reach\",\"cost_frac\",\"depth\",\"target_miss\"],\n    \"interpretation\":\"A common sparse-attention program vocabulary exposes phase-specific reachability and cost tradeoffs instead of treating every mask as a bespoke probe.\"\n  },\n";
    f << "  \"winner_counts\":{"; bool first=true; for(auto&kv:wins){ if(!first)f<<","; first=false; f<<"\n    "<<q(kv.first)<<":"<<kv.second;} f << "\n  },\n";
    f << "  \"guard_miss_counts\":{"; first=true; for(auto&kv:guardmiss){ if(!first)f<<","; first=false; f<<"\n    "<<q(kv.first)<<":"<<kv.second;} f << "\n  },\n";
    f << "  \"rows\":[\n";
    for(size_t i=0;i<rows.size();++i){ auto&r=rows[i]; f << "    {\"regime\":"<<q(r.regime)<<",\"mechanism\":"<<q(r.mech)<<",\"L\":"<<r.L<<",\"block\":"<<r.B<<",\"window\":"<<r.w<<",\"period\":"<<r.p<<",\"target\":"<<r.target<<",\"source\":"<<r.source<<",\"direct\":"<<(r.direct?"true":"false")<<",\"depth_reach\":"<<(r.depth_reach?"true":"false")<<",\"depth\":"<<r.depth<<",\"cost_frac\":"<<fixed<<setprecision(6)<<r.cost<<",\"target_miss\":"<<(r.depth_reach?0:1)<<",\"score\":"<<r.score<<"}"<<(i+1<rows.size()?",":"")<<"\n"; }
    f << "  ]\n}\n";
    cerr << "wrote sparse_attention_program_schema rows="<<rows.size()<<" winner="<<winner<<"\n";
    return 0;
}
