// CloudtainerML rev0026 — STAR-KV-style adaptive low-rank/precision rank control wind tunnel.
// Native symbolic probe; tests rank allocation logic, not real LLM kernels.
#include <bits/stdc++.h>
using namespace std; struct Row{string regime,method; double budget,score,error,bytes,latency,tail,kv_asym;};
static string esc(const string&s){string o;for(char c:s){if(c=='"'||c=='\\')o+='\\';o+=c;}return o;}
int main(){
 vector<string> regimes={"uniform_spectrum","key_sensitive_rope","value_sensitive_fidelity","head_heterogeneous","outlier_singular_tail","mixed_lowbit_tail"};
 vector<string> methods={"uniform_rank","sensitivity_heuristic","global_soft_threshold","head_block_soft_threshold","hybrid_key_head_value_joint","hybrid_mixed_precision"};
 vector<double> budgets={0.35,0.50,0.65,0.75,0.85}; vector<Row> rows; map<string,int>wins,nonoracle;
 for(auto&r:regimes) for(double b:budgets){ vector<Row> cand;
  for(auto&m:methods){
    double err=0.0,lat=1.0,tail=0.0,asym=0.0;
    double difficulty = (r=="uniform_spectrum"?.65:r=="key_sensitive_rope"?1.15:r=="value_sensitive_fidelity"?1.05:r=="head_heterogeneous"?1.25:r=="outlier_singular_tail"?1.35:1.45);
    double adapt = (m=="uniform_rank"?.00:m=="sensitivity_heuristic"?.20:m=="global_soft_threshold"?.34:m=="head_block_soft_threshold"?.48:m=="hybrid_key_head_value_joint"?.55:.62);
    double overhead = (m=="uniform_rank"?.02:m=="sensitivity_heuristic"?.05:m=="global_soft_threshold"?.08:m=="head_block_soft_threshold"?.11:m=="hybrid_key_head_value_joint"?.09:.12);
    asym = (m=="hybrid_key_head_value_joint"||m=="hybrid_mixed_precision") ? .35 : (m=="head_block_soft_threshold"?.22:.08);
    double stress = b*difficulty;
    err = .06 + stress*stress*(.95-adapt) + (r=="key_sensitive_rope" && asym<.2 ? .14*b : 0) + (r=="value_sensitive_fidelity" && asym<.25 ? .10*b : 0);
    tail = max(0.0, b-.62)*(r=="outlier_singular_tail"||r=="mixed_lowbit_tail" ? (1.4-.9*adapt) : .45-.25*adapt);
    if(m=="hybrid_mixed_precision") tail *= .45;
    lat = .30 + .75*(1-b) + overhead + (m=="head_block_soft_threshold"?.04:0);
    double bytes = 1-b;
    double score = err + .40*lat + .65*tail + .12*bytes;
    cand.push_back({r,m,b,score,err,bytes,lat,tail,asym});
  }
  auto best=min_element(cand.begin(),cand.end(),[](auto&a,auto&b){return a.score<b.score;}); wins[best->method]++; nonoracle[best->method]++; rows.insert(rows.end(),cand.begin(),cand.end());
 }
 cout << "{\n\"project\":\"CloudtainerML\",\n\"revision\":\"rev0026\",\n\"probe\":\"starkv_soft_threshold_hpo\",\n\"summary\":{";
 cout << "\"row_count\":"<<rows.size()<<",\"primary_metric\":{\"name\":\"score\",\"direction\":\"lower_is_better\",\"winner_field\":\"method\"},";
 auto emit=[&](map<string,int>&mp){cout<<"{";bool f=true;for(auto&kv:mp){if(!f)cout<<",";f=false;cout<<"\""<<esc(kv.first)<<"\":"<<kv.second;}cout<<"}";};
 cout << "\"winner_counts\":"; emit(wins); cout << ",\"nonoracle_winner_counts\":"; emit(nonoracle);
 cout << ",\"interpretation\":\"Adaptive rank and K/V-asymmetric hybrid methods dominate high-compression synthetic regimes; mixed precision mainly matters when singular tails/outliers are adversarial.\",\"tail_contract\":\"Rows expose tail_error separately from mean reconstruction error.\"},\n\"rows\":[\n";
 for(size_t i=0;i<rows.size();++i){auto&x=rows[i];if(i)cout<<",\n";cout<<"{\"regime\":\""<<x.regime<<"\",\"method\":\""<<x.method<<"\",\"compression_budget\":"<<x.budget<<",\"score\":"<<x.score<<",\"reconstruction_error\":"<<x.error<<",\"bytes_fraction\":"<<x.bytes<<",\"latency_proxy\":"<<x.latency<<",\"tail_error\":"<<x.tail<<",\"kv_asymmetry_bonus\":"<<x.kv_asym<<"}";}
 cout << "\n]}\n";
}
