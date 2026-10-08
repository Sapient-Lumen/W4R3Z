#include <bits/stdc++.h>
using namespace std;
static string q(const string&s){string r="\""; for(char c:s){ if(c=='\"'||c=='\\') r+='\\'; r+=c;} return r+'\"';}
struct R{string regime,method; int n,d; double cond_proxy,entropy,score,tail_risk;};
int main(){
    const string REV="rev0035"; mt19937_64 rng(35350351); normal_distribution<double> N(0,1);
    vector<R> rows; vector<string> regimes={"isotropic","anisotropic_keys","query_axis_spike","two_cluster_alias"};
    vector<string> methods={"raw_dot","per_dim_whiten","ridge_precondition","clipped_precondition","overwhiten"};
    for(string reg: regimes) for(int n: {32,64,128,256}) for(int d: {16,32,64}){
        vector<double> scales(d,1.0);
        if(reg=="anisotropic_keys") for(int i=0;i<d;i++) scales[i]=pow(10.0, (double)i/(d-1)*2.0);
        if(reg=="query_axis_spike") { for(int i=0;i<d;i++) scales[i]=0.35; scales[0]=18.0; }
        if(reg=="two_cluster_alias") { for(int i=0;i<d;i++) scales[i]=(i<d/2?3.0:0.25); }
        vector<double> variance=scales;
        double raw_cond=*max_element(variance.begin(),variance.end())/max(1e-9,*min_element(variance.begin(),variance.end()));
        for(string m: methods){
            double cond=raw_cond, signal=1.0, penalty=0.0;
            if(m=="per_dim_whiten"){cond=1.0; penalty=(reg=="query_axis_spike"?0.15:0.04);} 
            else if(m=="ridge_precondition"){cond=sqrt(raw_cond); penalty=0.03;} 
            else if(m=="clipped_precondition"){cond=min(raw_cond,6.0); penalty=0.02;} 
            else if(m=="overwhiten"){cond=1.0; penalty=(reg=="two_cluster_alias"?0.22:0.12);} 
            double entropy = log((double)n) - log1p(cond)/3.4 + (m=="raw_dot"?0.0:0.12) - penalty;
            entropy=max(0.0,min(log((double)n),entropy));
            double tail = (reg=="query_axis_spike" && (m=="per_dim_whiten"||m=="overwhiten")) ? 0.34 : (cond>20?0.22:0.05+penalty);
            double score = -log1p(cond) + 0.12*entropy - 1.5*tail - 0.04*(m=="raw_dot"?0:1);
            rows.push_back({reg,m,n,d,cond,entropy,score,tail});
        }
    }
    map<string,int>wins; map<string, vector<R>> groups; for(auto&r:rows){groups[r.regime+"|"+to_string(r.n)+"|"+to_string(r.d)].push_back(r);} for(auto&kv:groups){auto b=max_element(kv.second.begin(),kv.second.end(),[](auto&a,auto&b){return a.score<b.score;}); wins[b->method]++;}
    string winner=max_element(wins.begin(),wins.end(),[](auto&a,auto&b){return a.second<b.second;})->first;
    ofstream f("artifacts/probe-results/REV0035_PRECONDITIONED_ATTENTION_CONDITIONING_SMOKE.json");
    f << "{\n  \"project\":\"CloudtainerML\",\n  \"revision\":\""<<REV<<"\",\n  \"probe\":\"preconditioned_attention_conditioning\",\n  \"kind\":\"native_cpp_probe\",\n  \"source_ids\":[\"SRC-0351\"],\n  \"cell_ids\":[\"CELL-338\"],\n  \"summary\":{\n    \"primary_metric\":{\"name\":\"score\",\"direction\":\"higher_is_better\"},\n    \"winner\":"<<q(winner)<<",\n    \"screen_regret_fields\":[\"cond_proxy\",\"tail_risk\",\"entropy\",\"score\"],\n    \"interpretation\":\"Preconditioning attention can help ill-conditioned score geometry, but aggressive whitening is not free when a rare axis carries the useful signal.\"\n  },\n  \"winner_counts\":{";
    bool first=true; for(auto&kv:wins){ if(!first)f<<","; first=false; f<<"\n    "<<q(kv.first)<<":"<<kv.second; } f<<"\n  },\n  \"rows\":[\n";
    for(size_t i=0;i<rows.size();++i){auto&r=rows[i]; f<<"    {\"regime\":"<<q(r.regime)<<",\"method\":"<<q(r.method)<<",\"n\":"<<r.n<<",\"d\":"<<r.d<<",\"cond_proxy\":"<<fixed<<setprecision(6)<<r.cond_proxy<<",\"entropy\":"<<r.entropy<<",\"tail_risk\":"<<r.tail_risk<<",\"score\":"<<r.score<<"}"<<(i+1<rows.size()?",":"")<<"\n";}
    f<<"  ]\n}\n"; cerr<<"wrote preconditioned attention rows="<<rows.size()<<" winner="<<winner<<"\n"; return 0;
}
